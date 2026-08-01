# Decisions

## 2026-08-01: Pin the automation runtime to Node 24

Decision: Install and select Node 24 for OpenClaw, QMD, Codex CLI, and Vercel CLI.

Reason: OpenClaw's dedicated Node guide names Node 24 as the recommended default and requires at least Node 24.15 on that line. A single supported runtime prevents native module ABI drift in QMD.

Evidence:

* https://docs.openclaw.ai/install/node
* https://github.com/tobi/qmd

## 2026-08-01: Keep the public repository separate from private runtime data

Decision: Clone the public system into `~/Openclaw/system` and keep the vault plus OpenClaw workspace under `~/Openclaw/runtime`.

Reason: This separation prevents normal Git operations from staging meeting transcripts, calendar data, tasks, and personal notes. It also lets Codex update the public system without mixing data ownership boundaries.

Evidence:

* https://docs.openclaw.ai/agent-workspace
* https://git-scm.com/docs/gitignore

## 2026-08-01: Use a review gate between Granola and TaskNotes

Decision: Codex writes proposed meeting actions into the meeting note. A separate approval command creates TaskNotes files for selected actions.

Reason: Meeting transcripts contain ambiguity, tentative ideas, and statements assigned to different people. Separating extraction from task creation preserves user control and makes the state transition auditable.

Evidence:

* https://tasknotes.dev/
* https://docs.granola.ai/help-center/taking-notes/transcription

## 2026-08-01: Use Obsidian Bases as the task view foundation

Decision: Enable Bases before TaskNotes and ship portable Base files for task views.

Reason: Current TaskNotes requires Obsidian 1.10.1 or later and uses Bases files for its task interfaces. Versioned Base files are inspectable and portable.

Evidence:

* https://tasknotes.dev/
* https://tasknotes.dev/views/task-list/

## 2026-08-01: Use local Granola desktop authentication for version one

Decision: Read the signed in Granola desktop session and call the same local account endpoints used by Kaz's working flow.

Reason: The user explicitly selected the existing automatic local desktop authentication method. This avoids requiring a separate paid integration. The setup doctor identifies this dependency clearly because desktop app updates may change it.

Evidence:

* https://docs.granola.ai/help-center/sharing/exporting-notes
* https://docs.granola.ai/help-center/taking-notes/transcription

## 2026-08-01: Use exact HTML and SVG for system diagrams

Decision: Render labels, arrows, and setup state with HTML and SVG. Use generated raster art only as a supporting visual.

Reason: Deterministic diagrams keep text crisp, accessible, and printable. Supporting art can add warmth without becoming a source of technical truth.

Evidence:

* https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html
* https://www.w3.org/TR/SVG2/

## 2026-08-01: Preserve Kaz's Claude workflow and isolate Remm's Codex workflow

Decision: Keep Kaz's existing Vault Recall and Granola summarization compatible with Claude. Build Remm's Codex based implementation only in this new repository.

Reason: The user clarified that he still personally uses Claude. A separate implementation prevents the new onboarding work from invalidating his current workflow.

Evidence:

* User clarification recorded in the active goal ledger.

## 2026-08-01: Represent repeating requests as TaskNotes recurrence rules

Decision: Store repeating work as TaskNotes tasks with an RFC 5545 recurrence rule and a concrete next scheduled occurrence. Keep Apple Reminders for one time alerts.

Reason: TaskNotes advances the next occurrence when an instance is completed, while keeping the schedule portable in Markdown. This directly supports requests such as a reminder every Wednesday at nine.

Evidence:

* https://tasknotes.dev/features/recurring-tasks/
* https://www.rfc-editor.org/rfc/rfc5545

## 2026-08-01: Register Google OAuth from Doppler into the Mac keychain flow

Decision: Store the Google OAuth client values in Doppler. Build the required client JSON only in a temporary directory, register it with `gog`, and remove the temporary file immediately. Let `gog` use the macOS Keychain for runtime credentials.

Reason: The setup needs browser OAuth for two Google accounts without placing credential files in the repository or permanent project folders. Doppler remains the source of truth, while the system keychain provides the local runtime cache expected by the CLI.

Evidence:

* https://github.com/steipete/gogcli#authentication-secrets
* https://docs.doppler.com/docs/enclave-secrets

## 2026-08-01: Activate background work with user LaunchAgents

Decision: Install separate user LaunchAgents for the Telegram gateway and hourly Granola processing. Start them only after account sign ins and Doppler secrets are ready.

Reason: User LaunchAgents match a personal Mac deployment, survive app restarts, and preserve the version one boundary that the Mac must be awake. Delayed activation avoids a noisy failure loop during account setup.

Evidence:

* https://www.launchd.info/
* https://support.apple.com/guide/terminal/script-management-with-launchd-apdc6c107e0/mac

## 2026-08-01: Use a landscape presenter PDF for the first conversation

Decision: Give the introductory call its own landscape Letter PDF with one idea per page, large text, and a separate page for each of the nine discussion sections.

Reason: The full setup guide is optimized for installation. A screen shared conversation needs larger type, lower information density, and a predictable speaking sequence. The presenter PDF points back to the same repository and does not create a second setup process.

Evidence:

* https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
* https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html

## 2026-08-01: Publish the interactive guide from its existing source folder

Decision: Publish the tracked `guide` folder through GitHub Pages and link the hosted guide from `START-HERE.md`. Keep the local HTML copy as the setup version that saves Remm's checklist progress on his Mac.

Reason: A hosted link is easy to email and preview before installation. Publishing the existing folder avoids a duplicate website or a second content stream. GitHub's official Pages workflow supports uploading a static folder as an artifact and deploying it from the default branch.

Evidence:

* https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
* https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
