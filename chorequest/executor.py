"""Safety boundary: all filesystem/CSV changes are journaled and reversible."""
from __future__ import annotations
import csv, json, shutil
from datetime import datetime
from pathlib import Path

class Executor:
    def __init__(self, root: Path, session: str):
        self.root = root.resolve(); self.session = session
        self.journal_dir = self.root / "journals"; self.log_dir = self.root / "logs"
        self.journal_dir.mkdir(parents=True, exist_ok=True); self.log_dir.mkdir(parents=True, exist_ok=True)
        self.journal = self.journal_dir / f"{session}.jsonl"; self.log = self.log_dir / f"{session}.log"

    def _record(self, entry, message):
        entry["time"] = datetime.now().isoformat(timespec="seconds")
        with self.journal.open("a", encoding="utf-8") as f: f.write(json.dumps(entry) + "\n")
        with self.log.open("a", encoding="utf-8") as f: f.write(f"{entry['time']} | {message}\n")
        print(f"  {message}")

    def move(self, source: Path, destination: Path):
        source, destination = source.resolve(), destination.resolve()
        if not source.is_file() or self.root not in source.parents or self.root not in destination.parents:
            raise ValueError("refusing a move outside the selected sandbox/folder")
        destination.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(source), str(destination))
        self._record({"kind":"move", "source":str(source), "destination":str(destination)}, f"MOVED {source.name} -> {destination.parent.name}/{destination.name}")

    def update_expense(self, csv_path: Path, row_number: int, old: dict, new: dict):
        csv_path = csv_path.resolve()
        if self.root not in csv_path.parents: raise ValueError("refusing CSV outside selected sandbox")
        with csv_path.open(newline="", encoding="utf-8") as f: rows = list(csv.DictReader(f)); fields = rows[0].keys() if rows else new.keys()
        rows[row_number] = new
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(fields)); writer.writeheader(); writer.writerows(rows)
        self._record({"kind":"expense", "path":str(csv_path), "row":row_number, "old":old, "new":new}, f"UPDATED expense row {row_number + 1}: {old.get('description')} -> {new.get('status')}")

    def rollback(self):
        if not self.journal.exists(): return 0
        entries = [json.loads(x) for x in self.journal.read_text(encoding="utf-8").splitlines() if x]
        for e in reversed(entries):
            if e["kind"] == "move":
                src, dst = Path(e["source"]), Path(e["destination"])
                if dst.exists(): src.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(dst), str(src))
            else:
                path = Path(e["path"]); rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
                rows[e["row"]] = e["old"]
                with path.open("w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        self.log.open("a", encoding="utf-8").write(f"{datetime.now().isoformat(timespec='seconds')} | ROLLBACK {len(entries)} operations\n")
        return len(entries)
