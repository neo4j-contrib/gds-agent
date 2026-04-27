import logging
import os
from typing import Optional, Tuple
from graphdatascience import GraphDataScience
from graphdatascience.session import GdsSessions, AuraAPICredentials, SessionMemory

logger = logging.getLogger("mcp_server_neo4j_gds")


class GdsMode:
    PLUGIN = "plugin"
    SESSION = "session"


class SessionManager:
    def __init__(self):
        self.mode: Optional[str] = None
        self.session_gds: Optional[GraphDataScience] = None
        self.session_name: Optional[str] = None
        self._aura_credentials: Optional[AuraAPICredentials] = None
        self._sessions_client: Optional[GdsSessions] = None
        self._db_url: Optional[str] = None
        self._auth: Optional[Tuple[str, str]] = None
        self._database: Optional[str] = None

    def detect_mode(self, gds: GraphDataScience) -> str:
        if self.mode is not None:
            return self.mode

        try:
            result = gds.run_cypher(
                "CALL gds.session.list() YIELD name RETURN name LIMIT 1"
            )
            self.mode = GdsMode.SESSION
            logger.info("Detected GDS Aura Graph Analytics (sessions) mode")
        except Exception as e:
            error_msg = str(e).lower()
            if (
                "no procedure" in error_msg
                or "unknown function" in error_msg
                or "there is no procedure" in error_msg
            ):
                self.mode = GdsMode.PLUGIN
                logger.info("Detected GDS Plugin (on-prem) mode")
            else:
                logger.warning(
                    f"Could not determine GDS mode, defaulting to plugin: {e}"
                )
                self.mode = GdsMode.PLUGIN

        return self.mode

    def initialize_aura_credentials(self):
        client_id = os.getenv("AURA_API_CLIENT_ID")
        client_secret = os.getenv("AURA_API_CLIENT_SECRET")
        project_id = os.getenv("AURA_API_PROJECT_ID")

        if not all([client_id, client_secret, project_id]):
            raise ValueError(
                "Missing Aura API credentials. Set AURA_API_CLIENT_ID, AURA_API_CLIENT_SECRET, and AURA_API_PROJECT_ID"
            )

        self._aura_credentials = AuraAPICredentials(
            client_id, client_secret, project_id
        )
        self._sessions_client = GdsSessions(api_credentials=self._aura_credentials)
        logger.info("Aura API credentials initialized")

    def create_or_get_session(
        self, db_url: str, auth: Tuple[str, str], database: Optional[str] = None
    ) -> GraphDataScience:
        if self.session_gds is not None:
            logger.info(f"Reusing existing session: {self.session_name}")
            return self.session_gds

        self._db_url = db_url
        self._auth = auth
        self._database = database

        if self._sessions_client is None:
            self.initialize_aura_credentials()

        memory_gb = int(os.getenv("SESSION_MEMORY_GB", "8"))
        memory = getattr(SessionMemory, f"m_{memory_gb}GB")
        session_name = os.getenv("SESSION_NAME", "mcp_gds_session")
        ttl_hours = int(os.getenv("SESSION_TTL_HOURS", "24"))

        logger.info(
            f"Creating or getting session '{session_name}' with {memory_gb}GB memory and {ttl_hours}h TTL"
        )

        try:
            self.session_gds = self._sessions_client.get_or_create(
                session_name=session_name,
                memory=memory,
                ttl=ttl_hours * 3600,
                db_connection=(db_url, auth[0], auth[1]),
            )
            self.session_name = session_name
            logger.info(f"Session '{session_name}' created/retrieved successfully")

            self.session_gds.verify_connectivity()
            logger.info("Session connectivity verified")

            return self.session_gds
        except Exception as e:
            logger.error(f"Failed to create/get session: {e}")
            raise

    def list_sessions(self):
        if self._sessions_client is None:
            self.initialize_aura_credentials()

        sessions_df = self._sessions_client.list()
        if sessions_df.empty:
            return {"sessions": [], "count": 0}

        sessions = []
        for _, row in sessions_df.iterrows():
            sessions.append(
                {
                    "name": row.get("name"),
                    "status": row.get("status"),
                    "memory": row.get("memory"),
                    "created_at": str(row.get("created_at")),
                    "expires_at": str(row.get("expires_at")),
                }
            )

        return {"sessions": sessions, "count": len(sessions)}

    def delete_session(self, session_name: Optional[str] = None):
        if self._sessions_client is None:
            self.initialize_aura_credentials()

        name_to_delete = session_name or self.session_name
        if not name_to_delete:
            raise ValueError("No session name specified")

        logger.info(f"Deleting session: {name_to_delete}")
        self._sessions_client.delete(session_name=name_to_delete)

        if name_to_delete == self.session_name:
            self.session_gds = None
            self.session_name = None

        return {"session_name": name_to_delete, "deleted": True}

    def recreate_session(self, memory_gb: Optional[int] = None):
        if self.session_name:
            logger.info(
                f"Deleting existing session before recreation: {self.session_name}"
            )
            try:
                self.delete_session(self.session_name)
            except Exception as e:
                logger.warning(f"Failed to delete existing session: {e}")

        if memory_gb:
            os.environ["SESSION_MEMORY_GB"] = str(memory_gb)

        return self.create_or_get_session(self._db_url, self._auth, self._database)

    def get_gds(self, base_gds: GraphDataScience) -> GraphDataScience:
        mode = self.detect_mode(base_gds)

        if mode == GdsMode.PLUGIN:
            return base_gds
        elif mode == GdsMode.SESSION:
            if self.session_gds is None:
                raise RuntimeError(
                    "Session mode detected but no session created. Session will be created on first use."
                )
            return self.session_gds
        else:
            raise ValueError(f"Unknown GDS mode: {mode}")

    def close(self):
        if self.session_gds is not None:
            try:
                logger.info("Closing session GDS connection")
                self.session_gds.close()
            except Exception as e:
                logger.warning(f"Error closing session: {e}")
