"""Action-mapping layer: game keys become explicit domain operations."""

FOLDER_KEYS = {"a": "Documents", "s": "Media", "d": "Archive"}
EXPENSE_KEYS = {"a": "approved", "f": "flagged", "c": "categorized"}

def folder_action(key):
    return FOLDER_KEYS.get(key.lower())

def expense_action(key):
    return EXPENSE_KEYS.get(key.lower())
