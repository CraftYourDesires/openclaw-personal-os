# OpenClaw Personal OS

OpenClaw Personal OS is a guided Mac setup for a voice first personal assistant. It connects Wispr Flow, Telegram, OpenClaw, Codex, Granola, Obsidian, Google Calendar, GitHub, and Vercel without expecting the owner to be technical.

Begin with `START-HERE.md`. The interactive guide is the canonical onboarding document. Open `guide/index.html` in a browser, or read the matching PDF in `guide/remm-openclaw-personal-os.pdf`.

For an introductory conversation, use the landscape presenter PDF in `output/pdf/remm-personal-os-call-overview.pdf`. It explains the system map and follows the nine part call sequence before any installation begins.

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

1. Install the Codex desktop app and sign in with Remm's paid ChatGPT account.
2. In Finder, press Shift, Command, and H to open the Home folder.
3. Create one folder named `Openclaw`.
4. Open `~/Openclaw` in Codex.
5. Paste the bootstrap prompt from `START-HERE.md`.
6. Let Codex clone this repository into `~/Openclaw/system` and create private data under `~/Openclaw/runtime`.
7. Follow one account or permission instruction at a time.
8. Run `personal-os services-start` after accounts and Doppler secrets are ready.
9. Run `personal-os doctor` until every required check passes.

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

## Required agent abilities

* Vault Recall is the custom installed skill. It searches QMD evidence, resolves transcript conflicts, and preserves the Granola approval gate.
* `gog` is the bundled OpenClaw Google Workspace skill used for both calendars and optional read only Gmail.
* Task capture, repeating tasks, daily notes, meeting import, and action approval are reviewed `personal-os` command workflows defined in the OpenClaw workspace instructions.
* GitHub CLI and Vercel CLI are agentic project tools available to Codex after Remm signs into his own accounts.

## Security posture

The setup repository lives at `~/Openclaw/system`. The OpenClaw agent works inside `~/Openclaw/runtime`. Routine actions use reviewed helper commands. Telegram accepts only the owner's numeric user ID. Host execution uses an allowlist. App installation and other supported high risk actions require a short lived PIN authorization. Secrets live in Doppler and are injected at runtime.

Google OAuth client values also live in Doppler. The helper creates a temporary credential file for `gog`, registers it, and removes that temporary file immediately.

## Privacy note

This setup mixes work and personal information in one private vault. Confirm that meeting recording, transcript retention, calendar access, and email access comply with employer policy and local law. Full Granola transcripts are retained until the owner deletes them.

## Project files

* `START-HERE.md`: exact blank Mac folder, cloning, prompt, and resume instructions
* `setup.sh`: idempotent local installer
* `doctor.sh`: one command health check
* `scripts/personal_os.py`: daily note, Granola, task, reminder, calendar, and recall commands
* `vault-template/`: portable Obsidian vault configuration
* `workspace-template/`: OpenClaw operating instructions
* `config/`: safe OpenClaw and launch service templates
* `skills/`: core Codex and OpenClaw skills
* `guide/`: interactive HTML and matching PDF
* `output/pdf/`: short landscape presenter PDF for the introductory call
* `status/`: first GitHub to Vercel deployment
* `tests/`: automated verification
