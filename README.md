# FFXIV Mitigation & Mechanic-Solving Agent

A **knowledge layer** for analyzing [FFLogs](https://www.fflogs.com/) reports as an FFXIV
mitigation & mechanic-solving analyst. You point it at a raid-night report and it helps you
diagnose *why a pull went wrong* (who died, to what, was the mit there) and *what to do next*
(forward mit plans) — grounded in the actual log data, not vibes.

It's built for **prog**: figuring out unsolved fights, attributing deaths to mechanics vs. mit
gaps, and reasoning about cooldown economy across a fight timeline.

> ⚠️ **This is a personal hobby project, shared for fun.** The FFXIV knowledge in `knowledge/`
> is authored by Claude and curated by hand — it is incomplete and sometimes wrong. Treat it as
> a living document, not ground truth. Corrections welcome (see [Contributing](#contributing)).

---

## What's actually in here

The product is the `knowledge/` directory — prose that gets loaded as an LLM system prompt —
plus a small stdlib-only Python script that fetches and decodes FFLogs data into a readable form.
There's no app to deploy and no UI.

```
knowledge/
├── AGENT.md            # the analysis agent's persona + reasoning discipline (loaded first)
├── fundamentals.md     # cross-cutting rules of the game (vulns, Damage Down, the 8-player budget, schools)
├── primitives.md       # mechanic vocabulary (tankbusters, towers, gazes, stacks, …)
├── jobs.md             # every job's mitigation/defensive toolkit, tagged for querying
└── fights/
    └── dancing-mad-ultimate.md   # an observed mechanic catalog (NOT a mit plan)
scripts/
└── fetch_fight.py      # FFLogs GraphQL fetcher → paste-ready decoded text
.claude/
└── commands/ffxivanalyze.md      # the /ffxivanalyze slash command for Claude Code
```

Project state, decisions, and roadmap live in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md); the
glossary is [CONTEXT.md](CONTEXT.md); authoring guidance for contributors is [CLAUDE.md](CLAUDE.md).
A reusable layout for comp-agnostic mit-plan sheets (planning mode) is in
[docs/mit-sheet-conventions.md](docs/mit-sheet-conventions.md).

---

## The two agents (important mental model)

This repo involves **two distinct agents** — keep them separate:

- **Analysis agent** — runs on [claude.ai](https://claude.ai) or in Claude Code. It *consumes*
  `knowledge/` + a fetched fight file as its system prompt and analyzes your logs. Everything in
  `knowledge/` is written **for it**.
- **Build agent** — Claude Code working in this repo, *authoring* the knowledge layer.
  [CLAUDE.md](CLAUDE.md) is its instruction file. If you contribute, you're acting as the build agent.

The **analysis agent** itself has **two runtime modes**, two halves of one plan → raid → observe cycle:

- **Analysis mode** — read a *past* pull and diagnose what happened (backward, observational).
- **Planning mode** — author a *forward* mit plan, assigning cooldowns to fight timestamps
  (forward, derivational; every cooldown must be recast-feasible).

---

## Setup

### 1. Clone + Python

```bash
git clone <your-fork-url> ffxiv-agent
cd ffxiv-agent
```

`scripts/fetch_fight.py` uses **only the Python 3 standard library** — no `pip install` needed.
Any Python 3.x works.

### 2. FFLogs API credentials

1. Create a client at <https://www.fflogs.com/api/clients/> (leave **Public Client** unchecked;
   the client-credentials flow stores a secret locally). Redirect URL can be `http://localhost`
   (unused).
2. Copy the template and fill in your own credentials:
   ```bash
   cp .env.example .env
   ```
   ```ini
   FFLOGS_CLIENT_ID=your_client_id_here
   FFLOGS_CLIENT_SECRET=your_client_secret_here
   ```
   `.env` is gitignored — never commit it.

### 3. Run it

**In Claude Code** (recommended) — the `/ffxivanalyze` slash command loads the knowledge layer,
runs the fetcher itself, and walks the summary → drill-in workflow:

```
/ffxivanalyze <report-code> [fight-id]
```

Omit the fight ID to list the whole raid night's pulls and pick one. Decoded dumps land in a
gitignored `.fights/` directory.

**Manually / on claude.ai** — run the fetcher and feed its output (plus `knowledge/`) to an
analysis chat:

```bash
# list the fights in a report
py scripts/fetch_fight.py <REPORT_CODE>

# decode one fight to a file you can paste in
py scripts/fetch_fight.py <REPORT_CODE> <FIGHT_ID> > fight.txt
```

Then paste the `knowledge/` files (AGENT.md first) + `fight.txt` into a claude.ai conversation,
or set up a claude.ai Project with `knowledge/` as project knowledge.

---

## Optional: Google Sheets output

Planning mode can write mit plans into a Google Sheet via the third-party
[`mcp-google-sheets`](https://github.com/xing5/mcp-google-sheets) MCP server. **This is fully
optional and per-user** — the core product (analysis + the knowledge layer) needs none of it,
and each person brings their own Google account and sheets.

To enable it:

1. `pipx install mcp-google-sheets` (or `pip install --user mcp-google-sheets`).
2. Create a Google Cloud **service account**, enable the Sheets API, download its JSON key, and
   **share your target spreadsheet with the service account's email**.
3. `cp .mcp.json.example .mcp.json` and set `SERVICE_ACCOUNT_PATH` to your key's absolute path.
   `.mcp.json` is gitignored; never commit your key or its path.

The maintainer's own mit-plan sheets are private and not part of this repo — you keep your own.

---

## Contributing

Outside contributions go through **fork + pull request**:

1. Fork the repo, branch, make your change, open a PR.
2. For **factual corrections** to FFXIV mechanics (a wrong debuff %, a misclassified mechanic,
   an outdated tooltip), please **open an Issue first** with a citation — a log, a patch note,
   or [The Balance](https://discord.gg/thebalanceffxiv). The whole project history is correcting
   FFXIV facts, so corrections are the most valuable contribution; they're just worth discussing
   before they land.

Before authoring knowledge-layer changes, read [CLAUDE.md](CLAUDE.md) — it documents the
two-agents boundary, the file-design principles (fight files are catalogs, not mit plans), and a
running list of FFXIV mistakes not to reintroduce.

A couple of conventions worth knowing up front:
- **Fight catalogs are anonymized to role labels** (MT, OT, SGE, DRG, …), never real character
  names. Keep it that way.
- **Trust live job-guide / patch data over training-data memory.** When the guide and memory
  disagree, the guide wins.

## License

[MIT](LICENSE).
