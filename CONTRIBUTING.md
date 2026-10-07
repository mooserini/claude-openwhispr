# Contributing

OpenWhispr users and Claude users both welcome. Fixes from either side
make the bridge stronger.

## What helps most

- **CLI-accuracy fixes.** If an OpenWhispr CLI flag, path, scope, or limit
  in `skills/openwhispr/SKILL.md` drifts from
  [the docs](https://docs.openwhispr.com/llms.txt), a correction with the
  docs link is the highest-value contribution there is.
- **First-session reports.** Tried the README's try-this block and tripped?
  Say where, on what OS, with what plan (free local or paid cloud).
- **Screenshot updates.** App UI moves fast; a fresh capture with personal
  details blurred keeps the visual story honest.

## Ground rules

- This project is unaffiliated with OpenWhispr and Anthropic. Don't claim
  endorsement; do credit sources with links.
- No personal data in contributions: blur emails, names, and paths in
  screenshots; keep placeholders generic.
- Local-first, consent-gated, no silent cloud: any change that weakens
  those needs an explicit discussion first.
- Tests are stdlib + pytest only, no live network:
  `python -m pytest tests/ -q`.
