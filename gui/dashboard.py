"""
ELARA desktop interface v12

The interface keeps the existing desktop command router and OpenRouter brain.
The sidebar intentionally contains only New chat  Images  and Account.

Visible ELARA responses never contain comma characters.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import threading
import time
import uuid
from pathlib import Path
from typing import Any
import mimetypes

import tkinter as tk
from tkinter import filedialog
from tkinter import font as tkfont
from tkinter import messagebox

from PIL import Image, ImageTk

from commands.router import route
from services.brain_service import BrainService
from shared_chat_store import SharedChatStore


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHAT_STORE = DATA_DIR / "elara_chats.json"
ACCOUNT_STORE = DATA_DIR / "elara_accounts.json"
SESSION_STORE = DATA_DIR / "elara_session.json"


class ELARADashboard:
    # ----------------------------------------------------------
    # Visual palette
    # ----------------------------------------------------------
    BG = "#000000"
    SIDEBAR = "#171717"
    HOVER = "#2A2A2A"
    ACTIVE = "#2F2F2F"
    COMPOSER = "#2A2A2A"
    BORDER = "#3F3F3F"
    TEXT = "#ECECEC"
    SECONDARY = "#AFAFAF"
    MUTED = "#7D7D7D"
    USER_BUBBLE = "#2F2F2F"
    PURPLE = "#8B5CF6"
    PURPLE_HOVER = "#A78BFA"
    WHITE = "#FFFFFF"
    DANGER = "#F87171"
    SUCCESS = "#22C55E"

    WIDTH = 1366
    HEIGHT = 820
    SIDEBAR_WIDTH = 240

    PBKDF2_ROUNDS = 210_000

    def __init__(self):
        self.root = tk.Tk()
        self.root.tk.call("tk", "scaling", 1.18)
        self.root.title("ELARA")
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.root.minsize(980, 650)
        self.root.configure(bg=self.BG)

        # ------------------------------------------------------
        # Runtime
        # ------------------------------------------------------
        self.brain: BrainService | None = None
        self.processing = False
        self.listening = False
        self.stop_requested = False
        self.active_request_id: str | None = None

        # ------------------------------------------------------
        # Speech
        # ------------------------------------------------------
        # SpeechService is intentionally created only once and reused
        # for every microphone request. Whisper should not reload on
        # every button press.
        self.speech_service = None
        self.speech_service_lock = threading.Lock()

        # ------------------------------------------------------
        # Chat
        # ------------------------------------------------------
        self.sessions: list[dict[str, Any]] = []
        self.active_session_id: str | None = None
        self.messages: list[dict[str, str]] = []
        self.attached_file: Path | None = None
        self.active_context_attachment: Path | None = None
        self._attachment_image_refs: list[ImageTk.PhotoImage] = []
        self.entry_placeholder = True

        # ------------------------------------------------------
        # Search is intentionally not in the sidebar.
        # ------------------------------------------------------
        self.search_mode = False
        self.search_entry: tk.Entry | None = None

        # ------------------------------------------------------
        # Account
        # ------------------------------------------------------
        self.accounts: list[dict[str, Any]] = []
        self.current_account_id: str | None = None
        self.current_username: str | None = None

        # ------------------------------------------------------
        # State
        # ------------------------------------------------------
        self.home_mode = True

        self.setup_fonts()
        self.shared_chat_store = SharedChatStore(legacy_json_path=CHAT_STORE)
        self.load_accounts()
        self.load_current_account()
        self.shared_chat_store.set_active_owner(str(self.current_account_id or "guest"))
        self.load_sessions()
        self.ensure_active_session()

        self.build_shell()
        self.render_state()
        self.update_account_button()
        self.root.after(1500, self.refresh_from_shared_store)

        self.root.after(150, self.initialize_brain)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<Escape>", self.escape_action)
        self.root.bind("<Control-n>", self.shortcut_new_chat)
        self.root.bind_all("<MouseWheel>", self.chat_mousewheel_global, add="+")
        self.root.bind_all("<Button-4>", self.chat_scroll_up, add="+")
        self.root.bind_all("<Button-5>", self.chat_scroll_down, add="+")

    # ==========================================================
    # FONT SETUP
    # ==========================================================

    def setup_fonts(self):
        available = set(tkfont.families(self.root))
        self.font_body = "Segoe UI" if "Segoe UI" in available else "Arial"
        self.font_brand = "Michroma" if "Michroma" in available else self.font_body
        self.font_symbol = (
            "Segoe UI Symbol" if "Segoe UI Symbol" in available else self.font_body
        )
        self.font_emoji = (
            "Segoe UI Emoji" if "Segoe UI Emoji" in available else self.font_body
        )

    # ==========================================================
    # OUTPUT RULE
    # ==========================================================

    @staticmethod
    def sanitize_elara_output(text: str) -> str:
        value = str(text)

        # Keep ELARA responses visually clean in the Tkinter chat.
        # Remove common Markdown markers so raw formatting symbols such as
        # **bold** and ### headings do not appear in the UI.
        import re

        value = value.replace("```", "")
        value = value.replace("`", "")
        value = re.sub(r"\*{1,3}([^*\n]+?)\*{1,3}", r"\1", value)
        value = re.sub(r"_{1,3}([^_\n]+?)_{1,3}", r"\1", value)
        value = re.sub(r"^\s*#{1,6}\s*", "", value, flags=re.MULTILINE)
        value = re.sub(r"^\s*[-+*]\s+", "", value, flags=re.MULTILINE)
        value = re.sub(r"^\s*>\s?", "", value, flags=re.MULTILINE)

        # Remove stray decorative Unicode symbols that commonly appear in
        # model output while keeping normal letters numbers and punctuation.
        value = value.replace("•", "")
        value = value.replace("▪", "")
        value = value.replace("▫", "")
        value = value.replace("◦", "")

        # ELARA output rule: never show commas.
        value = value.replace(",", "")

        # Normalize excess blank lines without flattening the response.
        value = re.sub(r"\n{3,}", "\n\n", value)
        return value.strip()

    # ==========================================================
    # ACCOUNT AUTH
    # ==========================================================

    def load_accounts(self):
        self.accounts = []
        try:
            if not ACCOUNT_STORE.exists():
                return

            raw_text = ACCOUNT_STORE.read_text(encoding="utf-8").strip()
            if not raw_text:
                return

            raw = json.loads(raw_text)
            if not isinstance(raw, list):
                return

            for item in raw:
                if not isinstance(item, dict):
                    continue
                if not item.get("id") or not item.get("username"):
                    continue
                self.accounts.append(item)
        except Exception as error:
            print("[ACCOUNT STORE LOAD ERROR]", error)
            self.accounts = []

    def save_accounts(self):
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            ACCOUNT_STORE.write_text(
                json.dumps(self.accounts, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as error:
            print("[ACCOUNT STORE SAVE ERROR]", error)

    @classmethod
    def _hash_password(cls, password: str, salt: bytes | None = None):
        if salt is None:
            salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            cls.PBKDF2_ROUNDS,
        )
        return salt.hex(), digest.hex()

    @classmethod
    def _verify_password(cls, password: str, salt_hex: str, hash_hex: str):
        try:
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(hash_hex)
        except ValueError:
            return False

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            cls.PBKDF2_ROUNDS,
        )
        return hmac.compare_digest(actual, expected)

    def load_current_account(self):
        self.current_account_id = None
        self.current_username = None
        try:
            if not SESSION_STORE.exists():
                return

            raw_text = SESSION_STORE.read_text(encoding="utf-8").strip()
            if not raw_text:
                return

            raw = json.loads(raw_text)
            account_id = str(raw.get("account_id", "")).strip()
            if not account_id:
                return

            for account in self.accounts:
                if str(account.get("id")) == account_id:
                    self.current_account_id = account_id
                    self.current_username = str(account.get("username", "")).strip()
                    self.shared_chat_store.set_active_owner(account_id)
                    return
        except Exception as error:
            print("[ACCOUNT SESSION LOAD ERROR]", error)

        self.shared_chat_store.set_active_owner(str(self.current_account_id or "guest"))

    def save_current_account(self):
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            SESSION_STORE.write_text(
                json.dumps(
                    {"account_id": self.current_account_id},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            self.shared_chat_store.set_active_owner(str(self.current_account_id or "guest"))
        except Exception as error:
            print("[ACCOUNT SESSION SAVE ERROR]", error)

    def account_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("ELARA Account")
        dialog.configure(bg=self.SIDEBAR)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        width = 360
        height = 350 if self.current_account_id is None else 230
        x = self.root.winfo_x() + max((self.root.winfo_width() - width) // 2, 10)
        y = self.root.winfo_y() + max((self.root.winfo_height() - height) // 2, 10)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        if self.current_account_id is not None:
            tk.Label(
                dialog,
                text="Account",
                font=(self.font_body, 21, "bold"),
                fg=self.TEXT,
                bg=self.SIDEBAR,
            ).pack(pady=(22, 6))

            tk.Label(
                dialog,
                text=self.current_username or "Account",
                font=(self.font_body, 16),
                fg=self.SECONDARY,
                bg=self.SIDEBAR,
            ).pack(pady=(0, 20))

            button = self.dialog_button(
                dialog,
                "Log out",
                lambda: self.logout_account(dialog),
            )
            button.pack(fill="x", padx=45, pady=8)

            close = self.dialog_button(dialog, "Close", dialog.destroy)
            close.pack(fill="x", padx=45, pady=8)
            return

        tk.Label(
            dialog,
            text="Log in to ELARA",
            font=(self.font_body, 21, "bold"),
            fg=self.TEXT,
            bg=self.SIDEBAR,
        ).pack(pady=(18, 6))

        tk.Label(
            dialog,
            text="Use your local ELARA account",
            font=(self.font_body, 14),
            fg=self.MUTED,
            bg=self.SIDEBAR,
        ).pack(pady=(0, 14))

        username = tk.Entry(
            dialog,
            bg=self.HOVER,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#3A3A3A",
            font=(self.font_body, 15),
        )
        username.pack(fill="x", padx=45, ipady=8, pady=5)
        username.insert(0, "Username")

        password = tk.Entry(
            dialog,
            bg=self.HOVER,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#3A3A3A",
            show="•",
            font=(self.font_body, 15),
        )
        password.pack(fill="x", padx=45, ipady=8, pady=5)
        password.insert(0, "Password")

        def clear_placeholder(entry, placeholder):
            if entry.get() == placeholder:
                entry.delete(0, "end")

        username.bind("<FocusIn>", lambda _e: clear_placeholder(username, "Username"))
        password.bind("<FocusIn>", lambda _e: clear_placeholder(password, "Password"))

        status = tk.Label(
            dialog,
            text="",
            font=(self.font_body, 13),
            fg=self.DANGER,
            bg=self.SIDEBAR,
        )
        status.pack(pady=(2, 4))

        actions = tk.Frame(dialog, bg=self.SIDEBAR)
        actions.pack(fill="x", padx=45, pady=5)

        login = self.dialog_button(
            actions,
            "Log in",
            lambda: self.login_account(username, password, status, dialog),
        )
        login.pack(side="left", fill="x", expand=True, padx=(0, 4))

        create = self.dialog_button(
            actions,
            "Create account",
            lambda: self.create_account(username, password, status),
        )
        create.pack(side="left", fill="x", expand=True, padx=(4, 0))

        close = self.dialog_button(dialog, "Close", dialog.destroy)
        close.pack(fill="x", padx=45, pady=(8, 12))
        username.focus_set()

    def dialog_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=(self.font_body, 14, "bold"),
            fg=self.TEXT,
            bg=self.HOVER,
            activeforeground=self.TEXT,
            activebackground=self.ACTIVE,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            padx=10,
            pady=8,
        )

    def get_dialog_values(self, username_entry, password_entry):
        username = username_entry.get().strip()
        password = password_entry.get()
        if username in {"", "Username"}:
            return None, None
        if password in {"", "Password"}:
            return None, None
        return username, password

    def create_account(self, username_entry, password_entry, status_label):
        username, password = self.get_dialog_values(username_entry, password_entry)
        if username is None:
            status_label.configure(text="Enter a username and password")
            return

        if len(username) < 3:
            status_label.configure(text="Username must be at least 3 characters")
            return

        if len(password) < 4:
            status_label.configure(text="Password must be at least 4 characters")
            return

        normalized = username.lower()
        for account in self.accounts:
            if str(account.get("username", "")).lower() == normalized:
                status_label.configure(text="Username already exists")
                return

        salt_hex, hash_hex = self._hash_password(password)
        account = {
            "id": uuid.uuid4().hex,
            "username": username,
            "salt": salt_hex,
            "password_hash": hash_hex,
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        self.accounts.append(account)
        self.save_accounts()
        self.current_account_id = account["id"]
        self.current_username = username
        self.save_current_account()
        self.shared_chat_store.set_active_owner(self.current_account_id)
        self.load_sessions_for_current_account()
        self.update_account_button()
        if hasattr(self, "history_inner"):
            self.refresh_chat_history()
        status_label.configure(
            text="Account created",
            fg=self.SUCCESS,
        )

    def login_account(self, username_entry, password_entry, status_label, dialog):
        username, password = self.get_dialog_values(username_entry, password_entry)
        if username is None:
            status_label.configure(text="Enter your username and password")
            return

        account = next(
            (
                item
                for item in self.accounts
                if str(item.get("username", "")).lower() == username.lower()
            ),
            None,
        )

        if account is None:
            status_label.configure(text="Account not found")
            return

        valid = self._verify_password(
            password,
            str(account.get("salt", "")),
            str(account.get("password_hash", "")),
        )

        if not valid:
            status_label.configure(text="Incorrect password")
            return

        self.current_account_id = str(account["id"])
        self.current_username = str(account["username"])
        self.save_current_account()
        self.shared_chat_store.set_active_owner(self.current_account_id)
        self.load_sessions_for_current_account()
        self.update_account_button()
        if hasattr(self, "history_inner"):
            self.refresh_chat_history()
        self.render_state()
        dialog.destroy()

    def logout_account(self, dialog):
        self.current_account_id = None
        self.current_username = None
        self.save_current_account()
        self.shared_chat_store.set_active_owner("guest")
        self.load_sessions_for_current_account()
        self.update_account_button()
        if hasattr(self, "history_inner"):
            self.refresh_chat_history()
        self.render_state()
        dialog.destroy()

    # ==========================================================
    # SHARED CHAT STORAGE
    # ==========================================================

    def _shared_owner_id(self) -> str:
        return str(self.current_account_id or "guest")

    def load_sessions(self):
        self.load_sessions_for_current_account()

    def load_sessions_for_current_account(self):
        owner = self._shared_owner_id()
        self.shared_chat_store.set_active_owner(owner)
        self.sessions = self.shared_chat_store.list_sessions(owner)

        if not self.sessions:
            fresh = self.shared_chat_store.create_session(owner)
            self.sessions = [fresh]

        active_id = self.shared_chat_store.get_active_chat(owner)
        active = None
        if active_id:
            active = self.shared_chat_store.get_session(owner, active_id)

        if active is None:
            active = self.sessions[0]
            active_id = str(active["id"])
            self.shared_chat_store.set_active_chat(owner, active_id)

        self.active_session_id = active_id
        self.messages = list(active.get("messages", []))
        self.restore_active_context_attachment()

    def save_sessions(self):
        # Sessions are persisted incrementally through add_message and chat
        # creation. Do not rewrite every chat here because the OS can update
        # the same SQLite database concurrently.
        owner = self._shared_owner_id()
        if self.active_session_id:
            self.shared_chat_store.set_active_chat(owner, self.active_session_id)

    def make_session(self):
        owner = self._shared_owner_id()
        return self.shared_chat_store.create_session(owner)

    def ensure_active_session(self):
        owner = self._shared_owner_id()
        session = self.shared_chat_store.ensure_active_session(owner)
        self.sessions = self.shared_chat_store.list_sessions(owner)
        self.active_session_id = str(session["id"])
        self.messages = list(session.get("messages", []))
        self.restore_active_context_attachment()

    def get_active_session(self):
        owner = self._shared_owner_id()
        if not self.active_session_id:
            return None
        session = self.shared_chat_store.get_session(owner, self.active_session_id)
        if session is not None:
            # Keep the in-memory session object shape expected by the UI.
            for index, item in enumerate(self.sessions):
                if str(item.get("id")) == self.active_session_id:
                    self.sessions[index] = session
                    break
            else:
                self.sessions.append(session)
            return session
        return None

    def restore_active_context_attachment(self):
        self.active_context_attachment = None

        for message in reversed(self.messages):
            if str(message.get("side", "")).strip() != "boss":
                continue
            raw_attachment = str(message.get("attachment", "")).strip()
            if not raw_attachment:
                continue
            path = Path(raw_attachment)
            if path.exists() and path.is_file():
                self.active_context_attachment = path
                return

    def sync_active_session(self):
        session = None
        for item in self.sessions:
            if str(item.get("id")) == str(self.active_session_id):
                session = item
                break
        if session is None:
            session = self.get_active_session()
        if session is None:
            return

        session["messages"] = list(self.messages)
        session["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")

        self.shared_chat_store.update_title_from_messages(
            self._shared_owner_id(),
            str(session["id"]),
            self.messages,
        )
        self.shared_chat_store.set_active_chat(
            self._shared_owner_id(),
            str(session["id"]),
        )

        latest = self.shared_chat_store.get_session(
            self._shared_owner_id(),
            str(session["id"]),
        )
        if latest is not None:
            for index, item in enumerate(self.sessions):
                if str(item.get("id")) == str(session["id"]):
                    self.sessions[index] = latest
                    break

        if hasattr(self, "history_inner"):
            self.refresh_chat_history()

    # ==========================================================
    # CHAT HISTORY
    # ==========================================================

    def refresh_chat_history(self):
        if not hasattr(self, "history_inner"):
            return

        for child in self.history_inner.winfo_children():
            child.destroy()

        sessions = [
            session
            for session in self.sessions
            if session.get("messages")
        ]

        sessions.sort(
            key=lambda item: str(item.get("updated", "")),
            reverse=True,
        )

        if not sessions:
            tk.Label(
                self.history_inner,
                text="No chats yet.",
                font=(self.font_body, 13),
                fg=self.MUTED,
                bg=self.SIDEBAR,
                anchor="w",
            ).pack(
                fill="x",
                padx=8,
                pady=8,
            )
            return

        for session in sessions:
            session_id = session.get("id")
            title = str(session.get("title", "New chat")).strip() or "New chat"
            active = session_id == self.active_session_id

            button = tk.Button(
                self.history_inner,
                text=title,
                command=lambda sid=session_id: self.open_session(sid),
                font=(self.font_body, 14),
                fg=self.TEXT,
                bg=self.ACTIVE if active else self.SIDEBAR,
                activeforeground=self.TEXT,
                activebackground=self.HOVER,
                relief="flat",
                bd=0,
                highlightthickness=0,
                cursor="hand2",
                anchor="w",
                justify="left",
                wraplength=max(self.SIDEBAR_WIDTH - 44, 120),
                padx=10,
                pady=7,
            )
            button.pack(fill="x", pady=1)

    def open_session(self, session_id):
        if self.processing:
            return

        for session in self.sessions:
            if session.get("id") != session_id:
                continue

            self.active_session_id = session_id
            self.shared_chat_store.set_active_chat(self._shared_owner_id(), str(session_id))
            fresh_session = self.shared_chat_store.get_session(self._shared_owner_id(), str(session_id)) or session
            self.messages = list(fresh_session.get("messages", []))
            self.attached_file = None
            self.restore_active_context_attachment()

            self.entry.configure(state="normal")
            self.entry.delete(0, "end")
            self.entry.insert(0, "Ask anything")
            self.entry.configure(fg=self.MUTED)
            self.entry_placeholder = True

            self.render_state()
            self.show_attachment()
            self.refresh_chat_history()
            self.focus_entry()
            return

    # ==========================================================
    # SHELL
    # ==========================================================

    def build_shell(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.sidebar = tk.Frame(
            self.root,
            bg=self.SIDEBAR,
            width=self.SIDEBAR_WIDTH,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.main = tk.Frame(self.root, bg=self.BG)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.build_sidebar()
        self.build_topbar()
        self.build_content()
        self.build_home()
        self.build_composer()

    # ==========================================================
    # SIDEBAR
    # ==========================================================

    def sidebar_button(self, text, command):
        button = tk.Button(
            self.sidebar,
            text=text,
            command=command,
            font=(self.font_body, 15),
            fg=self.TEXT,
            bg=self.SIDEBAR,
            activeforeground=self.TEXT,
            activebackground=self.HOVER,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            anchor="w",
            padx=13,
            pady=10,
        )

        button.bind("<Enter>", lambda _e: button.configure(bg=self.HOVER))
        button.bind("<Leave>", lambda _e: button.configure(bg=self.SIDEBAR))
        return button

    def build_sidebar(self):
        self.sidebar.grid_rowconfigure(0, weight=0)
        self.sidebar.grid_rowconfigure(1, weight=0)
        self.sidebar.grid_rowconfigure(2, weight=0)
        self.sidebar.grid_rowconfigure(3, weight=1)
        self.sidebar.grid_rowconfigure(4, weight=0)
        self.sidebar.grid_rowconfigure(5, weight=0)

        top = tk.Frame(self.sidebar, bg=self.SIDEBAR)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=(14, 16))

        tk.Label(
            top,
            text="ELARA",
            font=(self.font_body, 20, "bold"),
            fg=self.TEXT,
            bg=self.SIDEBAR,
        ).pack(side="left", padx=6)

        self.new_chat_button = self.sidebar_button("＋  New chat", self.new_chat)
        self.new_chat_button.grid(row=1, column=0, sticky="ew", padx=7, pady=2)

        self.images_button = self.sidebar_button("▧  Images", self.attach_file)
        self.images_button.grid(row=2, column=0, sticky="ew", padx=7, pady=2)

        self.history_frame = tk.Frame(
            self.sidebar,
            bg=self.SIDEBAR,
        )
        self.history_frame.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=7,
            pady=(12, 5),
        )
        self.history_frame.grid_rowconfigure(0, weight=1)
        self.history_frame.grid_columnconfigure(0, weight=1)

        self.history_canvas = tk.Canvas(
            self.history_frame,
            bg=self.SIDEBAR,
            highlightthickness=0,
            bd=0,
        )
        self.history_scroll = tk.Scrollbar(
            self.history_frame,
            orient="vertical",
            command=self.history_canvas.yview,
            width=8,
            relief="flat",
        )
        self.history_canvas.configure(
            yscrollcommand=self.history_scroll.set,
        )
        self.history_canvas.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        self.history_scroll.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        self.history_inner = tk.Frame(
            self.history_canvas,
            bg=self.SIDEBAR,
        )
        self.history_window = self.history_canvas.create_window(
            (0, 0),
            window=self.history_inner,
            anchor="nw",
        )
        self.history_inner.bind(
            "<Configure>",
            lambda _event: self.history_canvas.configure(
                scrollregion=self.history_canvas.bbox("all")
            ),
        )
        self.history_canvas.bind(
            "<Configure>",
            lambda event: self.history_canvas.itemconfigure(
                self.history_window,
                width=event.width,
            ),
        )
        self.history_canvas.bind(
            "<MouseWheel>",
            lambda event: self.history_canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units",
            ),
        )

        self.refresh_chat_history()

        self.status_frame = tk.Frame(self.sidebar, bg=self.SIDEBAR)
        self.status_frame.grid(row=4, column=0, sticky="ew", padx=18, pady=(2, 5))

        self.status_dot = tk.Label(
            self.status_frame,
            text="●",
            font=(self.font_body, 13),
            fg=self.PURPLE,
            bg=self.SIDEBAR,
        )
        self.status_dot.pack(side="left", padx=(0, 7))

        self.status_text = tk.Label(
            self.status_frame,
            text="ELARA ready",
            font=(self.font_body, 14),
            fg=self.SECONDARY,
            bg=self.SIDEBAR,
        )
        self.status_text.pack(side="left")

        self.account_button = self.sidebar_button("◉  Account", self.account_dialog)
        self.account_button.grid(row=5, column=0, sticky="ew", padx=7, pady=(2, 12))

    def update_account_button(self):
        if not hasattr(self, "account_button"):
            return
        label = self.current_username or "Account"
        self.account_button.configure(text=f"◉  {label}")

    # ==========================================================
    # TOP BAR
    # ==========================================================

    def build_topbar(self):
        self.topbar = tk.Frame(self.main, bg=self.BG, height=58)
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.topbar.grid_propagate(False)
        self.topbar.grid_columnconfigure(0, weight=1)
        self.topbar.grid_columnconfigure(1, weight=0)

        tk.Label(
            self.topbar,
            text="ELARA",
            font=(self.font_body, 16, "bold"),
            fg=self.TEXT,
            bg=self.BG,
        ).grid(row=0, column=0, sticky="w", padx=16)

        self.header_new_chat = tk.Button(
            self.topbar,
            text="New chat",
            command=self.new_chat,
            font=(self.font_body, 14),
            fg=self.SECONDARY,
            bg=self.BG,
            activeforeground=self.TEXT,
            activebackground=self.HOVER,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=10,
        )
        self.header_new_chat.grid(row=0, column=1, sticky="e", padx=10)

    # ==========================================================
    # CONTENT
    # ==========================================================

    def build_content(self):
        self.content = tk.Frame(self.main, bg=self.BG)
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.chat_canvas = tk.Canvas(
            self.content,
            bg=self.BG,
            highlightthickness=0,
            bd=0,
        )
        self.chat_scroll = tk.Scrollbar(
            self.content,
            orient="vertical",
            command=self.chat_canvas.yview,
            width=9,
            relief="flat",
        )
        self.chat_canvas.configure(yscrollcommand=self.chat_scroll.set)
        self.chat_canvas.grid(row=0, column=0, sticky="nsew")
        self.chat_scroll.grid(row=0, column=1, sticky="ns")

        self.chat_inner = tk.Frame(self.chat_canvas, bg=self.BG)
        self.chat_window = self.chat_canvas.create_window(
            (0, 0),
            window=self.chat_inner,
            anchor="nw",
        )

        self.chat_inner.bind(
            "<Configure>",
            lambda _e: self.chat_canvas.configure(
                scrollregion=self.chat_canvas.bbox("all")
            ),
        )
        self.chat_canvas.bind("<Configure>", self.resize_chat)
        self.chat_canvas.bind("<MouseWheel>", self.chat_mousewheel)

    def resize_chat(self, event):
        self.chat_canvas.itemconfigure(self.chat_window, width=event.width)

    def chat_mousewheel(self, event):
        self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ==========================================================
    # HOME
    # ==========================================================

    def build_home(self):
        self.home_frame = tk.Frame(self.content, bg=self.BG)

        tk.Label(
            self.home_frame,
            text="ELARA",
            font=(self.font_brand, 41, "bold"),
            fg=self.TEXT,
            bg=self.BG,
        ).pack(pady=(0, 6))

        tk.Label(
            self.home_frame,
            text="How can I help Boss?",
            font=(self.font_body, 18),
            fg=self.SECONDARY,
            bg=self.BG,
        ).pack()

    # ==========================================================
    # COMPOSER
    # ==========================================================

    def build_composer(self):
        self.composer_shell = tk.Frame(self.main, bg=self.BG, height=108)
        self.composer_shell.place_forget()
        self.composer_shell.grid_columnconfigure(0, weight=1)

        self.composer_card = tk.Frame(
            self.composer_shell,
            bg=self.COMPOSER,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            bd=0,
        )
        self.composer_card.pack(fill="x", padx=18, pady=(6, 18))

        self.composer_card.grid_columnconfigure(1, weight=1)

        self.attach_button = tk.Button(
            self.composer_card,
            text="+",
            command=self.attach_file,
            font=(self.font_body, 23),
            fg=self.SECONDARY,
            bg=self.COMPOSER,
            activeforeground=self.TEXT,
            activebackground=self.HOVER,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=11,
        )
        self.attach_button.grid(row=0, column=0, sticky="nsw")

        self.entry = tk.Entry(
            self.composer_card,
            bg=self.COMPOSER,
            fg=self.TEXT,
            disabledbackground=self.COMPOSER,
            disabledforeground=self.MUTED,
            insertbackground=self.TEXT,
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=(self.font_body, 16),
        )
        self.entry.grid(row=0, column=1, sticky="ew", ipady=10)
        self.entry.bind("<Return>", self.send_message)
        self.entry.bind("<KeyPress>", self.entry_keypress)

        self.mic_button = tk.Button(
            self.composer_card,
            text="🎤",
            command=self.start_microphone,
            font=(self.font_emoji, 18),
            fg=self.SECONDARY,
            bg=self.COMPOSER,
            activeforeground=self.TEXT,
            activebackground=self.HOVER,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=8,
        )
        self.mic_button.grid(row=0, column=2, sticky="ns")

        self.send_button = tk.Button(
            self.composer_card,
            text="↑",
            command=self.send_message,
            font=(self.font_body, 20, "bold"),
            fg=self.WHITE,
            bg=self.PURPLE,
            activeforeground=self.WHITE,
            activebackground=self.PURPLE_HOVER,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=10,
            pady=4,
        )
        self.send_button.grid(row=0, column=3, padx=(5, 7), pady=5)

        self.stop_button = tk.Button(
            self.composer_card,
            text="■",
            command=self.stop_response,
            font=(self.font_body, 16, "bold"),
            fg="#111111",
            bg="#E5E5E5",
            activeforeground="#111111",
            activebackground=self.WHITE,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=9,
            pady=4,
        )
        self.stop_button.grid(row=0, column=3, padx=(5, 7), pady=5)
        self.stop_button.grid_remove()

        self.attachment_label = tk.Label(
            self.composer_shell,
            text="",
            font=(self.font_body, 13),
            fg=self.SECONDARY,
            bg=self.BG,
            anchor="w",
        )

        self.entry.insert(0, "Ask anything")
        self.entry.configure(fg=self.MUTED)
        self.entry_placeholder = True
        self.entry.bind("<FocusIn>", self.clear_input_placeholder)
        self.entry.bind("<FocusOut>", self.restore_input_placeholder)

    def clear_input_placeholder(self, _event=None):
        if self.entry_placeholder or self.entry.get() == "Ask anything":
            self.entry.delete(0, "end")
            self.entry.configure(fg=self.TEXT)
            self.entry_placeholder = False
        return None

    def restore_input_placeholder(self, _event=None):
        if not self.processing and not self.entry.get().strip():
            self.entry.delete(0, "end")
            self.entry.insert(0, "Ask anything")
            self.entry.configure(fg=self.MUTED)
            self.entry_placeholder = True

    def entry_keypress(self, event=None):
        if self.entry_placeholder:
            self.entry.delete(0, "end")
            self.entry.configure(fg=self.TEXT)
            self.entry_placeholder = False
        return None

    def focus_entry(self):
        self.entry.focus_set()

    # ==========================================================
    # ATTACHMENT
    # ==========================================================

    def attach_file(self):
        if self.processing:
            return

        path = filedialog.askopenfilename(
            title="Add photos",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.webp"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        self.attached_file = Path(path)
        self.show_attachment()
        self.focus_entry()

    def show_attachment(self):
        if self.attached_file is None:
            self.attachment_label.place_forget()
            return

        self.attachment_label.configure(
            text=f"📎 {self.attached_file.name}"
        )
        self.attachment_label.place(
            x=45,
            y=2,
            anchor="nw",
        )

    # ==========================================================
    # STATE / RENDER
    # ==========================================================

    def render_state(self):
        self._attachment_image_refs.clear()
        for child in self.chat_inner.winfo_children():
            child.destroy()

        self.composer_shell.lift()

        if self.messages:
            self.home_mode = False
            self.home_frame.place_forget()
            self.render_messages()
            self.position_composer(chat_mode=True)
            self.root.after_idle(self.scroll_to_bottom)
            self.status_text.configure(text="ELARA ready")
            self.status_dot.configure(fg=self.PURPLE)
            return

        self.home_mode = True
        self.home_frame.place(
            relx=0.5,
            rely=0.40,
            anchor="center",
        )
        self.position_composer(chat_mode=False)
        self.status_text.configure(text="ELARA ready")
        self.status_dot.configure(fg=self.PURPLE)
        self.root.after(80, self.focus_entry)

    def position_composer(self, chat_mode=None):
        if chat_mode is None:
            chat_mode = not self.home_mode

        self.composer_shell.place_forget()
        if chat_mode:
            self.composer_shell.place(
                relx=0.5,
                rely=0.985,
                anchor="s",
                relwidth=0.76,
                height=108,
            )
        else:
            self.composer_shell.place(
                relx=0.5,
                rely=0.69,
                anchor="center",
                relwidth=0.70,
                height=108,
            )
        self.composer_shell.lift()

    def render_messages(self):
        for message in self.messages:
            self.render_message(message)

        # Reserve the same bottom area occupied by the floating composer.
        # It is intentionally invisible and only prevents the last message
        # from being hidden behind the composer.
        spacer = tk.Frame(
            self.chat_inner,
            bg=self.BG,
            height=130,
        )
        spacer.pack(fill="x", padx=0, pady=0)
        spacer.pack_propagate(False)

    def render_message(self, message):
        side = message.get("side")
        text = message.get("text", "")
        stamp = message.get("time", "")

        row = tk.Frame(self.chat_inner, bg=self.BG)
        row.pack(fill="x", padx=24, pady=12)
        row.grid_columnconfigure(0, weight=1)

        if side == "boss":
            bubble_frame = tk.Frame(
                row,
                bg=self.USER_BUBBLE,
            )
            bubble_frame.grid(row=0, column=0, sticky="e", padx=(180, 0))

            attachment = str(message.get("attachment", "")).strip()
            attachment_path = Path(attachment) if attachment else None

            if attachment_path is not None and attachment_path.exists():
                suffix = attachment_path.suffix.lower()
                if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
                    try:
                        image = Image.open(attachment_path).convert("RGB")
                        image.thumbnail((280, 210))
                        photo = ImageTk.PhotoImage(image)
                        self._attachment_image_refs.append(photo)
                        tk.Label(
                            bubble_frame,
                            image=photo,
                            bg=self.USER_BUBBLE,
                            bd=0,
                        ).pack(anchor="e", padx=10, pady=(10, 5))
                    except Exception as error:
                        print("[GUI ATTACHMENT PREVIEW ERROR]", error)
                else:
                    tk.Label(
                        bubble_frame,
                        text=f"📎 {attachment_path.name}",
                        font=(self.font_body, 14),
                        fg=self.TEXT,
                        bg=self.USER_BUBBLE,
                        anchor="w",
                        padx=10,
                        pady=3,
                    ).pack(anchor="e", pady=(9, 3))

            if text:
                tk.Label(
                    bubble_frame,
                    text=text,
                    font=(self.font_body, 15),
                    fg=self.TEXT,
                    bg=self.USER_BUBBLE,
                    justify="left",
                    anchor="w",
                    wraplength=640,
                    padx=14,
                    pady=9,
                ).pack(anchor="e")

            tk.Label(
                row,
                text=stamp,
                font=(self.font_body, 12),
                fg=self.MUTED,
                bg=self.BG,
            ).grid(row=1, column=0, sticky="e", padx=(0, 8), pady=(3, 0))
            return

        frame = tk.Frame(row, bg=self.BG)
        frame.grid(row=0, column=0, sticky="w", padx=(10, 100))

        tk.Label(
            frame,
            text="ELARA",
            font=(self.font_body, 14, "bold"),
            fg=self.TEXT,
            bg=self.BG,
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            frame,
            text=self.sanitize_elara_output(text),
            font=(self.font_body, 15),
            fg=self.TEXT,
            bg=self.BG,
            justify="left",
            anchor="w",
            wraplength=850,
        ).pack(anchor="w")

        tk.Label(
            frame,
            text=stamp,
            font=(self.font_body, 12),
            fg=self.MUTED,
            bg=self.BG,
        ).pack(anchor="w", pady=(4, 0))

    # ==========================================================
    # MESSAGE HELPERS
    # ==========================================================

    def add_message(self, side: str, text: str, attachment: Path | None = None):
        value = str(text).strip()
        if not value and attachment is None:
            return
        if side == "elara":
            value = self.sanitize_elara_output(value)

        message = {
            "side": side,
            "text": value,
            "time": time.strftime("%H:%M"),
        }
        if attachment is not None:
            message["attachment"] = str(attachment)

        self.messages.append(message)

        owner = self._shared_owner_id()
        if self.active_session_id:
            self.shared_chat_store.append_message(
                owner,
                str(self.active_session_id),
                side,
                value,
                attachment=str(attachment) if attachment is not None else None,
                stamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            )
            self.shared_chat_store.update_title_from_messages(
                owner,
                str(self.active_session_id),
                self.messages,
            )
            self.shared_chat_store.set_active_chat(owner, str(self.active_session_id))

        self.sync_active_session()
        self.render_state()

    # ==========================================================
    # SEND
    # ==========================================================

    def send_message(self, event=None):
        if self.processing:
            return "break"

        text = self.entry.get().strip()
        if self.entry_placeholder or text == "Ask anything":
            text = ""

        attached = self.attached_file
        if not text and attached is None:
            return "break"

        self.entry.delete(0, "end")
        visible = text or f"Image: {attached.name}" if attached else text
        self.add_message("boss", visible, attached)
        self.home_mode = False

        self.processing = True
        self.stop_requested = False
        request_id = uuid.uuid4().hex
        self.active_request_id = request_id
        self.set_busy(True)

        conversation = [dict(message) for message in self.messages]

        if attached is not None and attached.exists() and attached.is_file():
            self.active_context_attachment = attached

        active_context_attachment = self.active_context_attachment

        threading.Thread(
            target=self.process_message,
            args=(request_id, text, attached, conversation, active_context_attachment),
            daemon=True,
        ).start()

        return "break"

    def process_message(
        self,
        request_id: str,
        text: str,
        attached: Path | None,
        conversation: list[dict[str, Any]],
        active_context_attachment: Path | None,
    ):
        response = ""
        try:
            print("[ELARA GUI] User:", text)

            if attached is not None and attached.exists():
                response = self.process_with_attachment(
                    text,
                    attached,
                    conversation,
                )
            else:
                response = route(text, None)
                if not response:
                    if self.brain is None:
                        deadline = time.time() + 15.0
                        while self.brain is None and time.time() < deadline:
                            if self.stop_requested:
                                return
                            time.sleep(0.05)

                    if self.brain is None:
                        raise RuntimeError("OpenRouter brain did not become ready.")

                    response = self.process_with_chat_context(
                        text,
                        conversation,
                        active_context_attachment,
                    )

            response = self.sanitize_elara_output(
                response or "I did not understand that Boss."
            )

        except Exception as error:
            print("[ELARA GUI ERROR]", error)
            response = "I could not process that request Boss."

        self.root.after(
            0,
            lambda rid=request_id, value=response: self.complete_response(rid, value),
        )

    def _context_prompt(self, message: dict[str, Any]) -> str:
        side = message.get("side")
        text = str(message.get("text", "")).strip()
        attachment = str(message.get("attachment", "")).strip()

        if side == "boss" and attachment and attachment:
            try:
                name = Path(attachment).name
                placeholder = f"Image: {name}"
                if text == placeholder:
                    return ""
            except Exception:
                pass

        return text

    def _build_chat_context(
        self,
        conversation: list[dict[str, Any]],
        current_text: str,
        current_attachment: Path | None = None,
        active_context_attachment: Path | None = None,
    ) -> list[dict[str, Any]]:
        system_prompt = getattr(
            self.brain,
            "SYSTEM_PROMPT",
            "You are ELARA.",
        )

        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        history = conversation[:-1] if conversation else []
        history = history[-20:]

        selected_attachment = current_attachment
        if selected_attachment is None:
            candidate = active_context_attachment
            if candidate is not None and candidate.exists() and candidate.is_file():
                selected_attachment = candidate

        selected_attachment_resolved = (
            selected_attachment.resolve()
            if selected_attachment is not None and selected_attachment.exists()
            else None
        )

        for item in history:
            side = str(item.get("side", "")).strip()
            if side not in {"boss", "elara"}:
                continue

            role = "user" if side == "boss" else "assistant"
            item_text = self._context_prompt(item)

            # Attachment bytes are supplied separately below as active context.
            # This keeps the original attachment available even after many turns.
            if side == "boss":
                raw_attachment = str(item.get("attachment", "")).strip()
                if raw_attachment:
                    item_text = item_text or f"[Previously attached file: {Path(raw_attachment).name}]"

            if item_text:
                messages.append({"role": role, "content": item_text})

        if selected_attachment_resolved is not None:
            suffix = selected_attachment_resolved.suffix.lower()
            try:
                if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
                    mime = mimetypes.guess_type(selected_attachment_resolved.name)[0] or "image/png"
                    encoded = base64.b64encode(
                        selected_attachment_resolved.read_bytes()
                    ).decode("ascii")
                    data_url = f"data:{mime};base64,{encoded}"
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Active visual context from an earlier attachment in this chat. Use this image together with the conversation history when answering the latest request.",
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": data_url},
                                },
                            ],
                        }
                    )
                elif suffix == ".pdf":
                    encoded = base64.b64encode(
                        selected_attachment_resolved.read_bytes()
                    ).decode("ascii")
                    data_url = f"data:application/pdf;base64,{encoded}"
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Active document context from an earlier PDF attachment in this chat. Use this document together with the conversation history when answering the latest request.",
                                },
                                {
                                    "type": "file",
                                    "file": {
                                        "filename": selected_attachment_resolved.name,
                                        "file_data": data_url,
                                    },
                                },
                            ],
                        }
                    )
            except Exception as error:
                print("[ELARA ACTIVE CONTEXT ERROR]", error)

        current_content: Any = current_text.strip()

        if current_attachment is not None and current_attachment.exists():
            suffix = current_attachment.suffix.lower()

            if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
                mime = mimetypes.guess_type(current_attachment.name)[0] or "image/png"
                encoded = base64.b64encode(
                    current_attachment.read_bytes()
                ).decode("ascii")
                data_url = f"data:{mime};base64,{encoded}"
                prompt = current_text.strip() or "Analyze this image and explain what you see."
                current_content = [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url},
                    },
                ]

            elif suffix == ".pdf":
                encoded = base64.b64encode(
                    current_attachment.read_bytes()
                ).decode("ascii")
                data_url = f"data:application/pdf;base64,{encoded}"
                prompt = current_text.strip() or "Analyze this PDF and explain its contents."
                current_content = [
                    {"type": "text", "text": prompt},
                    {
                        "type": "file",
                        "file": {
                            "filename": current_attachment.name,
                            "file_data": data_url,
                        },
                    },
                ]

        if not current_content:
            current_content = "Please respond to the user's latest request."

        messages.append(
            {
                "role": "user",
                "content": current_content,
            }
        )
        return messages

    def process_with_chat_context(
        self,
        text: str,
        conversation: list[dict[str, Any]],
        active_context_attachment: Path | None = None,
    ) -> str:
        if self.brain is None or getattr(self.brain, "client", None) is None:
            raise RuntimeError("OpenRouter brain is not ready.")

        response: Any = self.brain.client.chat.completions.create(
            model=self.brain.OPENROUTER_MODEL,
            messages=self._build_chat_context(
                conversation,
                text,
                active_context_attachment=active_context_attachment,
            ),
            temperature=0.7,
            max_tokens=1000,
        )

        choices = getattr(response, "choices", None)
        if not choices:
            raise RuntimeError("OpenRouter returned no choices.")

        message = getattr(choices[0], "message", None)
        if message is None:
            raise RuntimeError("OpenRouter response has no message.")

        content = getattr(message, "content", None)
        if content is None:
            raise RuntimeError("OpenRouter returned empty content.")

        return self.sanitize_elara_output(str(content).strip())

    def complete_response(self, request_id: str, response: str):
        if request_id != self.active_request_id:
            return

        if self.stop_requested:
            self.finish_processing()
            return

        print("[ELARA GUI] ELARA:", response)
        self.add_message("elara", response)
        self.finish_processing()

    def process_with_attachment(
        self,
        text: str,
        attached: Path,
        conversation: list[dict[str, Any]],
    ) -> str:
        if self.brain is None or getattr(self.brain, "client", None) is None:
            raise RuntimeError("OpenRouter brain is not ready.")

        if not attached.exists() or not attached.is_file():
            raise FileNotFoundError(f"Attachment not found: {attached}")

        suffix = attached.suffix.lower()

        if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf"}:
            messages = self._build_chat_context(
                conversation,
                text,
                attached,
            )
            response: Any = self.brain.client.chat.completions.create(
                model=self.brain.OPENROUTER_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1200,
            )
        elif suffix in {
            ".txt", ".md", ".py", ".json", ".csv", ".log", ".yaml", ".yml",
            ".xml", ".html", ".css", ".js", ".ts", ".java", ".c", ".cpp",
            ".h", ".hpp", ".sql", ".ini", ".cfg", ".toml",
        }:
            try:
                file_text = attached.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                file_text = attached.read_text(encoding="utf-8", errors="replace")

            if len(file_text) > 120000:
                file_text = file_text[:120000] + "\n[File truncated for transmission]"

            prompt = text or f"Analyze the attached file {attached.name}."
            messages = self._build_chat_context(
                conversation,
                f"{prompt}\n\nFilename: {attached.name}\n\nFile contents:\n{file_text}",
            )
            response = self.brain.client.chat.completions.create(
                model=self.brain.OPENROUTER_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1200,
            )
        else:
            raise RuntimeError(
                f"This file type is not supported for direct AI analysis yet: {attached.suffix or attached.name}"
            )

        choices = getattr(response, "choices", None)
        if not choices:
            raise RuntimeError("OpenRouter returned no choices.")

        message = getattr(choices[0], "message", None)
        if message is None:
            raise RuntimeError("OpenRouter response has no message.")

        content = getattr(message, "content", None)
        if content is None:
            raise RuntimeError("OpenRouter returned empty content.")

        value = self.sanitize_elara_output(str(content).strip())
        if not value:
            raise RuntimeError("OpenRouter returned blank content.")
        return value

    # ==========================================================
    # BUSY / STOP
    # ==========================================================

    def set_busy(self, busy: bool):
        if busy:
            self.processing = True
            self.send_button.grid_remove()
            self.stop_button.grid(row=0, column=3, padx=(5, 7), pady=5)
            self.attach_button.configure(state="disabled")
            self.mic_button.configure(state="disabled")
            # Keep the input enabled so Boss can type the next command.
            self.entry.configure(state="normal")
            self.status_text.configure(text="ELARA thinking")
            self.status_dot.configure(fg=self.PURPLE)
            self.focus_entry()
            return

        self.processing = False
        self.stop_button.grid_remove()
        self.send_button.grid(row=0, column=3, padx=(5, 7), pady=5)
        self.attach_button.configure(state="normal")
        self.mic_button.configure(state="normal")
        self.entry.configure(state="normal")
        self.status_text.configure(text="ELARA ready")
        self.status_dot.configure(fg=self.PURPLE)

    def finish_processing(self):
        self.processing = False
        self.stop_requested = False
        self.active_request_id = None
        self.attached_file = None
        self.show_attachment()
        self.set_busy(False)
        self.restore_input_placeholder()
        self.focus_entry()

    def stop_response(self):
        if not self.processing:
            return
        self.stop_requested = True
        self.status_text.configure(text="ELARA stopped")
        self.status_dot.configure(fg=self.DANGER)

    # ==========================================================
    # MICROPHONE
    # ==========================================================

    def start_microphone(self):
        if self.listening or self.processing:
            return


        self.listening = True
        self.mic_button.configure(
            text="●",
            fg=self.DANGER,
            state="disabled",
        )
        self.status_text.configure(text="Listening")
        self.status_dot.configure(fg=self.DANGER)

        threading.Thread(
            target=self.microphone_worker,
            daemon=True,
        ).start()

    def get_speech_service(self):
        """Create SpeechService once and reuse it for all mic requests."""
        if self.speech_service is not None:
            return self.speech_service

        with self.speech_service_lock:
            if self.speech_service is None:
                from services.speech_service import SpeechService

                self.speech_service = SpeechService()
                print("[ELARA SPEECH] SpeechService initialized once.")

        return self.speech_service

    def microphone_worker(self):
        try:
            speech = self.get_speech_service()
            text = speech.listen()

            if text:
                self.root.after(
                    0,
                    lambda value=text: self.voice_received(value),
                )

        except Exception as error:
            print("[ELARA MIC ERROR]", error)

        finally:
            self.root.after(0, self.microphone_finished)

    def voice_received(self, text: str):
        self.entry.configure(state="normal")
        self.clear_input_placeholder()
        self.entry.delete(0, "end")
        self.entry.insert(0, str(text))
        self.entry.configure(fg=self.TEXT)
        self.entry_placeholder = False

        # Start processing immediately so there is no small window in
        # which a second microphone click can race the voice request.
        self.send_message()

    def microphone_finished(self):
        self.listening = False
        self.mic_button.configure(text="🎤", fg=self.SECONDARY)
        if not self.processing:
            self.mic_button.configure(state="normal")
            self.status_text.configure(text="ELARA ready")
            self.status_dot.configure(fg=self.PURPLE)

    # ==========================================================
    # NEW CHAT
    # ==========================================================

    def new_chat(self):
        if self.processing:
            self.stop_requested = True
            self.processing = False
            self.active_request_id = None

        self.sync_active_session()

        fresh = self.make_session()
        self.sessions.append(fresh)
        self.active_session_id = fresh["id"]
        self.messages = []
        self.attached_file = None
        self.active_context_attachment = None

        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, "Ask anything")
        self.entry.configure(fg=self.MUTED)
        self.entry_placeholder = True

        self.save_sessions()
        self.refresh_chat_history()
        self.render_state()
        self.show_attachment()
        self.set_busy(False)
        self.focus_entry()

    def shortcut_new_chat(self, _event=None):
        self.new_chat()
        return "break"

    # ==========================================================
    # ESCAPE
    # ==========================================================

    def escape_action(self, _event=None):
        if self.processing:
            self.stop_response()
            return "break"
        return None

    # ==========================================================
    # BRAIN
    # ==========================================================

    def initialize_brain(self):
        try:
            self.brain = BrainService()
            self.status_text.configure(text="ELARA online")
            self.status_dot.configure(fg=self.PURPLE)
        except Exception as error:
            print("[ELARA BRAIN ERROR]", error)
            self.status_text.configure(text="ELARA offline")
            self.status_dot.configure(fg=self.DANGER)

    # ==========================================================
    # SCROLL
    # ==========================================================

    def scroll_to_bottom(self):
        def move():
            try:
                self.chat_canvas.update_idletasks()
                self.chat_canvas.yview_moveto(1.0)
            except tk.TclError:
                pass

        self.root.after(10, move)
        self.root.after(60, move)

    def _widget_inside_chat(self, widget):
        current = widget
        while current is not None:
            if current == self.chat_canvas or current == self.chat_inner:
                return True
            try:
                parent_name = current.winfo_parent()
                if not parent_name:
                    break
                current = current._nametowidget(parent_name)
            except Exception:
                break
        return False

    def chat_mousewheel_global(self, event):
        try:
            widget = self.root.winfo_containing(event.x_root, event.y_root)
            if not self._widget_inside_chat(widget):
                return
            delta = int(-1 * (event.delta / 120))
            if delta:
                self.chat_canvas.yview_scroll(delta, "units")
                return "break"
        except Exception:
            pass

    def chat_scroll_up(self, _event=None):
        self.chat_canvas.yview_scroll(-3, "units")
        return "break"

    def chat_scroll_down(self, _event=None):
        self.chat_canvas.yview_scroll(3, "units")
        return "break"

    # ==========================================================
    # SHARED STORE SYNC
    # ==========================================================

    def _shared_signature(self, sessions):
        return tuple(
            (str(item.get("id", "")), str(item.get("updated", "")))
            for item in sessions
        )

    def refresh_from_shared_store(self):
        try:
            if self.processing or self.listening:
                self.root.after(1500, self.refresh_from_shared_store)
                return

            owner = self._shared_owner_id()
            latest_sessions = self.shared_chat_store.list_sessions(owner)
            active_id = self.active_session_id or self.shared_chat_store.get_active_chat(owner)
            if not active_id and latest_sessions:
                active_id = str(latest_sessions[0]["id"])

            current_sig = self._shared_signature(self.sessions)
            latest_sig = self._shared_signature(latest_sessions)

            if current_sig != latest_sig:
                self.sessions = latest_sessions

            if active_id:
                latest_active = self.shared_chat_store.get_session(owner, str(active_id))
                if latest_active is not None:
                    if (
                        str(latest_active.get("updated", ""))
                        != str((self.get_active_session() or {}).get("updated", ""))
                        or len(latest_active.get("messages", []))
                        != len(self.messages)
                    ):
                        self.active_session_id = str(active_id)
                        self.messages = list(latest_active.get("messages", []))
                        self.restore_active_context_attachment()
                        self.render_state()
                    elif self.active_session_id != str(active_id):
                        self.active_session_id = str(active_id)

            if hasattr(self, "history_inner") and current_sig != latest_sig:
                self.refresh_chat_history()
        except Exception as error:
            print("[SHARED CHAT SYNC ERROR]", error)
        finally:
            try:
                self.root.after(1500, self.refresh_from_shared_store)
            except Exception:
                pass

    # ==========================================================
    # CLOSE / RUN
    # ==========================================================

    def close(self):
        try:
            self.sync_active_session()
            self.save_current_account()
            self.root.destroy()
        except Exception:
            pass

    def run(self):
        print("[GUI] ELARA dashboard v18 online.")
        self.root.mainloop()


if __name__ == "__main__":
    app = ELARADashboard()
    app.run()
