"""
Tkinter-based clipboard bridge for headless OS clipboard operations.
"""

import threading
import tkinter as tk
from typing import Optional

_clipboard_lock = threading.Lock()
_shared_root: Optional[tk.Tk] = None


def _get_or_create_root() -> tk.Tk:
    """Returns a persistent headless Tk root instance."""
    global _shared_root
    if _shared_root is None:
        _shared_root = tk.Tk()
        _shared_root.withdraw()
    return _shared_root


def copy_to_clipboard(text: str) -> bool:
    """
    Copies the specified text to the system clipboard using Tkinter.
    Returns True if successful, False otherwise.
    """
    with _clipboard_lock:
        try:
            root = _get_or_create_root()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            return True
        except Exception:
            try:
                # Re-initialize in case root was invalidated
                fallback_root = tk.Tk()
                fallback_root.withdraw()
                fallback_root.clipboard_clear()
                fallback_root.clipboard_append(text)
                fallback_root.update()
                fallback_root.destroy()
                return True
            except Exception as ex:
                print(f"[ClipboardHelper] Error copying to clipboard: {ex}")
                return False


def get_clipboard_text() -> str:
    """Reads current string content from clipboard using Tkinter."""
    with _clipboard_lock:
        try:
            root = _get_or_create_root()
            return root.clipboard_get()
        except Exception:
            return ""
