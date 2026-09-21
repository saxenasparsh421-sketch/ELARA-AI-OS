from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "elara.db"
LEGACY_JSON_PATH = DATA_DIR / "elara_chats.json"


class ChatStore:
    """
    Shared persistent chat storage for ELARA App and ELARA OS.

    Both the GUI application and the background OS use this same database.

    Database:
        data/elara.db
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DB_PATH

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._initialize_database()

    # ---------------------------------------------------------
    # DATABASE
    # ---------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            str(self.db_path),
            timeout=15,
        )

        connection.row_factory = sqlite3.Row

        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA foreign_keys=ON;")
        connection.execute("PRAGMA busy_timeout=15000;")

        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT 'New Chat',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'app',
                    created_at TEXT NOT NULL,

                    FOREIGN KEY (conversation_id)
                        REFERENCES conversations(id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    message_id INTEGER,
                    file_path TEXT NOT NULL,
                    file_name TEXT,
                    mime_type TEXT,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY (conversation_id)
                        REFERENCES conversations(id)
                        ON DELETE CASCADE,

                    FOREIGN KEY (message_id)
                        REFERENCES messages(id)
                        ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                    ON messages(conversation_id);

                CREATE INDEX IF NOT EXISTS idx_messages_created
                    ON messages(created_at);

                CREATE INDEX IF NOT EXISTS idx_attachments_conversation
                    ON attachments(conversation_id);
                """
            )

    # ---------------------------------------------------------
    # TIME
    # ---------------------------------------------------------

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    # ---------------------------------------------------------
    # CONVERSATIONS
    # ---------------------------------------------------------

    def create_conversation(
        self,
        title: str = "New Chat",
    ) -> str:
        conversation_id = uuid.uuid4().hex
        timestamp = self._now()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO conversations
                (
                    id,
                    title,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    title.strip() or "New Chat",
                    timestamp,
                    timestamp,
                ),
            )

        return conversation_id

    def conversation_exists(
        self,
        conversation_id: str,
    ) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM conversations
                WHERE id = ?
                LIMIT 1
                """,
                (conversation_id,),
            ).fetchone()

        return row is not None

    def get_conversation(
        self,
        conversation_id: str,
    ) -> Optional[dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    title,
                    created_at,
                    updated_at
                FROM conversations
                WHERE id = ?
                """,
                (conversation_id,),
            ).fetchone()

        return dict(row) if row else None

    def list_conversations(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    title,
                    created_at,
                    updated_at
                FROM conversations
                ORDER BY updated_at DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def rename_conversation(
        self,
        conversation_id: str,
        title: str,
    ) -> bool:
        title = title.strip() or "New Chat"

        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE conversations
                SET
                    title = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    title,
                    self._now(),
                    conversation_id,
                ),
            )

        return cursor.rowcount > 0

    def delete_conversation(
        self,
        conversation_id: str,
    ) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM conversations
                WHERE id = ?
                """,
                (conversation_id,),
            )

        return cursor.rowcount > 0

    # ---------------------------------------------------------
    # MESSAGES
    # ---------------------------------------------------------

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        source: str = "app",
    ) -> int:
        if not self.conversation_exists(conversation_id):
            raise ValueError(
                f"Conversation does not exist: {conversation_id}"
            )

        role = role.strip().lower()
        source = source.strip().lower()

        if not role:
            raise ValueError("Message role cannot be empty.")

        if not content:
            content = ""

        timestamp = self._now()

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO messages
                (
                    conversation_id,
                    role,
                    content,
                    source,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    role,
                    content,
                    source,
                    timestamp,
                ),
            )

            connection.execute(
                """
                UPDATE conversations
                SET updated_at = ?
                WHERE id = ?
                """,
                (
                    timestamp,
                    conversation_id,
                ),
            )

            return int(cursor.lastrowid)

    def get_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                id,
                conversation_id,
                role,
                content,
                source,
                created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
        """

        parameters: list[Any] = [conversation_id]

        if limit is not None:
            limit = max(1, int(limit))

            query = """
                SELECT
                    id,
                    conversation_id,
                    role,
                    content,
                    source,
                    created_at
                FROM (
                    SELECT
                        id,
                        conversation_id,
                        role,
                        content,
                        source,
                        created_at
                    FROM messages
                    WHERE conversation_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                )
                ORDER BY id ASC
            """

            parameters.append(limit)

        with self._connect() as connection:
            rows = connection.execute(
                query,
                parameters,
            ).fetchall()

        return [dict(row) for row in rows]

    def get_last_message(
        self,
        conversation_id: str,
    ) -> Optional[dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    conversation_id,
                    role,
                    content,
                    source,
                    created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (conversation_id,),
            ).fetchone()

        return dict(row) if row else None

    # ---------------------------------------------------------
    # ATTACHMENTS
    # ---------------------------------------------------------

    def add_attachment(
        self,
        conversation_id: str,
        file_path: str,
        message_id: Optional[int] = None,
        file_name: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> int:
        if not self.conversation_exists(conversation_id):
            raise ValueError(
                f"Conversation does not exist: {conversation_id}"
            )

        timestamp = self._now()

        if file_name is None:
            file_name = Path(file_path).name

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO attachments
                (
                    conversation_id,
                    message_id,
                    file_path,
                    file_name,
                    mime_type,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    message_id,
                    str(file_path),
                    file_name,
                    mime_type,
                    timestamp,
                ),
            )

            return int(cursor.lastrowid)

    def get_attachments(
        self,
        conversation_id: str,
    ) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    conversation_id,
                    message_id,
                    file_path,
                    file_name,
                    mime_type,
                    created_at
                FROM attachments
                WHERE conversation_id = ?
                ORDER BY id ASC
                """,
                (conversation_id,),
            ).fetchall()

        return [dict(row) for row in rows]

    # ---------------------------------------------------------
    # SETTINGS
    # ---------------------------------------------------------

    def set_setting(
        self,
        key: str,
        value: Any,
    ) -> None:
        serialized = json.dumps(
            value,
            ensure_ascii=False,
        )

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO settings
                (
                    key,
                    value
                )
                VALUES (?, ?)
                ON CONFLICT(key)
                DO UPDATE SET value = excluded.value
                """,
                (
                    key,
                    serialized,
                ),
            )

    def get_setting(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT value
                FROM settings
                WHERE key = ?
                """,
                (key,),
            ).fetchone()

        if row is None:
            return default

        try:
            return json.loads(row["value"])
        except Exception:
            return row["value"]

    # ---------------------------------------------------------
    # ACTIVE CHAT
    # ---------------------------------------------------------

    def set_active_conversation(
        self,
        conversation_id: str,
    ) -> None:
        if not self.conversation_exists(conversation_id):
            raise ValueError(
                f"Conversation does not exist: {conversation_id}"
            )

        self.set_setting(
            "active_conversation_id",
            conversation_id,
        )

    def get_active_conversation(self) -> Optional[str]:
        return self.get_setting(
            "active_conversation_id",
            None,
        )

    def get_or_create_active_conversation(self) -> str:
        active_id = self.get_active_conversation()

        if active_id and self.conversation_exists(active_id):
            return active_id

        conversations = self.list_conversations()

        if conversations:
            conversation_id = conversations[0]["id"]
        else:
            conversation_id = self.create_conversation()

        self.set_active_conversation(conversation_id)

        return conversation_id

    # ---------------------------------------------------------
    # LEGACY JSON MIGRATION
    # ---------------------------------------------------------

    def migrate_legacy_json(
        self,
        json_path: Optional[Path] = None,
    ) -> Optional[str]:
        """
        Import the old data/elara_chats.json file.

        This method does NOT delete or modify the old JSON file.

        It returns the first imported conversation ID.
        """

        path = Path(json_path) if json_path else LEGACY_JSON_PATH

        if not path.exists():
            return None

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)
        except Exception:
            return None

        if not data:
            return None

        imported_first_id = None

        # -----------------------------------------------------
        # Format 1
        #
        # {
        #   "chat_id": {
        #       ...
        #   }
        # }
        # -----------------------------------------------------

        if isinstance(data, dict):
            items = list(data.items())
        elif isinstance(data, list):
            items = []

            for index, item in enumerate(data):
                items.append(
                    (
                        str(index),
                        item,
                    )
                )
        else:
            return None

        for legacy_key, chat_data in items:
            if not isinstance(chat_data, dict):
                continue

            title = (
                chat_data.get("title")
                or chat_data.get("name")
                or "New Chat"
            )

            messages = (
                chat_data.get("messages")
                or chat_data.get("history")
                or []
            )

            conversation_id = self.create_conversation(
                title=str(title),
            )

            if imported_first_id is None:
                imported_first_id = conversation_id

            if not isinstance(messages, list):
                continue

            for message in messages:
                if not isinstance(message, dict):
                    continue

                role = (
                    message.get("role")
                    or message.get("side")
                    or message.get("sender")
                    or "elara"
                )

                content = (
                    message.get("content")
                    or message.get("text")
                    or message.get("message")
                    or ""
                )

                source = (
                    message.get("source")
                    or "app"
                )

                self.add_message(
                    conversation_id=conversation_id,
                    role=str(role),
                    content=str(content),
                    source=str(source),
                )

        if imported_first_id:
            self.set_active_conversation(
                imported_first_id
            )

        return imported_first_id


# -------------------------------------------------------------
# SIMPLE SHARED INSTANCE
# -------------------------------------------------------------

chat_store = ChatStore()


if __name__ == "__main__":
    print("ELARA Chat Store")
    print(f"Database: {DB_PATH}")

    store = ChatStore()

    conversation_id = store.create_conversation(
        "ELARA Test Chat"
    )

    print(
        "Created conversation:",
        conversation_id,
    )

    user_message_id = store.add_message(
        conversation_id,
        "boss",
        "Hello ELARA",
        "app",
    )

    print(
        "Added Boss message:",
        user_message_id,
    )

    elara_message_id = store.add_message(
        conversation_id,
        "elara",
        "Hello Boss",
        "os",
    )

    print(
        "Added ELARA message:",
        elara_message_id,
    )

    messages = store.get_messages(
        conversation_id
    )

    print("\nMessages:")

    for message in messages:
        print(
            f"{message['role']}: "
            f"{message['content']} "
            f"[{message['source']}]"
        )

    print("\nConversations:")

    for conversation in store.list_conversations():
        print(
            conversation["id"],
            conversation["title"],
        )

    print("\nChat store test completed successfully.")