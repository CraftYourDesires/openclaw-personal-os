# Start Here on Remm's Mac

This repository is the complete starter package. Codex should read this file first and guide Remm one step at a time.

## What Kaz sends Remm

1. Repository: `https://github.com/CraftYourDesires/openclaw-personal-os`
2. Interactive guide: `guide/index.html`
3. Full setup PDF: `guide/remm-openclaw-personal-os.pdf`
4. Short call PDF: `output/pdf/remm-personal-os-call-overview.pdf`

The repository already contains the HTML, both PDFs, installer, folder templates, Obsidian configuration, Vault Recall skill, setup doctor, and first Vercel practice project. Sending the repository link gives Codex the entire package.

## The one Home folder

Create one folder named `Openclaw` directly inside Remm's Mac Home folder.

The finished layout is:

```text
~/Openclaw/
  system/       Public repository and setup code
  runtime/      Private personal data created by the installer
    vault/      Obsidian notes, tasks, meetings, and daily notes
    workspace/  OpenClaw instructions and skills
    bin/        Reviewed helper commands
    logs/       Local service logs
```

Git tracks `system`. Git never tracks `runtime`.

## Remm's first five steps

1. Install the Codex desktop app and sign in with Remm's paid ChatGPT account.
2. Open Finder and press Shift, Command, and H together to open the Home folder.
3. Choose File, then New Folder. Name the folder `Openclaw`.
4. Open Codex, choose Open Folder, and select the new `Openclaw` folder.
5. Start a task in Codex and paste the bootstrap prompt below.

## Bootstrap prompt for Codex

```text
Goal: complete my OpenClaw Personal OS setup on this Mac from a blank starting point.

Success means:
* My public system repository is located at ~/Openclaw/system.
* My private runtime is located at ~/Openclaw/runtime.
* Every required application, command line tool, account connection, Obsidian plugin, OpenClaw service, and Vault Recall component is installed and verified.
* A controlled voice request, recurring task, calendar event, daily note, Granola review, approved meeting task, recall answer, GitHub change, and Vercel deployment all pass.

Stop when: personal-os doctor reports that every required check passes and every controlled end to end test succeeds.

Constraints: Preserve existing files. Keep private data in ~/Openclaw/runtime. Keep reusable public code in ~/Openclaw/system. Store secrets through Doppler. Use my own accounts and pause for every personal sign in, permission, private token, paid plan choice, PIN entry, or material decision.

Create ~/Openclaw if it is missing. Clone https://github.com/CraftYourDesires/openclaw-personal-os into ~/Openclaw/system if that folder is missing. Read START-HERE.md, README.md, DECISIONS.md, setup.sh, and guide/index.html before installing.

Run the safe setup steps yourself. Give me one short human instruction at a time. Wait for me to finish each sign in or permission screen, verify the result, then continue. Run personal-os doctor after each phase and use its first required FIX item as the next step.
```

## What Codex handles

Codex creates the folder structure, clones the repository, reads the guide, runs the installer, installs the supported tools, configures the safe local files, runs the doctor, and verifies each connection.

After cloning, Codex opens the interactive guide from `~/Openclaw/system/guide/index.html` in Remm's default browser.

## What Remm handles

Remm signs into his own accounts, approves macOS permissions, creates his Telegram bot with the verified BotFather account, sends the bot its first private message, enters private values through Doppler, authorizes Google, chooses any paid plans, opens the Obsidian vault, and confirms the final tests. Codex reads that first Telegram update, confirms Remm's sender name, and stores the numeric owner ID.

## Pause and resume

Open `~/Openclaw` in Codex and say:

```text
Continue my OpenClaw Personal OS setup from START-HERE.md. Run personal-os doctor, explain the first required FIX item in one short instruction, verify it after I finish, and continue.
```

If a screen looks different, attach a screenshot to Codex and say what you expected to see. Codex should inspect the current screen and provide the next single action.
