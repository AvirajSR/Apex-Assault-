# ChoreQuest

ChoreQuest is a terminal game where each keypress performs a real, reversible cleanup operation. It is intentionally a small Python (3.10+) standard-library prototype for a hackathon demo.

## Run

```bash
python3 chorequest.py reset
python3 chorequest.py folder
python3 chorequest.py expenses
python3 chorequest.py rollback --latest
python3 chorequest_gui.py
PORT=5002 python3 contra_game.py
PORT=5003 python3 contra_game_pro.py
```

The Tkinter command opens a desktop UI with clickable chore actions, live progress bars, translation history, and an Undo button. It uses the same executor as the terminal version.

`contra_game.py` is the original run-and-gun variant: move, jump, choose a cleanup weapon, and shoot incoming file targets. A successful hit executes the corresponding real file move; missed targets cost lives. It uses no Contra assets or copied characters.

`contra_game_pro.py` is the polished platformer build with opponent health, files-left tracking, varied enemy fire patterns, scrolling depth layers, jumpable obstacles, pickups, and three weapon behaviors: machine gun, sniper, and bazooka.

`reset` restores the reproducible mock folder and expense CSV under `runtime/`. The default mode never touches anything outside that sandbox. Folder mode shows one file at a time: `a` = Documents, `s` = Media, `d` = Archive, `q` = quit. Expense mode uses `a` = approve, `f` = flag, `c` = categorize, and `q` = quit. Each action is printed as a translation such as `A → moved invoice.pdf to Documents` and updates the real progress meter.

To work on a real folder, use `python3 chorequest.py folder --real-folder /path/to/folder`. The program prints every planned move and asks for an exact `YES` confirmation before changing anything. Only files directly in that folder are considered, and all moves are journaled.

Rollback reverses every operation in the latest session (or pass `--session SESSION_ID`). Journals and human-readable logs live in `runtime/journals/` and `runtime/logs/`.

## Architecture

`chorequest.py` is the game layer (timing, terminal rendering, scoring). `chorequest/mapping.py` translates keys into domain actions. `chorequest/executor.py` is the safety boundary: it performs moves/CSV updates, writes a reversible journal, and rolls it back. `chorequest/chores.py` implements the two chore adapters behind the same `next_item/apply` shape.

## 60–90 second demo

Run `python3 chorequest.py reset`, then `python3 chorequest.py folder`. Press `a`, `s`, or `d` for each displayed filename (the extension hint makes the intended category obvious). Pause on the translation lines to show that points correspond to actual moves; finish the 10-file meter and show the created category folders. Run `python3 chorequest.py rollback --latest` to demonstrate one-step undo. For the second slice, run `python3 chorequest.py expenses` and press `a`, `f`, or `c` for a few rows.
