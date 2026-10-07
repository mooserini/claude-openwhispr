---
name: openwhispr
description: Find what the user dictated in local voice history.
version: 0.1.0
author: Thomas Kenny (github.com/mooserini)
license: MIT
platforms: [linux, macos, windows]
---

# OpenWhispr Skill

Local-first voice history and shared notes, with a paid cloud fallback. When OpenWhispr is the user's consistent voice input everywhere, its transcriptions are the rolling breadcrumb trail of what they said, and its notes are the handoff surface between agents.

Does not include assistant replies. Does not replace any speech-to-text setup the agent already has. Defaults to the free local desktop bridge; the cloud API is opt-in only and never touched without explicit in-turn consent.

## When to Use

- The user says "find what I said", "what was that thing I dictated", or can't remember a dictated phrase.
- Reading recent dictations, searching past voice history, or grounding a task in what the user actually said.
- Creating, reading, updating, or searching OpenWhispr notes as agent-to-agent handoffs.
- Transcribing a local audio file with the desktop model, optionally saving straight to a note.
- Managing dictionary words or snippets the user dictates constantly.
- Don't use for: the agent's own voice configuration, or any cloud call or API key step the user has not asked for in this turn.

## Prerequisites

- Node.js 20 or later.
- `@openwhispr/cli` installed globally via `npm install -g @openwhispr/cli`.
- OpenWhispr desktop app running locally for any `--local` work (install via `brew install --cask openwhispr`, openwhispr.com/download, or GitHub releases — no App Store, no login). No login or API key needed for local.
- Remote/cloud is opt-in and paid (API key management is a paid feature). Key setup runs via `openwhispr auth login`; the key is stored in the CLI's own config with `0600` permissions, never in a project `.env`. Gotchas: `transcriptions:delete` has no checkbox in the desktop app, so a delete-capable key must be created through the API; workspace keys (`ow_wks_live_`) do not work with the CLI — use a personal key. Never log in, set `api-base`, or send audio remote without explicit consent.
- Cloud opt-in note (only if the user asked this turn): without the desktop app, the agent bootstrap flow works — `POST https://api.openwhispr.com/api/v1/auth/email-code` with the user's email, the user pastes the 6-digit code (1 code per 60s, 5 per hour per email, 10 per hour per IP, 5 attempts per code, code expires in 10 minutes), then `POST https://api.openwhispr.com/api/v1/auth/email-code/verify` returns a 15-minute session token good only for `POST https://api.openwhispr.com/api/v1/keys/create`, which mints a scoped permanent key.

## How to Run

Run every invocation through the Bash tool. Always prefer `--local` to force the free desktop bridge.

- Check health via `openwhispr --local notes list --limit 1` — exit 0 means the local bridge answered, and it cannot touch the cloud. Bare `openwhispr doctor` diagnoses both backends and may contact the cloud when a key is stored, so run it only if the user asked for cloud diagnostics this turn. If local is unavailable (exit 2), tell the user to launch the desktop app and retry — never fall back to remote silently.
- Backend select via `openwhispr config get`; leave `backend: auto` so it prefers local when the app runs. The bridge listens on loopback; the live port is recorded in the CLI's bridge file — never assume a fixed port.
- Find what the user said via `openwhispr --local transcriptions list --limit 50`. The default table shows only ID, Status, Duration and Created, not the text, so use the times to pick candidates, then read each with `openwhispr --local transcriptions get <id>`. Individual dictations live only in transcriptions; they are not saved as notes.
- Notes are what the user (or an agent) made on purpose, and the transcripts attached to them. Read them via `openwhispr --local notes list --limit 20`, `openwhispr --local notes get <id> --format json|markdown`, `openwhispr --local notes search <query> --limit 10`.
- Write handoff note via `openwhispr --local notes create --content <text> --title <t> --folder <id>` (folder takes an id — resolve it first via `openwhispr --local folders list`) or `--content-file <path>` for long bodies.
- Dual backends: `--local` forces the desktop bridge (free, no cap, audio stays on-machine); `--remote` forces OpenWhispr Cloud (paid plan + key; over 4 MB files are split into 4-minute chunks client-side needing `ffmpeg` on PATH; cloud transcription is beta with no SLA). Bare `openwhispr` with `backend: auto` prefers local when reachable. Touch `--remote` only after the user opts into cloud.

## Quick Reference

All invocations run through `...`:

```
openwhispr --local notes list --limit 1   # local-only health check
openwhispr doctor                         # both backends; may contact cloud — opt-in turns only
openwhispr config get
openwhispr --local notes list [--folder <id>] [--limit N] [--format json|table]
openwhispr --local notes get <id> [--transcript] [--format json|markdown]
openwhispr --local notes create --content <text> | --content-file <path> [--title <t>] [--folder <id>]
openwhispr --local notes update <id> [--content <t>] [--folder <id>] [--title <t>]
openwhispr --local notes delete <id> [--dry-run]
openwhispr --local notes search <query> [--limit N]
openwhispr --local folders list
openwhispr --local folders create --name <name>
openwhispr --local transcriptions list [--limit N]
openwhispr --local transcriptions get <id> [--format json|text]
openwhispr --local transcriptions delete <id> [--dry-run]
openwhispr --local transcribe <file> [--model <id>] [--language <code>] [--note] [--title <t>] [--folder <name>]
openwhispr --local dictionary list
openwhispr --local dictionary add <word...> / remove <word...>
openwhispr --local snippets list / add "<trigger>" "<replacement>" / remove "<trigger>"
```

Exit codes: 0 success (at least one backend reachable for `doctor`), 1 bad args, 2 backend unreachable (app not running), 3 auth failure (often a missing scope — regenerate the key with the right boxes ticked), 4 not found.

## Procedure

1. Verify local is up via `openwhispr --local notes list --limit 1`. Done when it exits 0; if exit 2, tell the user to launch the desktop app and retry — do not fall back to remote silently.
2. Find the breadcrumb: `transcriptions list` first (limit 50), pick candidates by `Created` time, then `transcriptions get <id>` to read the text. Done when the matching utterance or a clear miss is established; quote id + timestamp when citing. Then check `notes search` for anything the user saved deliberately as a note.
3. Promote only on purpose: transcriptions are raw history; `notes create` only when the user wants a durable shared note. Done when the note id returns and `notes get` round-trips the same content.
4. Share between agents via notes: title + folder + full JSON body, never paraphrase ids. Done when the next agent can `notes get <id>` without asking the user for context.
5. Transcribe locally via `openwhispr --local transcribe <file>` using the app's current model; add `--note --title --folder <name>` (folder by name here) to file it in one step. Done when transcript text prints and the optional note id exists.
6. Grow the dictionary from real misses via `openwhispr --local dictionary add <word>` using the spelling the user wants to read, not the phonetic miss. Done when `dictionary list` shows the entry. Auto-learn (Settings → Preferences → Auto-learn from corrections) is off by default; once the user enables it, their corrections are added without a prompt — agent-side writes still need consent every time.

## Pitfalls

- Notes vs transcriptions: individual dictations land only in transcriptions, never in notes, so search transcriptions first and notes second. Notes (and the on-disk export folder) hold only what was made on purpose. An empty trail with Data Retention off is not a CLI bug: with retention off, text is pasted and nothing is stored. Local mode sees this desktop only, not the phone, unless paid cloud backup is on. Never call a `--limit 20` miss "not in history" without saying which door was checked.
- Dictionary is a hint, not an override. Keep it to the ~50 words actually gotten wrong; 500 dilutes the model. Export before moving machines.
- `--model <id>` must already be downloaded in the desktop app; a wrong name makes the CLI list what's available — use that list verbatim.
- Over 4 MB, remote files split into 4-minute chunks client-side and need `ffmpeg` on PATH; `--remote` transcribe is 600 minutes per calendar month and needs `--prompt` for names; prefer local for long or private audio.
- No SRT/VTT from the CLI; use `--format json` and post-process segments for timestamps.
- `audio delete` is local-only and dictation-only; meeting transcripts have no audio file; `--remote` errors by design.
- Never write, update, or delete notes/transcriptions/dictionary without explicit consent; reads and searches are always safe.
- Unattended runs stop at consent gates: `auth login`, the email-code paste, and any write need a person present. If nobody is there, report what is blocked and stop — never queue, retry-loop, or work around it.
- File fallback: OpenWhispr can auto-save notes, and the transcripts attached to them, as files on disk, organized by folder, with a rebuild action. Individual dictations are not exported there; reach those with `transcriptions list`. When the user enables it, prefer Read/Grep against their configured save location for bulk reads of notes; use the CLI when freshness or metadata (ids, timestamps) matters.

## Verification

- `openwhispr --local notes list --limit 1` exits 0 (local bridge reachable).
- Cited utterance includes transcription id + UTC timestamp matching `transcriptions get`.
- Any created note round-trips via `notes get <id> --format json` with identical title/content.
- No remote calls were made unless the user asked in this turn.
