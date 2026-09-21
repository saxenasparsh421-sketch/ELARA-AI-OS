from __future__ import annotations

from pathlib import Path
from typing import Optional

from shared.chat_store import ChatStore


class ELARAOSChatBridge:
    """
    ELARA OS <-> shared chat database bridge.

    ELARA App and ELARA OS both use:
        data/elara.db
    """

    def __init__(self):
        self.store = ChatStore()
        self.active_conversation_id: Optional[str] = None

    # ---------------------------------------------------------
    # CONVERSATION
    # ---------------------------------------------------------

    def start_conversation(
        self,
        title: str = "New Chat",
    ) -> str:

        conversation_id = self.store.create_conversation(
            title=title
        )

        self.active_conversation_id = conversation_id

        self.store.set_active_conversation(
            conversation_id
        )

        return conversation_id

    def use_conversation(
        self,
        conversation_id: str,
    ) -> None:

        if not self.store.conversation_exists(
            conversation_id
        ):
            raise ValueError(
                f"Conversation does not exist: {conversation_id}"
            )

        self.active_conversation_id = conversation_id

        self.store.set_active_conversation(
            conversation_id
        )

    def get_active_conversation(self) -> str:

        if self.active_conversation_id:

            if self.store.conversation_exists(
                self.active_conversation_id
            ):
                return self.active_conversation_id

        conversation_id = (
            self.store.get_or_create_active_conversation()
        )

        self.active_conversation_id = conversation_id

        return conversation_id

    # ---------------------------------------------------------
    # BOSS MESSAGE
    # ---------------------------------------------------------

    def save_boss_message(
        self,
        text: str,
        conversation_id: Optional[str] = None,
    ) -> int:

        conversation_id = (
            conversation_id
            or self.get_active_conversation()
        )

        return self.store.add_message(
            conversation_id=conversation_id,
            role="boss",
            content=text,
            source="os",
        )

    # ---------------------------------------------------------
    # ELARA MESSAGE
    # ---------------------------------------------------------

    def save_elara_message(
        self,
        text: str,
        conversation_id: Optional[str] = None,
    ) -> int:

        conversation_id = (
            conversation_id
            or self.get_active_conversation()
        )

        return self.store.add_message(
            conversation_id=conversation_id,
            role="elara",
            content=text,
            source="os",
        )

    # ---------------------------------------------------------
    # ATTACHMENT
    # ---------------------------------------------------------

    def save_attachment(
        self,
        file_path: str | Path,
        conversation_id: Optional[str] = None,
        message_id: Optional[int] = None,
        mime_type: Optional[str] = None,
    ) -> int:

        conversation_id = (
            conversation_id
            or self.get_active_conversation()
        )

        path = Path(file_path)

        return self.store.add_attachment(
            conversation_id=conversation_id,
            file_path=str(path),
            message_id=message_id,
            file_name=path.name,
            mime_type=mime_type,
        )

    # ---------------------------------------------------------
    # READ MESSAGES
    # ---------------------------------------------------------

    def get_messages(
        self,
        conversation_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[dict]:

        conversation_id = (
            conversation_id
            or self.get_active_conversation()
        )

        return self.store.get_messages(
            conversation_id,
            limit=limit,
        )

    # ---------------------------------------------------------
    # READ CONVERSATIONS
    # ---------------------------------------------------------

    def get_conversations(self) -> list[dict]:
        return self.store.list_conversations()


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    print("ELARA OS Chat Bridge")
    print("=" * 40)

    bridge = ELARAOSChatBridge()

    conversation_id = bridge.start_conversation(
        "OS Bridge Test"
    )

    print(
        "Conversation ID:",
        conversation_id
    )

    boss_message_id = bridge.save_boss_message(
        "Boss message from ELARA OS"
    )

    print(
        "Boss message ID:",
        boss_message_id
    )

    elara_message_id = bridge.save_elara_message(
        "ELARA OS is connected to shared storage."
    )

    print(
        "ELARA message ID:",
        elara_message_id
    )

    print("\nStored messages:")

    messages = bridge.get_messages()

    for message in messages:

        print(
            f"{message['role']}: "
            f"{message['content']} "
            f"[source={message['source']}]"
        )

    print("\nStored conversations:")

    conversations = bridge.get_conversations()

    for conversation in conversations:

        print(
            conversation["id"],
            conversation["title"]
        )

    print(
        "\nELARA OS Chat Bridge test completed successfully."
    )