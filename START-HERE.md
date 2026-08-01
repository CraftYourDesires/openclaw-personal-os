# Start Here on Remm's Mac

This repository is the complete starter package. Codex should read this file first and guide Remm one step at a time.

## What Kaz sends Remm

1. [Complete OpenClaw Personal OS repository](https://github.com/CraftYourDesires/openclaw-personal-os)
2. [Open the interactive setup guide](https://craftyourdesires.github.io/openclaw-personal-os/)
3. [Open or download the full setup PDF](guide/remm-openclaw-personal-os.pdf)
4. [Open or download the short call PDF](output/pdf/remm-personal-os-call-overview.pdf)

The repository already contains the HTML, both PDFs, installer, folder templates, Obsidian configuration, Vault Recall skill, setup doctor, and first Vercel practice project. Sending the repository link gives Codex the entire package.

For the simplest email, send Remm the repository link and the interactive guide link above. The PDFs are optional attachments. Do not attach `guide/index.html` by itself because it uses supporting files stored beside it in the repository.

Remm can read the hosted guide immediately in any browser. During setup, Codex clones the complete repository and opens the local interactive copy at `~/Openclaw/system/guide/index.html`. The local copy keeps his checklist progress in his browser on his Mac.

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

## Remm's first eight steps

1. Install the Codex desktop app and sign in with Remm's paid ChatGPT account.
2. In Codex, press Command and comma to open Settings. Choose General. Under Permissions, turn on Full access.
3. In the same General settings, turn on Prevent sleep while running.
4. Return to the task. Open the permissions control beneath the prompt box and choose Full access.
5. Open Finder and press Shift, Command, and H together to open the Home folder.
6. Choose File, then New Folder. Name the folder `Openclaw`.
7. Open Codex, choose Open Folder, and select the new `Openclaw` folder.
8. Start a task in Codex and paste the bootstrap prompt below.

## Keep Codex in Full access

Full access lets Codex read files, make changes, run commands, and use the network without stopping for routine approval prompts. After selecting it for the first task, tell Codex:

```text
Preserve my existing Codex settings and make Full access the default for future local tasks on this Mac. Use the current Codex configuration format. Confirm that routine approval prompts are off, local sandbox restrictions are removed, and this task reports Full access. Do not change another person's Codex configuration.
```

Use Full access only on Remm's personal Mac and with folders or repositories he trusts. Switch back to Ask for approval before opening unknown downloaded code. Full access does not remove the setup requirement to pause for account sign ins, macOS privacy prompts, private values, destructive actions, or decisions outside the approved plan.

## Bootstrap prompt for Codex

```text
Goal: complete my OpenClaw Personal OS setup on this Mac from a blank starting point.

Success means:
* My public system repository is located at ~/Openclaw/system.
* My private runtime is located at ~/Openclaw/runtime.
* Codex Full access is enabled, selected for this task, and saved as the default for future local tasks on this Mac.
* Prevent sleep while running is enabled.
* Every required application, command line tool, account connection, Obsidian plugin, OpenClaw service, and Vault Recall component is installed and verified.
* A controlled voice request, recurring task, calendar event, daily note, Granola review, approved meeting task, recall answer, GitHub change, and Vercel deployment all pass.

Stop when: personal-os doctor reports that every required check passes and every controlled end to end test succeeds.

Constraints: Preserve existing files. Keep private data in ~/Openclaw/runtime. Keep reusable public code in ~/Openclaw/system. Store secrets through Doppler. Use my own accounts. Do not pause for routine Codex command approvals after Full access is active. Pause for every personal sign in, macOS permission, private token, paid plan choice, PIN entry, destructive action, or material decision outside this approved plan.

Create ~/Openclaw if it is missing. Clone https://github.com/CraftYourDesires/openclaw-personal-os into ~/Openclaw/system if that folder is missing. Read START-HERE.md, README.md, DECISIONS.md, setup.sh, and guide/index.html before installing.

First verify that this task reports Full access and that Prevent sleep while running is enabled. Preserve my existing Codex settings and make Full access the default for my future local tasks using the current Codex configuration format. Then run the safe setup steps yourself. Give me one short human instruction at a time only when I must sign in, approve a macOS privacy prompt, enter a private value, or make a material decision. Continue routine installation and verification without asking for Codex command approval. Run personal-os doctor after each phase and use its first required FIX item as the next step.
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
