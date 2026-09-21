"""
ELARA OCR Command

Reads meaningful main content from the current screen.

OCR is completely local.
No OpenRouter or cloud AI is used.
"""

import re
from collections import defaultdict

from vision.screen import screen_capture
from vision.ocr import ocr


# =========================================================
# COMMAND TRIGGERS
# =========================================================

TRIGGERS = [
    "read the text on my screen",
    "read text on my screen",
    "read my screen",
    "read screen",
    "screen read",
    "screen text",
    "what does my screen say",
    "what is written on my screen",
    "read what is on my screen",
    "read this screen",

    "screen ka text padho",
    "screen ka text padh",
    "screen par kya likha hai",
    "screen pe kya likha hai",
    "screen par likha hua padho",
    "screen pe likha hua padho",
    "screen ka text batao",
    "screen ka text btao",
    "screen pe kya hai",
    "screen pado",
]


# =========================================================
# COMMAND DETECTION
# =========================================================

def is_ocr_command(text):

    if not text:
        return False

    text = text.lower().strip()

    for trigger in TRIGGERS:

        if trigger in text:
            return True

    return False


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_line(text):

    if not text:
        return ""

    text = text.strip()

    # Remove OCR quotation artifacts from
    # the beginning of a line.
    text = re.sub(
        r"^[‘’“”\"']+",
        "",
        text
    )

    # Remove OCR quotation artifacts from
    # the end of a line.
    text = re.sub(
        r"[‘’“”\"']+$",
        "",
        text
    )

    # Normalize whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# URL DETECTION
# =========================================================

def contains_url(text):

    if not text:
        return False

    patterns = [
        r"https?://",
        r"www\.",
        r"\.com\b",
        r"\.net\b",
        r"\.org\b",
        r"\.in\b",
        r"\.io\b",
        r"\.ai\b",
        r"google\.com",
    ]

    for pattern in patterns:

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            return True

    return False


# =========================================================
# EMAIL DETECTION
# =========================================================

def contains_email(text):

    if not text:
        return False

    return bool(
        re.search(
            r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b",
            text
        )
    )


# =========================================================
# BROWSER TEXT DETECTION
# =========================================================

def looks_like_browser_text(text):

    if not text:
        return False

    lower = text.lower().strip()

    patterns = [
        r"^google\.com",
        r"^search\?",
        r"^search\s",
        r"^https?://",
        r"^www\.",
        r"google search",
        r"googleseare",
        r"verify that it's you",
        r"verify that its you",
    ]

    for pattern in patterns:

        if re.search(
            pattern,
            lower
        ):
            return True

    return False


# =========================================================
# FOOTER DETECTION
# =========================================================

def looks_like_footer(text):

    if not text:
        return False

    lower = text.lower().strip()

    footer_patterns = [
        "ai can make mistakes",
        "double-check responses",
        "double check responses",
        "activate windows",
        "go to settings to activate windows",
        "activate wind",
        "windows.",
        "activate wind windows",
        "wind",
    ]

    for pattern in footer_patterns:

        if pattern in lower:
            return True

    return False


# =========================================================
# CODE DETECTION
# =========================================================

def looks_like_code(text):

    if not text:
        return False

    lower = text.lower().strip()

    patterns = [
        r"^\s*def\s+\w+",
        r"^\s*class\s+\w+",
        r"^\s*import\s+\w+",
        r"^\s*from\s+\w+",
        r"^\s*return\b",
        r"^\s*if\s+.+:",
        r"^\s*elif\s+.+:",
        r"^\s*else\s*:",
        r"^\s*for\s+.+\s+in\s+",
        r"^\s*while\s+.+:",
        r"^\s*try\s*:",
        r"^\s*except\b",
        r"^\s*print\s*\(",
        r"^\s*raise\b",
        r"^\s*with\s+.+:",
        r"^\s*async\s+def",
    ]

    for pattern in patterns:

        if re.search(
            pattern,
            lower
        ):
            return True

    error_words = [
        "traceback",
        "error code:",
        "rate limit exceeded",
        "ratelimiterror",
        "filenotfounderror",
        "modulenotfounderror",
        "tesseractnotfounderror",
        "permissionerror",
        "syntaxerror",
        "nameerror",
        "typeerror",
        "valueerror",
        "attributeerror",
    ]

    for word in error_words:

        if word in lower:
            return True

    return False


# =========================================================
# PATH DETECTION
# =========================================================

def looks_like_path(text):

    if not text:
        return False

    patterns = [
        r"^[A-Za-z]:\\",
        r"^[A-Za-z]:/",
        r"^/home/",
        r"^/usr/",
        r"^/var/",
        r"^/opt/",
        r"^\\\\",
    ]

    for pattern in patterns:

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            return True

    return False


# =========================================================
# TERMINAL DETECTION
# =========================================================

def looks_like_terminal(text):

    if not text:
        return False

    lower = text.lower().strip()

    patterns = [
        r"^PS [A-Za-z]:\\",
        r"^C:\\.*>",
        r"^C:/.*>",
        r"^\$ ",
        r"^>>>",
        r"^\(.+\)\s*PS ",
    ]

    for pattern in patterns:

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            return True

    terminal_words = [
        "rate limit exceeded",
        "traceback",
        "error code:",
        "rate-limit",
        "ratelimiterror",
        "filenotfounderror",
        "tesseractnotfounderror",
        "modulenotfounderror",
        "permissionerror",
    ]

    for word in terminal_words:

        if word in lower:
            return True

    return False


# =========================================================
# UI DETECTION
# =========================================================

UI_TEXT = {
    "new tab",
    "ask gemini",
    "sign in",
    "log in",
    "search",
    "share",
    "library",
    "projects",
    "recents",
    "plugins",
    "codex",
    "openai",
    "free",
    "settings",
    "home",
    "menu",
    "close",
    "cancel",
    "submit",
    "send",
    "file",
    "edit",
    "selection",
    "view",
    "go",
    "run",
    "debug",
    "terminal",
    "output",
    "problems",
    "ports",
    "explorer",
}


def looks_like_ui(text):

    if not text:
        return True

    lower = text.lower().strip()

    if lower in UI_TEXT:
        return True

    words = lower.split()

    if len(words) <= 3:

        matches = 0

        for word in words:

            if word in UI_TEXT:
                matches += 1

        if matches == len(words):
            return True

    return False


# =========================================================
# GARBAGE DETECTION
# =========================================================

def looks_like_garbage(text):

    if not text:
        return True

    readable = re.sub(
        r"[^A-Za-z0-9\u0900-\u097F]",
        "",
        text
    )

    if len(readable) < 3:
        return True

    symbol_count = len(
        re.findall(
            r"[^\w\s]",
            text,
            flags=re.UNICODE
        )
    )

    if len(text) > 0:

        symbol_ratio = (
            symbol_count
            / len(text)
        )

        if symbol_ratio > 0.45:
            return True

    words = text.split()

    # A single extremely long OCR token is
    # usually a URL, code or OCR corruption.
    if len(words) == 1:

        if len(words[0]) > 40:
            return True

    return False


# =========================================================
# GROUP OCR WORDS INTO LINES
# =========================================================

def group_words_into_lines(data):

    groups = defaultdict(list)

    for item in data:

        key = (
            item["block_num"],
            item["par_num"],
            item["line_num"]
        )

        groups[key].append(item)

    lines = []

    for items in groups.values():

        items.sort(
            key=lambda item: item["left"]
        )

        text = " ".join(
            item["text"]
            for item in items
        )

        text = normalize_line(
            text
        )

        if not text:
            continue

        left = min(
            item["left"]
            for item in items
        )

        top = min(
            item["top"]
            for item in items
        )

        right = max(
            item["left"]
            + item["width"]
            for item in items
        )

        bottom = max(
            item["top"]
            + item["height"]
            for item in items
        )

        confidence_values = [
            item["confidence"]
            for item in items
            if item["confidence"] >= 0
        ]

        if confidence_values:

            confidence = (
                sum(confidence_values)
                / len(confidence_values)
            )

        else:

            confidence = 0

        lines.append(
            {
                "text": text,
                "left": left,
                "top": top,
                "right": right,
                "bottom": bottom,
                "width": right - left,
                "height": bottom - top,
                "confidence": confidence,
            }
        )

    lines.sort(
        key=lambda item: (
            item["top"],
            item["left"]
        )
    )

    return lines


# =========================================================
# MAIN CONTENT FILTER
# =========================================================

def filter_main_content(data):

    lines = group_words_into_lines(
        data
    )

    selected = []

    for item in lines:

        text = item["text"]

        # ---------------------------------------------
        # Browser / URL
        # ---------------------------------------------

        if contains_url(text):
            continue

        if contains_email(text):
            continue

        if looks_like_browser_text(text):
            continue

        # ---------------------------------------------
        # Footer
        # ---------------------------------------------

        if looks_like_footer(text):
            continue

        # ---------------------------------------------
        # UI
        # ---------------------------------------------

        if looks_like_ui(text):
            continue

        # ---------------------------------------------
        # Code / terminal / paths
        # ---------------------------------------------

        if looks_like_path(text):
            continue

        if looks_like_terminal(text):
            continue

        if looks_like_code(text):
            continue

        # ---------------------------------------------
        # Random symbols / OCR garbage
        # ---------------------------------------------

        if looks_like_garbage(text):
            continue

        # ---------------------------------------------
        # Very low confidence short fragments
        # ---------------------------------------------

        if (
            item["confidence"] < 20
            and len(text) < 12
        ):
            continue

        selected.append(item)

    return selected


# =========================================================
# BUILD FINAL READABLE TEXT
# =========================================================

def build_readable_text(items):

    if not items:
        return ""

    final_lines = []

    seen = set()

    for item in items:

        line = normalize_line(
            item["text"]
        )

        if not line:
            continue

        key = line.lower()

        if key in seen:
            continue

        seen.add(key)

        final_lines.append(line)

    return "\n".join(
        final_lines
    ).strip()


# =========================================================
# MAIN OCR HANDLER
# =========================================================

def handle_ocr(text, speech=None):

    if not text:
        return None

    if not is_ocr_command(text):
        return None

    try:

        # -------------------------------------------------
        # STEP 1
        # -------------------------------------------------

        print()
        print(
            "[OCR] Starting screen reading..."
        )
        print()

        if speech:
            speech.speak(
                "Reading the screen Boss."
            )

        # -------------------------------------------------
        # STEP 2
        # -------------------------------------------------

        print()
        print(
            "[OCR] Taking screenshot..."
        )
        print()

        if speech:
            speech.speak(
                "Taking screenshot Boss."
            )

        screenshot_path = (
            screen_capture.capture()
        )

        print(
            "[OCR] Screenshot:",
            screenshot_path
        )

        # -------------------------------------------------
        # SCREEN SIZE
        # -------------------------------------------------

        image = (
            screen_capture.capture_image()
        )

        screen_width, screen_height = (
            image.size
        )

        print(
            "[OCR] Screen size:",
            screen_width,
            "x",
            screen_height
        )

        # -------------------------------------------------
        # STEP 3
        # -------------------------------------------------

        print()
        print(
            "[OCR] Reading visible text..."
        )
        print()

        if speech:
            speech.speak(
                "Reading visible text Boss."
            )

        # -------------------------------------------------
        # MAIN WEBPAGE REGION
        # -------------------------------------------------

        crop_left = int(
            screen_width * 0.055
        )

        crop_top = int(
            screen_height * 0.115
        )

        crop_right = int(
            screen_width * 0.985
        )

        crop_bottom = int(
            screen_height * 0.90
        )

        print(
            "[OCR] Content region:",
            crop_left,
            crop_top,
            crop_right,
            crop_bottom
        )

        # -------------------------------------------------
        # OCR ONLY MAIN REGION
        # -------------------------------------------------

        ocr_data = ocr.read_region(
            screenshot_path,
            crop_left,
            crop_top,
            crop_right,
            crop_bottom
        )

        if not ocr_data:

            print(
                "[OCR] No text detected."
            )

            return (
                "I could not find any readable "
                "text on the screen Boss."
            )

        # -------------------------------------------------
        # STEP 4
        # -------------------------------------------------

        print()
        print(
            "[OCR] Filtering main content..."
        )
        print()

        if speech:
            speech.speak(
                "Filtering the main content Boss."
            )

        main_content = (
            filter_main_content(
                ocr_data
            )
        )

        # -------------------------------------------------
        # STEP 5
        # -------------------------------------------------

        readable_text = (
            build_readable_text(
                main_content
            )
        )

        if not readable_text:

            print()
            print(
                "[OCR] No meaningful content detected."
            )
            print()

            return (
                "I could not find any meaningful "
                "text on the screen Boss."
            )

        # -------------------------------------------------
        # FINAL RESULT
        # -------------------------------------------------

        print()
        print(
            "[OCR] Final readable content:"
        )
        print()

        print(
            readable_text
        )

        print()

        return (
            "The readable content on the screen is: "
            + readable_text
        )

    except Exception as e:

        print()
        print(
            "[OCR ERROR]"
        )

        print(
            "Error Type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )

        print()

        return (
            "I was unable to read the screen right now Boss."
        )