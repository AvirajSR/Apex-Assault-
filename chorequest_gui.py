#!/usr/bin/env python3
"""Tkinter UI over the same chore/executor architecture."""
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import uuid
from chorequest.executor import Executor
from chorequest.chores import FolderChore, ExpenseChore
import chorequest.chores as chores

ROOT = Path(__file__).parent; RUNTIME = ROOT / "runtime"

class ChoreQuestUI:
    def __init__(self, root):
        self.root = root; root.title("ChoreQuest — Play your productivity"); root.geometry("760x560"); self.session = None
        style = ttk.Style(); style.theme_use("clam"); style.configure("TButton", padding=8)
        head = tk.Frame(root, bg="#101827"); head.pack(fill="x", padx=24, pady=16)
        tk.Label(head, text="CHOREQUEST", fg="#7dd3fc", bg="#101827", font=("Helvetica", 22, "bold")).pack(anchor="w")
        tk.Label(head, text="Play a fast game. Get a real digital chore done.", fg="#cbd5e1", bg="#101827").pack(anchor="w")
        self.tabs = ttk.Notebook(root); self.tabs.pack(fill="both", expand=True, padx=20, pady=8)
        self.folder_tab = self.make_tab("Folder Sort", "A = Documents    S = Media    D = Archive")
        self.expense_tab = self.make_tab("Expense Review", "A = Approve    F = Flag    C = Categorize")
        self.setup_folder(); self.setup_expenses()

    def make_tab(self, title, helptext):
        frame = tk.Frame(self.tabs, bg="#172235"); self.tabs.add(frame, text=title)
        tk.Label(frame, text=helptext, fg="#cbd5e1", bg="#172235", font=("Helvetica", 11)).pack(pady=14); return frame

    def widgets(self, frame, buttons):
        card = tk.Frame(frame, bg="#22304a"); card.pack(fill="x", padx=28, pady=8)
        item = tk.Label(card, text="", fg="white", bg="#22304a", font=("Helvetica", 18, "bold")); item.pack(pady=12)
        bar = ttk.Progressbar(card, length=520, mode="determinate"); bar.pack(pady=4)
        status = tk.Label(frame, text="", fg="#7dd3fc", bg="#172235"); status.pack(pady=4)
        actions = tk.Frame(frame, bg="#172235"); actions.pack(pady=6)
        for label, command in buttons: ttk.Button(actions, text=label, command=command, width=17).pack(side="left", padx=4)
        history = tk.Text(frame, height=12, bg="#0f172a", fg="#dbeafe", relief="flat", state="disabled"); history.pack(fill="both", expand=True, padx=28, pady=10)
        return item, bar, status, history

    def setup_folder(self):
        self.fitem, self.fbar, self.fstatus, self.fhistory = self.widgets(self.folder_tab, [("Documents (A)", lambda: self.folder_action("a")), ("Media (S)", lambda: self.folder_action("s")), ("Archive (D)", lambda: self.folder_action("d")), ("Undo", self.rollback)])
        self.reset_folder()

    def setup_expenses(self):
        self.eitem, self.ebar, self.estatus, self.ehistory = self.widgets(self.expense_tab, [("Approve (A)", lambda: self.expense_action("a")), ("Flag (F)", lambda: self.expense_action("f")), ("Categorize (C)", lambda: self.expense_action("c")), ("Undo", self.rollback)])
        self.reset_expenses()

    def log(self, box, text):
        box.configure(state="normal"); box.insert("end", text + "\n"); box.see("end"); box.configure(state="disabled")

    def reset_folder(self):
        from chorequest import reset
        reset(); self.folder_session = uuid.uuid4().hex[:8]; self.folder = FolderChore(RUNTIME / "sandbox_folder", Executor(RUNTIME / "sandbox_folder", self.folder_session)); self.refresh_folder(); self.log(self.fhistory, "Sandbox reset — ready to play")

    def reset_expenses(self):
        from chorequest import reset
        reset(); self.expense_session = uuid.uuid4().hex[:8]; self.expense = ExpenseChore(RUNTIME / "expenses.csv", Executor(RUNTIME, self.expense_session)); self.refresh_expense(); self.log(self.ehistory, "Sandbox reset — ready to play")

    def refresh_folder(self):
        n = len(self.folder.items); self.fbar["maximum"] = 8; self.fbar["value"] = 8 - n; item = self.folder.next_item(); self.fitem.config(text=item.name if item else "Complete!"); self.fstatus.config(text=f"{n} files remaining • session {self.session}")

    def refresh_expense(self):
        n = len(self.expense.rows); self.ebar["maximum"] = 5; self.ebar["value"] = 5 - n; row = self.expense.next_item(); self.eitem.config(text=f"{row['description']} · ${row['amount']}" if row else "Complete!"); self.estatus.config(text=f"{n} expenses remaining")

    def folder_action(self, key):
        if self.folder.next_item() and (result := self.folder.apply(key)): self.log(self.fhistory, "✓ " + result); self.refresh_folder()

    def expense_action(self, key):
        if self.expense.next_item() and (result := self.expense.apply(key)): self.log(self.ehistory, "✓ " + result); self.refresh_expense()

    def rollback(self):
        if messagebox.askyesno("Undo changes?", "Reverse every operation in this session?"):
            folder_active = self.tabs.index(self.tabs.select()) == 0
            base, session = ((RUNTIME / "sandbox_folder", self.folder_session) if folder_active else (RUNTIME, self.expense_session))
            count = Executor(base, session).rollback(); messagebox.showinfo("Rollback complete", f"Reversed {count} operation(s). Reset to play again.")

if __name__ == "__main__":
    app = tk.Tk(); ChoreQuestUI(app); app.mainloop()
