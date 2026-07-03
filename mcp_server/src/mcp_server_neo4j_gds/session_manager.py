import logging
import os
import threading
from contextlib import suppress
from datetime import timedelta
from typing import Dict, List, Optional, Tuple
from graphdatascience import GraphDataScience
from graphdatascience.session import GdsSessions, AuraAPICredentials, SessionMemory
from graphdatascience.session.dbms_connection_info import DbmsConnectionInfo

logger = logging.getLogger("mcp_server_neo4j_gds")
SESSION_NAME_PREFIX = "mcp_"


def ensure_mcp_session_name(session_name: str) -> str:
    if not session_name:
        raise ValueError("sessionName must be a non-empty string")
    if session_name.startswith(SESSION_NAME_PREFIX):
        return session_name
    return f"{SESSION_NAME_PREFIX}{session_name}"


class GdsMode:
    PLUGIN = "plugin"
    SESSION = "session"


class SessionManager:
    def __init__(self):
        self.mode: Optional[str] = None
        self._sessions: Dict[str, GraphDataScience] = {}
        self.graph_sessions: Dict[str, str] = {}
        self._lock = threading.Lock()
        self._sessions_client: Optional[GdsSessions] = None

    def detect_mode(self, gds: GraphDataScience) -> str:
        if self.mode is not None:
            return self.mode

        try:
            gds.run_cypher("CALL gds.session.list() YIELD name RETURN name LIMIT 1")
            self.mode = GdsMode.SESSION
            logger.info("Detected GDS Aura Graph Analytics (sessions) mode")
        except Exception as e:
            logger.info(f"Detected GDS Plugin (on-prem) mode ({e})")
            self.mode = GdsMode.PLUGIN

        return self.mode

    def _ensure_sessions_client(self):
        if self._sessions_client is not None:
            return
        client_id = os.getenv("AURA_API_CLIENT_ID")
        client_secret = os.getenv("AURA_API_CLIENT_SECRET")
        project_id = os.getenv("AURA_API_PROJECT_ID")

        if not all([client_id, client_secret]):
            raise ValueError(
                "Missing Aura API credentials. Set AURA_API_CLIENT_ID and AURA_API_CLIENT_SECRET"
            )

        self._sessions_client = GdsSessions(
            api_credentials=AuraAPICredentials(client_id, client_secret, project_id)
        )
        logger.info("Aura API credentials initialized")

    def _cached_session_exists(self, session_name: str) -> bool:
        self._ensure_sessions_client()
        try:
            inactive_statuses = {"deleted", "deleting", "failed", "terminated"}
            for session in self._sessions_client.list():
                if session.name != session_name:
                    continue
                return str(session.status).lower() not in inactive_statuses
            return False
        except Exception as e:
            logger.warning(f"Failed to validate cached session '{session_name}': {e}")
            return True

    def _evict(self, session_name: str):
        cached = self._sessions.pop(session_name, None)
        if cached is not None:
            with suppress(Exception):
                cached.close()
        self.graph_sessions = {
            graph: session
            for graph, session in self.graph_sessions.items()
            if session != session_name
        }

    def create_or_get_session(
        self,
        db_url: str,
        auth: Tuple[str, str],
        database: Optional[str] = None,
        *,
        session_name: str,
        memory_gb: Optional[int] = None,
    ) -> GraphDataScience:
        resolved_name = ensure_mcp_session_name(session_name)

        with self._lock:
            cached = self._sessions.get(resolved_name)
        if cached is not None:
            if self._cached_session_exists(resolved_name):
                return cached
            logger.info(f"Cached session '{resolved_name}' is no longer available")
            with self._lock:
                self._evict(resolved_name)

        self._ensure_sessions_client()

        if memory_gb is None:
            memory_gb = int(os.getenv("SESSION_MEMORY_GB", "8"))
        memory = getattr(SessionMemory, f"m_{memory_gb}GB")
        ttl_hours = int(os.getenv("SESSION_TTL_HOURS", "24"))

        logger.info(
            f"Creating or getting session '{resolved_name}' with {memory_gb}GB memory and {ttl_hours}h TTL"
        )

        db_connection = DbmsConnectionInfo(
            uri=db_url, username=auth[0], password=auth[1], database=database
        )

        session_gds = self._sessions_client.get_or_create(
            session_name=resolved_name,
            memory=memory,
            ttl=timedelta(hours=ttl_hours),
            db_connection=db_connection,
        )
        with self._lock:
            # Another thread may have created this session concurrently
            existing = self._sessions.get(resolved_name)
            if existing is not None:
                with suppress(Exception):
                    session_gds.close()
                return existing
            self._sessions[resolved_name] = session_gds
        logger.info(f"Session '{resolved_name}' created/retrieved successfully")
        return session_gds

    def get_session(self, session_name: str) -> Optional[GraphDataScience]:
        resolved_name = ensure_mcp_session_name(session_name)
        with self._lock:
            cached = self._sessions.get(resolved_name)
        if cached is None:
            return None
        if self._cached_session_exists(resolved_name):
            return cached
        with self._lock:
            self._evict(resolved_name)
        return None

    def active_sessions(self) -> List[Tuple[str, GraphDataScience]]:
        with self._lock:
            return list(self._sessions.items())

    def assert_graph_unmapped(self, graph_name: str, target_session: str):
        with self._lock:
            mapped = self.graph_sessions.get(graph_name)
            if mapped and mapped != target_session and mapped in self._sessions:
                raise ValueError(
                    f"Graph '{graph_name}' already exists in session '{mapped}'. "
                    f"Drop it first or choose a different graph name."
                )

    def record_graph(self, graph_name: str, session_name: str):
        with self._lock:
            self.graph_sessions[graph_name] = session_name

    def forget_graph(self, graph_name: str):
        with self._lock:
            self.graph_sessions.pop(graph_name, None)

    def session_for_graph(self, graph_name: str) -> Optional[str]:
        with self._lock:
            mapped = self.graph_sessions.get(graph_name)
            if mapped and mapped in self._sessions:
                return mapped
            sessions = dict(self._sessions)
        # Unmapped graph (e.g. after a restart): look for it in the active sessions
        for name, gds in sessions.items():
            try:
                if bool(gds.graph.exists(graph_name)["exists"]):
                    self.record_graph(graph_name, name)
                    return name
            except Exception as e:
                logger.warning(
                    f"Failed to check graph '{graph_name}' in session '{name}': {e}"
                )
        return None

    def list_sessions(self):
        self._ensure_sessions_client()

        sessions = []
        for s in self._sessions_client.list():
            sessions.append(
                {
                    "name": s.name,
                    "status": s.status,
                    "memory": str(s.memory),
                    "created_at": str(s.created_at),
                    "expiry_date": str(s.expiry_date) if s.expiry_date else None,
                }
            )
        return {"sessions": sessions, "count": len(sessions)}

    def delete_session(self, session_name: str):
        self._ensure_sessions_client()
        resolved_name = ensure_mcp_session_name(session_name)

        with self._lock:
            self._evict(resolved_name)

        logger.info(f"Deleting session: {resolved_name}")
        deleted = self._sessions_client.delete(session_name=resolved_name)

        return {"session_name": resolved_name, "deleted": deleted}

    def close(self):
        with self._lock:
            for gds in self._sessions.values():
                with suppress(Exception):
                    gds.close()
            self._sessions.clear()
            self.graph_sessions.clear()
