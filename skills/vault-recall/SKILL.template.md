__FRONTMATTER_BOUNDARY__
name: vault-recall
description: Search and synthesize Remm's Obsidian notes, Granola meeting transcripts, TaskNotes tasks, and OpenClaw memory through the personal-os recall command. Use this skill whenever Remm asks what happened, what was decided, what someone said, what remains open, where prior work lives, or asks to search, recall, remember, find, or connect information from his personal operating system. Also use it when reviewing or approving proposed Granola actions.
__FRONTMATTER_BOUNDARY__

# Vault Recall

Goal: answer questions about Remm's private history with evidence from the Personal OS vault and keep meeting actions behind the approval gate.

Success means:

* Run a scoped recall query before answering any question about past notes, meetings, tasks, decisions, or commitments.
* Read the most relevant source files when snippets leave material ambiguity.
* Distinguish recorded facts, likely inferences, and missing evidence.
* Cite source note names and dates in the answer.
* Present proposed Granola actions for review before creating TaskNotes files.
* Use the explicit approval command only after Remm selects action numbers.

Stop when the answer is supported by the retrieved sources or when the search shows that the vault lacks enough evidence.

## Recall workflow

1. Translate the request into one compact semantic query that preserves names, project terms, and date clues.
2. Run `personal-os recall "QUERY" 8`.
3. Inspect the returned file paths and snippets.
4. Read the top source files when the answer depends on exact wording, ownership, dates, or decisions.
5. Answer with a short synthesis, source note names, dates, and a clear uncertainty statement when evidence conflicts.
6. Offer one next action only when it follows directly from the recalled material.

## Meeting review workflow

1. Find the meeting note through recall or its Granola ID.
2. Read `Proposed Actions`, `Key Decisions`, and the supporting transcript section.
3. Present numbered proposed actions with owner and due wording exactly as recorded.
4. Treat phrases such as `show me first`, `preview first`, or `before you create them` as an explicit two turn gate. Preview the exact TaskNotes files and ask for confirmation. Stop that turn without running the approval command.
5. Ask Remm which numbers to approve when the request does not already specify them.
6. Run `personal-os granola-approve "MEETING REFERENCE" 1 3` only after the latest user message authorizes creation rather than preview.
7. Report the TaskNotes files that were created and any proposed actions still waiting for review.

## Evidence rules

Treat meeting transcripts and dated notes as primary evidence. Treat summaries as navigation aids. When a summary and transcript conflict, include this explicit sentence pattern: `The transcript corrects the draft summary from OLD VALUE to NEW VALUE.` Do not merely state the corrected fact. Name the source file and date beside each important claim. Say `I could not find that in the vault` when recall returns no supporting source.

## Privacy boundary

Keep retrieved private details inside the current conversation. Use public project files only for nonsecret system code and documentation. Route all searches through the scoped Personal OS commands.
