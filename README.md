# RILEM TC MWP — Research Codebase

> This repository contains analysis tools developed for the **RILEM Technical
> Committee on Wave Propagation in Pavements (TC MWP)**.
>
> The code was built collaboratively with an AI assistant.
> You do not need to be a programmer to contribute — read the methodology section below.

---

## Repository contents

```
/
├── README.md                  ← this file
│
├── biblio_local/              ← bibliometric analysis of the DOI_MWP corpus
│   ├── README.md              ← how to use this module
│   ├── run_local.py           ← the only file you need to run
│   ├── AI_tables/             ← classification tables — open in Excel to correct
│   └── biblio_output/         ← example figures and report
│
└── [more modules to come]/
```

Each module has its own `README.md` — start there for usage instructions.

---

## Methodology — AI-assisted iterative development

### The idea in one sentence

> A human researcher describes what they need in plain language;
> an AI assistant writes, tests, and documents the code;
> every change is recorded in a `corrections.md` file that keeps the full history.

### How a work session unfolds

```
  ┌──────────────────────────────────────────────────────────────┐
  │                                                              │
  │  1. Researcher describes a need or a problem                 │
  │        "Add a chart showing citations by year"               │
  │        "The publisher detection is wrong for MDPI"           │
  │                          ↓                                   │
  │  2. AI writes the code and runs automated tests              │
  │                          ↓                                   │
  │  3. Researcher reviews the result                            │
  │                          ↓                                   │
  │  4. AI documents the change in corrections.md                │
  │        · date and time                                       │
  │        · what changed, with before / after code              │
  │        · why it changed                                       │
  │        · test results                                        │
  │                          ↓                                   │
  │  5. Researcher commits and pushes to GitHub                  │
  │     OR asks for a correction → back to step 1                │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
```

### The role of `corrections.md`

Each module contains a `corrections.md` file — a **living development journal**
where every session is recorded with a date, a reason, and the test results.

It serves three purposes:

- **Audit trail** — every decision can be traced back to its reason.
- **Reproducibility** — anyone can follow the history and understand how the code evolved.
- **Continuity** — after a pause of days or weeks, the AI can read `corrections.md`
  and immediately resume work without losing context.

A session entry looks like this:

```markdown
## Session 12 — Fix publisher inference for MDPI journals
*2026-06-23 11:20*

### C-25 · What changed and why
The `AI_table_publisher_doi.csv` was missing the prefix `10.3390/` for MDPI.
Added it. Tests: 8/8 pass.
```

> ⚠️ **Never delete previous entries from `corrections.md`.**
> The full history is what makes this approach work.

### Starting a session with an AI agent

Give your AI agent **two documents** at the start of every session:

1. **The `README.md`** of the module you want to modify
   → tells the AI what the project does and what each file contains.
2. **The `corrections.md`** of that module
   → tells the AI everything that was already changed and why.

Then simply describe what you want:

> *"Run all tests and fix any failures."*
> *"Add a new figure showing citation counts per year."*
> *"The co-author network is too dense — reduce it to the top 20 nodes."*

The AI will write the changes, run the tests, and ask you to review before committing.

### Handing the project to someone else

If another person — or another AI agent — takes over a module:

1. Give them the module's `README.md` and `corrections.md`.
2. They **append** their new session to `corrections.md` — they never overwrite
   existing sessions.
3. They commit and push when done.

That is all. The methodology is self-documenting.

### Closing a session

Once the AI has made and tested the changes, save them to GitHub:

- **With GitHub Desktop** → see the next section (no command line needed).
- **With the terminal** → `git add .` → `git commit -m "Session N — …"` → `git push`.

---

## Saving your work with Git

**Git** is the system that tracks every change made to the files in this repository.
Think of it as a save button that also keeps a complete history of all previous versions.

You can use Git in two ways. The result is identical — choose what feels easier:

| | GitHub Desktop | Command line |
|---|---|---|
| Who it suits | Anyone — no terminal needed | Users comfortable with text commands |
| How to get it | [desktop.github.com](https://desktop.github.com) — free | Built into Mac/Linux; [git-scm.com](https://git-scm.com) for Windows |

---

### Option A — GitHub Desktop

👉 **Download:** [desktop.github.com](https://desktop.github.com) — free, Windows and Mac.

**First-time setup**

1. Install the application and sign in with your GitHub account.
2. **File → Clone repository** → paste the repository address → choose a folder on your computer.

**Every session — four steps**

| Step | What you do in GitHub Desktop |
|------|-------------------------------|
| **1. Get updates** | Click **Fetch origin**, then **Pull origin** |
| **2. Edit files** | Work in your usual applications (VS Code, Excel, Notepad…) |
| **3. Save a snapshot** | Tick the changed files on the left panel → write a short description in **Summary** → click **Commit to main** |
| **4. Send to GitHub** | Click **Push origin** (top-right button) |

For branches (working on a new feature without touching the stable version):
**Branch → New branch** to create one, **Branch → Merge into current branch** to merge it back.

---

### Option B — Terminal (command line)

Open **Terminal** (Mac/Linux) or **Command Prompt** (Windows).

**First-time setup**

```bash
git clone https://github.com/<username>/<repo>.git
cd <repo>
```

**Every session**

```bash
git pull                            # get the latest version from GitHub
git status                          # see which files changed
git add .                           # stage all changes
git commit -m "Session N — …"      # save a snapshot with a description
git push                            # send to GitHub
```

**Working on a new feature without touching `main`**

```bash
git checkout -b feature/new-chart   # create a new branch and switch to it
# … make changes, commit …
git checkout main                   # switch back to the stable version
git merge feature/new-chart         # bring the changes in
git branch -d feature/new-chart     # tidy up
```

**If something goes wrong**

```bash
git log --oneline                   # see the full history of commits
git checkout -- <filename>          # discard unsaved changes to one file
git reset HEAD~1                    # undo the last commit (your edits are kept)
```

**Recommended branch names**

| Branch | Use for |
|--------|---------|
| `main` | Stable, working code only |
| `dev` | Testing new features before merging to `main` |
| `feature/<name>` | A new analysis or figure |
| `fix/<name>` | Correcting a bug |

---

## Conventions

These rules apply to all modules in this repository and keep the codebase
consistent and easy to maintain.

**File names**

| Pattern | Role |
|---------|------|
| `run_*.py` | Entry point — this is what you run |
| `main.py` | Shared utilities — do not edit |
| `AI_table_*.csv` | AI-generated lookup table — check and correct in Excel |
| `corrections.md` | Development journal — append only, never delete |

**Code rules**

- No `print()` statements in library files — all output goes to files.
- All colours, font sizes and chart options live in `run_*.py` — never inside libraries.
- Tests must pass before every commit.

---

## Licence

RILEM TC MWP — free to use for all members of the TC group.
