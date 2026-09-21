from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
import uuid
from pathlib import Path
from typing import Any


def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _default_db_path() -> Path:
    appdata = os.getenv("APPDATA")

    if appdata:
        root = Path(appdata) / "ELARA"
    else:
        root = Path.home() / ".elara"

    root.mkdir(parents=True, exist_ok=True)

    return root / "elara_shared.db"


class SharedChatStore:
    """
    Shared SQLite chat store used by ELARA App and ELARA OS.

    The database lives outside either project so App and OS can be distributed
    separately while still using one chat source of truth.
    """

    def __init__(
        self,
        db_path: str | Path | None = None,
        legacy_json_path: str | Path | None = None,
    ) -> None:
        self.db_path = Path(db_path) if db_path else _default_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.legacy_json_path = (
            Path(legacy_json_path)
            if legacy_json_path
            else None
        )

        self._lock = threading.RLock()

        self._initialize()

        if self.legacy_json_path is not None:
            self.migrate_legacy_json(self.legacy_json_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.db_path.as_posix(),
            timeout=10.0,
            check_same_thread=False,
        )

        conn.row_factory = sqlite3.Row

        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=10000")

        return conn

    def _initialize(self) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS meta (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS chats (
                        id TEXT PRIMARY KEY,
                        owner_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        created TEXT NOT NULL,
                        updated TEXT NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS idx_chats_owner_updated
                        ON chats(owner_id, updated DESC);

                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id TEXT NOT NULL,
                        side TEXT NOT NULL,
                        text TEXT NOT NULL,
                        stamp TEXT NOT NULL,
                        attachment TEXT,
                        FOREIGN KEY(chat_id)
                            REFERENCES chats(id)
                            ON DELETE CASCADE
                    );

                    CREATE INDEX IF NOT EXISTS idx_messages_chat_id
                        ON messages(chat_id, id);
                    """
                )

    @staticmethod
    def _chat_key(owner_id: str) -> str:
        return f"active_chat:{owner_id}"

    def set_meta(
        self,
        key: str,
        value: str | None,
    ) -> None:
        with self._lock:
            with self._connect() as conn:
                if value is None:
                    conn.execute(
                        "DELETE FROM meta WHERE key = ?",
                        (key,),
                    )
                else:
                    conn.execute(
                        """
                        INSERT INTO meta(key, value)
                        VALUES(?, ?)
                        ON CONFLICT(key)
                        DO UPDATE SET value = excluded.value
                        """,
                        (key, value),
                    )

    def get_meta(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT value FROM meta WHERE key = ?",
                    (key,),
                ).fetchone()

        return str(row[0]) if row else default

    def set_active_owner(
        self,
        owner_id: str | None,
    ) -> None:
        self.set_meta(
            "active_owner_id",
            str(owner_id or "guest"),
        )

    def get_active_owner(self) -> str:
        return (
            self.get_meta(
                "active_owner_id",
                "guest",
            )
            or "guest"
        )

    def set_active_chat(
        self,
        owner_id: str,
        chat_id: str | None,
    ) -> None:
        self.set_meta(
            self._chat_key(owner_id),
            chat_id,
        )

    def get_active_chat(
        self,
        owner_id: str,
    ) -> str | None:
        return self.get_meta(
            self._chat_key(owner_id)
        )

    def _message_dict(
        self,
        row: sqlite3.Row,
    ) -> dict[str, Any]:
        item: dict[str, Any] = {
            "side": str(row["side"]),
            "text": str(row["text"]),
            "time": str(row["stamp"]),
        }

        if row["attachment"]:
            item["attachment"] = str(
                row["attachment"]
            )

        return item

    def get_session(
        self,
        owner_id: str,
        chat_id: str,
    ) -> dict[str, Any] | None:
        with self._lock:
            with self._connect() as conn:
                chat = conn.execute(
                    """
                    SELECT id
                         , owner_id
                         , title
                         , created
                         , updated
                    FROM chats
                    WHERE id = ?
                      AND owner_id = ?
                    """,
                    (
                        chat_id,
                        owner_id,
                    ),
                ).fetchone()

                if chat is None:
                    return None

                rows = conn.execute(
                    """
                    SELECT side
                         , text
                         , stamp
                         , attachment
                    FROM messages
                    WHERE chat_id = ?
                    ORDER BY id ASC
                    """,
                    (chat_id,),
                ).fetchall()

        return {
            "id": str(chat["id"]),
            "owner_id": str(chat["owner_id"]),
            "title": str(chat["title"]),
            "messages": [
                self._message_dict(row)
                for row in rows
            ],
            "updated": str(chat["updated"]),
        }

    def list_sessions(
        self,
        owner_id: str,
    ) -> list[dict[str, Any]]:
        with self._lock:
            with self._connect() as conn:
                chats = conn.execute(
                    """
                    SELECT id
                    FROM chats
                    WHERE owner_id = ?
                    ORDER BY updated DESC
                    LIMIT 100
                    """,
                    (owner_id,),
                ).fetchall()

        result: list[dict[str, Any]] = []

        for chat in chats:
            session = self.get_session(
                owner_id,
                str(chat["id"]),
            )

            if session is not None:
                result.append(session)

        result.reverse()

        result.sort(
            key=lambda item: str(
                item.get("updated", "")
            )
        )

        result = result[-100:]

        result.sort(
            key=lambda item: str(
                item.get("updated", "")
            ),
            reverse=True,
        )

        return result

    def create_session(
        self,
        owner_id: str,
        title: str = "New chat",
    ) -> dict[str, Any]:
        chat_id = uuid.uuid4().hex
        now = _now()

        session = {
            "id": chat_id,
            "owner_id": owner_id,
            "title": title or "New chat",
            "messages": [],
            "updated": now,
        }

        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO chats(
                        id,
                        owner_id,
                        title,
                        created,
                        updated
                    )
                    VALUES(?, ?, ?, ?, ?)
                    """,
                    (
                        chat_id,
                        owner_id,
                        session["title"],
                        now,
                        now,
                    ),
                )

        self.set_active_chat(
            owner_id,
            chat_id,
        )

        return session

    def save_session(
        self,
        session: dict[str, Any],
    ) -> None:
        owner_id = str(
            session.get(
                "owner_id",
                "guest",
            )
        ) or "guest"

        chat_id = str(
            session.get(
                "id",
                "",
            )
        ).strip()

        if not chat_id:
            return

        title = str(
            session.get(
                "title",
                "New chat",
            )
        ).strip() or "New chat"

        now = _now()

        messages = session.get(
            "messages",
            [],
        )

        if not isinstance(messages, list):
            messages = []

        with self._lock:
            with self._connect() as conn:
                existing = conn.execute(
                    """
                    SELECT created
                    FROM chats
                    WHERE id = ?
                    """,
                    (chat_id,),
                ).fetchone()

                created = (
                    str(existing[0])
                    if existing
                    else now
                )

                conn.execute(
                    """
                    INSERT INTO chats(
                        id,
                        owner_id,
                        title,
                        created,
                        updated
                    )
                    VALUES(?, ?, ?, ?, ?)

                    ON CONFLICT(id)
                    DO UPDATE SET
                        owner_id = excluded.owner_id,
                        title = excluded.title,
                        updated = excluded.updated
                    """,
                    (
                        chat_id,
                        owner_id,
                        title,
                        created,
                        now,
                    ),
                )

                conn.execute(
                    """
                    DELETE FROM messages
                    WHERE chat_id = ?
                    """,
                    (chat_id,),
                )

                for message in messages:
                    if not isinstance(
                        message,
                        dict,
                    ):
                        continue

                    side = str(
                        message.get(
                            "side",
                            "",
                        )
                    ).strip()

                    text = str(
                        message.get(
                            "text",
                            "",
                        )
                    ).strip()

                    if side not in {
                        "boss",
                        "elara",
                    } or not text:
                        continue

                    stamp = str(
                        message.get(
                            "time",
                            "",
                        )
                    ).strip() or now

                    attachment = str(
                        message.get(
                            "attachment",
                            "",
                        )
                    ).strip() or None

                    conn.execute(
                        """
                        INSERT INTO messages(
                            chat_id,
                            side,
                            text,
                            stamp,
                            attachment
                        )
                        VALUES(?, ?, ?, ?, ?)
                        """,
                        (
                            chat_id,
                            side,
                            text,
                            stamp,
                            attachment,
                        ),
                    )

        self.set_active_chat(
            owner_id,
            chat_id,
        )

    def append_message(
        self,
        owner_id: str,
        chat_id: str,
        side: str,
        text: str,
        attachment: str | None = None,
        stamp: str | None = None,
    ) -> None:
        side = str(side).strip()
        text = str(text).strip()

        if side not in {
            "boss",
            "elara",
        } or not text:
            return

        timestamp = stamp or _now()

        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO messages(
                        chat_id,
                        side,
                        text,
                        stamp,
                        attachment
                    )
                    VALUES(?, ?, ?, ?, ?)
                    """,
                    (
                        chat_id,
                        side,
                        text,
                        timestamp,
                        attachment,
                    ),
                )

                conn.execute(
                    """
                    UPDATE chats
                    SET updated = ?
                    WHERE id = ?
                      AND owner_id = ?
                    """,
                    (
                        timestamp,
                        chat_id,
                        owner_id,
                    ),
                )

        self.set_active_chat(
            owner_id,
            chat_id,
        )

    def update_title_from_messages(
        self,
        owner_id: str,
        chat_id: str,
        messages: list[dict[str, Any]],
    ) -> None:
        first_user = next(
            (
                str(
                    message.get(
                        "text",
                        "",
                    )
                )
                for message in messages
                if message.get("side") == "boss"
                and str(
                    message.get(
                        "text",
                        "",
                    )
                ).strip()
            ),
            "",
        )

        if not first_user:
            return

        full_title = " ".join(
            first_user.split()
        )

        title = full_title[:48]

        if len(full_title) > 48:
            title = title.rstrip() + "…"

        now = _now()

        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    UPDATE chats
                    SET title = ?,
                        updated = ?
                    WHERE id = ?
                      AND owner_id = ?
                    """,
                    (
                        title,
                        now,
                        chat_id,
                        owner_id,
                    ),
                )

    def ensure_active_session(
        self,
        owner_id: str,
    ) -> dict[str, Any]:
        active_id = self.get_active_chat(
            owner_id
        )

        if active_id:
            existing = self.get_session(
                owner_id,
                active_id,
            )

            if existing is not None:
                return existing

        sessions = self.list_sessions(
            owner_id
        )

        if sessions:
            newest = sessions[0]

            self.set_active_chat(
                owner_id,
                str(newest["id"]),
            )

            return newest

        return self.create_session(
            owner_id
        )

    def os_active_session(
        self,
    ) -> dict[str, Any]:
        owner = self.get_active_owner()

        return self.ensure_active_session(
            owner
        )

    def append_os_message(
        self,
        side: str,
        text: str,
        attachment: str | None = None,
    ) -> dict[str, Any]:
        owner = self.get_active_owner()

        session = self.ensure_active_session(
            owner
        )

        chat_id = str(
            session["id"]
        )

        self.append_message(
            owner,
            chat_id,
            side,
            text,
            attachment=attachment,
        )

        updated = self.get_session(
            owner,
            chat_id,
        )

        return (
            updated
            if updated is not None
            else session
        )

    def migrate_legacy_json(
        self,
        legacy_path: str | Path,
    ) -> int:
        path = Path(
            legacy_path
        )

        if not path.exists():
            return 0

        marker = (
            f"migrated:{path.resolve()}"
        )

        if self.get_meta(marker) == "1":
            return 0

        try:
            raw = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )
        except Exception:
            return 0

        if not isinstance(raw, list):
            self.set_meta(
                marker,
                "1",
            )
            return 0

        imported = 0

        with self._lock:
            with self._connect() as conn:
                for item in raw:
                    if not isinstance(
                        item,
                        dict,
                    ):
                        continue

                    chat_id = str(
                        item.get(
                            "id",
                            "",
                        )
                    ).strip()

                    owner_id = str(
                        item.get(
                            "owner_id",
                            "guest",
                        )
                    ).strip() or "guest"

                    if not chat_id:
                        continue

                    exists = conn.execute(
                        """
                        SELECT 1
                        FROM chats
                        WHERE id = ?
                        """,
                        (chat_id,),
                    ).fetchone()

                    if exists:
                        continue

                    title = str(
                        item.get(
                            "title",
                            "New chat",
                        )
                    ).strip() or "New chat"

                    updated = str(
                        item.get(
                            "updated",
                            "",
                        )
                    ).strip() or _now()

                    conn.execute(
                        """
                        INSERT INTO chats(
                            id,
                            owner_id,
                            title,
                            created,
                            updated
                        )
                        VALUES(?, ?, ?, ?, ?)
                        """,
                        (
                            chat_id,
                            owner_id,
                            title,
                            updated,
                            updated,
                        ),
                    )

                    raw_messages = item.get(
                        "messages",
                        [],
                    )

                    if not isinstance(
                        raw_messages,
                        list,
                    ):
                        raw_messages = []

                    for message in raw_messages:
                        if not isinstance(
                            message,
                            dict,
                        ):
                            continue

                        side = str(
                            message.get(
                                "side",
                                "",
                            )
                        ).strip()

                        text = str(
                            message.get(
                                "text",
                                "",
                            )
                        ).strip()

                        if side not in {
                            "boss",
                            "elara",
                        } or not text:
                            continue

                        stamp = str(
                            message.get(
                                "time",
                                "",
                            )
                        ).strip() or updated

                        attachment = str(
                            message.get(
                                "attachment",
                                "",
                            )
                        ).strip() or None

                        conn.execute(
                            """
                            INSERT INTO messages(
                                chat_id,
                                side,
                                text,
                                stamp,
                                attachment
                            )
                            VALUES(?, ?, ?, ?, ?)
                            """,
                            (
                                chat_id,
                                side,
                                text,
                                stamp,
                                attachment,
                            ),
                        )

                    imported += 1

        self.set_meta(
            marker,
            "1",
        )

        return imported