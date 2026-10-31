#!/usr/bin/env python3
"""Terminal game layer: rendering, timing and keyboard loop."""
from __future__ import annotations
import argparse, shutil, sys, time, uuid, termios, tty
from pathlib import Path
from chorequest.executor import Executor
from chorequest.chores import FolderChore, ExpenseChore

ROOT = Path(__file__).parent; SAMPLE = ROOT / "sample_data"; RUNTIME = ROOT / "runtime"

def reset():
    RUNTIME.mkdir(exist_ok=True)
    for name in ("sandbox_folder", "expenses.csv"):
        p = RUNTIME / name
        if p.is_dir(): shutil.rmtree(p)
        elif p.exists(): p.unlink()
    shutil.copytree(SAMPLE / "messy_folder", RUNTIME / "sandbox_folder")
    shutil.copy2(SAMPLE / "expenses.csv", RUNTIME / "expenses.csv")
    print("Sandbox reset. No user files are touched.")

def confirm_real(folder: Path):
    files = [p for p in sorted(folder.iterdir()) if p.is_file()]
    print(f"\nREAL-FOLDER PREVIEW ({folder.resolve()})")
    for p in files: print(f"  {p.name}  ->  category determined during play")
    print("This will move only these direct children and is fully journaled.")
    return input("Type YES to continue: ") == "YES"

def play(kind, real_folder=None):
    if kind == "folder":
        folder = Path(real_folder).expanduser() if real_folder else RUNTIME / "sandbox_folder"
        if not folder.exists(): reset()
        if real_folder and not confirm_real(folder): print("Cancelled; nothing changed."); return
        root = folder; executor = Executor(root, uuid.uuid4().hex[:8]); chore = FolderChore(folder, executor); title = "FOLDER SORT"
        keys = "a=Documents  s=Media  d=Archive"
    else:
        path = RUNTIME / "expenses.csv"
        if not path.exists(): reset()
        root = RUNTIME; executor = Executor(root, uuid.uuid4().hex[:8]); chore = ExpenseChore(path, executor); title = "EXPENSE REVIEW"; keys = "a=approve  f=flag  c=categorize"
    print(f"\n=== CHOREQUEST: {title} ===\n{keys} | q=quit | 45 seconds\nSession: {executor.session}\n")
    print("Every key is a real operation. Translation feed:")
    deadline = time.monotonic() + 45; score = 0
    while chore.next_item() and time.monotonic() < deadline:
        item = chore.next_item(); label = item.name if hasattr(item, "name") else f"#{item['id']} {item['description']} (${item['amount']})"
        print(f"\n[{len(chore.items) if hasattr(chore,'items') else len(chore.rows)} remaining] {label}")
        if sys.stdin.isatty():
            old = termios.tcgetattr(sys.stdin); tty.setcbreak(sys.stdin.fileno())
            try: key = sys.stdin.read(1).lower()
            finally: termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)
        else:
            key = sys.stdin.read(1).lower()
        if not key:
            break
        if key == "q": break
        result = chore.apply(key)
        if result: score += 10; print(f"  TRANSLATION: {result}  (+10)")
        else: print("  Use one of the shown action keys.")
    done = not chore.next_item()
    print(f"\n{'COMPLETE' if done else 'PAUSED'} — score {score}; {0 if done else 'items'} remaining. Journal: {executor.journal}")

def rollback(latest=False, session=None):
    journals = list((RUNTIME / "journals").glob("*.jsonl")) if (RUNTIME / "journals").exists() else []
    journals += list((RUNTIME / "sandbox_folder" / "journals").glob("*.jsonl")) if (RUNTIME / "sandbox_folder" / "journals").exists() else []
    target = (journals[-1] if latest and journals else None) or ((RUNTIME / "journals" / f"{session}.jsonl") if session else None)
    if not target or not target.exists(): print("No journal found."); return
    count = Executor(target.parent.parent, target.stem).rollback()
    print(f"Rolled back {count} operations from session {target.stem}.")

def main():
    ap = argparse.ArgumentParser(description="Play cleanup chores; every action is reversible")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("reset"); f = sub.add_parser("folder"); f.add_argument("--real-folder")
    sub.add_parser("expenses"); r = sub.add_parser("rollback"); r.add_argument("--latest", action="store_true"); r.add_argument("--session")
    args = ap.parse_args()
    if args.cmd == "reset": reset()
    elif args.cmd == "folder": play("folder", args.real_folder)
    elif args.cmd == "expenses": play("expenses")
    else: rollback(args.latest, args.session)
if __name__ == "__main__": main()
