import logging
import os
from contextlib import suppress
from datetime import timedelta
from typing import Optional, Tuple
from graphdatascience import GraphDataScience
from graphdatascience.session import GdsSessions, AuraAPICredentials, SessionMemory
from graphdatascience.session.dbms_connection_info import DbmsConnectionInfo

logger = logging.getLogger("mcp_server_neo4j_gds")


class GdsMode:
    PLUGIN = "plugin"
    SESSION = "session"


class SessionManager:
    def __init__(self):
        self.mode: Optional[str] = None
        self.session_gds: Optional[GraphDataScience] = None
        self.session_name: Optional[str] = None
        self._sessions_client: Optional[GdsSessions] = None
        self._db_url: Optional[str] = None
        self._auth: Optional[Tuple[str, str]] = None
        self._database: Optional[str] = None

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

    def create_or_get_session(
        self, db_url: str, auth: Tuple[str, str], database: Optional[str] = None
    ) -> GraphDataScience:
        if self.session_gds is not None:
            return self.session_gds

        self._db_url = db_url
        self._auth = auth
        self._database = database

        self._ensure_sessions_client()

        memory_gb = int(os.getenv("SESSION_MEMORY_GB", "8"))
        memory = getattr(SessionMemory, f"m_{memory_gb}GB")
        session_name = os.getenv("SESSION_NAME", "mcp_gds_session")
        ttl_hours = int(os.getenv("SESSION_TTL_HOURS", "24"))

        logger.info(
            f"Creating or getting session '{session_name}' with {memory_gb}GB memory and {ttl_hours}h TTL"
        )

        db_connection = DbmsConnectionInfo(
            uri=db_url, username=auth[0], password=auth[1], database=database
        )

        self.session_gds = self._sessions_client.get_or_create(
            session_name=session_name,
            memory=memory,
            ttl=timedelta(hours=ttl_hours),
            db_connection=db_connection,
        )
        self.session_name = session_name
        logger.info(f"Session '{session_name}' created/retrieved successfully")
        return self.session_gds

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

    def delete_session(self, session_name: Optional[str] = None):
        self._ensure_sessions_client()

        name_to_delete = session_name or self.session_name
        if not name_to_delete:
            raise ValueError("No session name specified")

        deleting_current_session = name_to_delete == self.session_name
        if deleting_current_session and self.session_gds is not None:
            with suppress(Exception):
                self.session_gds.close()

        logger.info(f"Deleting session: {name_to_delete}")
        deleted = self._sessions_client.delete(session_name=name_to_delete)

        if deleting_current_session:
            self.session_gds = None
            self.session_name = None

        return {"session_name": name_to_delete, "deleted": deleted}

    def recreate_session(self, memory_gb: Optional[int] = None):
        if self._db_url is None:
            raise RuntimeError(
                "Cannot recreate session before one has been created. Run an algorithm first."
            )

        if self.session_name:
            try:
                self.delete_session(self.session_name)
            except Exception as e:
                logger.warning(f"Failed to delete existing session: {e}")

        if memory_gb is not None:
            os.environ["SESSION_MEMORY_GB"] = str(memory_gb)

        return self.create_or_get_session(self._db_url, self._auth, self._database)

    def close(self):
        if self.session_gds is not None:
            try:
                self.session_gds.close()
            except Exception as e:
                logger.warning(f"Error closing session: {e}")
