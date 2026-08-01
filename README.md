# OpenClaw Personal OS

OpenClaw Personal OS is a guided Mac setup for a voice first personal assistant. It connects Wispr Flow, Telegram, OpenClaw, Codex, Granola, Obsidian, Google Calendar, GitHub, and Vercel without expecting the owner to be technical.

The interactive guide is the canonical onboarding document. Open `guide/index.html` in a browser, or read the matching PDF in `guide/remm-openclaw-personal-os.pdf`.

## What it does

* Dictate a request with Wispr Flow into a private Telegram bot.
* Let OpenClaw create routine tasks, reminders, and calendar events from one allowlisted Telegram account.
* Turn repeating requests into portable TaskNotes recurrence rules.
* Build a focused daily note with today's events, due tasks, reminders, Granola reviews, and notes.
* Import Granola meetings with full transcripts.
* Use Codex to propose meeting actions, then create real tasks only after approval.
* Search the Obsidian vault, meeting history, and OpenClaw memory with Vault Recall.
* Keep projects agent friendly through GitHub CLI and Vercel CLI.

## Start here

1. Install the Codex desktop app and sign in with a paid ChatGPT account.
2. Open this repository in Codex.
3. Attach `guide/index.html` or the PDF and paste the master onboarding prompt from the guide.
4. Let Codex run `bash setup.sh` and follow the pauses for account sign ins.
5. Run `personal-os services-start` after accounts and Doppler secrets are ready.
6. Run `personal-os doctor` until every required check passes.

## Three onboarding phases

### Phase 1: Accounts and voice

Codex installs GitHub CLI, Vercel CLI, Codex CLI, OpenClaw, Doppler, Obsidian, Granola, Wispr Flow, QMD, and the Google Workspace CLI. You sign in when the browser or app requires it. Telegram is paired to one numeric user ID.

### Phase 2: Daily operating system

Codex creates one Obsidian Sync vault, installs the required plugins, connects work and personal calendars, and verifies the daily note. Gmail access is optional and read only.

### Phase 3: Meetings, memory, and building

Codex connects the signed in Granola desktop session, verifies the review before task workflow, enables Vault Recall, and deploys the nonsecret status page through GitHub and Vercel.

## Required Obsidian plugins

Core plugins:

* Bases
* Daily Notes
* Templates
* Sync

Community plugins:

* TaskNotes
* Dataview
* Google Calendar

Excalidraw is included as an optional plugin and starts disabled.

## Security posture

The OpenClaw agent works inside `~/PersonalOS/runtime`. Routine actions use reviewed helper commands. Telegram accepts only the owner's numeric user ID. Host execution uses an allowlist. App installation and other supported high risk actions require a short lived PIN authorization. Secrets live in Doppler and are injected at runtime.

Google OAuth client values also live in Doppler. The helper creates a temporary credential file for `gog`, registers it, and removes that temporary file immediately.

## Privacy note

This setup mixes work and personal information in one private vault. Confirm that meeting recording, transcript retention, calendar access, and email access comply with employer policy and local law. Full Granola transcripts are retained until the owner deletes them.

## Project files

* `setup.sh`: idempotent local installer
* `doctor.sh`: one command health check
* `scripts/personal_os.py`: daily note, Granola, task, reminder, calendar, and recall commands
* `vault-template/`: portable Obsidian vault configuration
* `workspace-template/`: OpenClaw operating instructions
* `config/`: safe OpenClaw and launch service templates
* `skills/`: core Codex and OpenClaw skills
* `guide/`: interactive HTML and matching PDF
* `status/`: first GitHub to Vercel deployment
* `tests/`: automated verification
