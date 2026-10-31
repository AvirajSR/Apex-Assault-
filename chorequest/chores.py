"""Chore adapters: each exposes pending items and applies a mapped action."""
import csv
from pathlib import Path
from .mapping import folder_action, expense_action

class FolderChore:
    def __init__(self, folder: Path, executor):
        self.folder, self.executor = folder, executor
        self.items = [p for p in sorted(folder.iterdir()) if p.is_file()]
    def next_item(self): return self.items[0] if self.items else None
    def apply(self, key):
        item = self.next_item(); category = folder_action(key)
        if not item or not category: return None
        self.items.pop(0); dest = self.folder / category / item.name
        self.executor.move(item, dest); return f"{key.upper()} → moved {item.name} to {category}/"

class ExpenseChore:
    def __init__(self, path: Path, executor):
        self.path, self.executor = path, executor
        with path.open(newline="", encoding="utf-8") as f: self.rows = list(csv.DictReader(f))
    def next_item(self): return self.rows[0] if self.rows else None
    def apply(self, key):
        row = self.next_item(); status = expense_action(key)
        if not row or not status: return None
        old = dict(row); row["status"] = status; self.rows.pop(0)
        self.executor.update_expense(self.path, 0, old, row)
        return f"{key.upper()} → {row['description']} marked {status}"
