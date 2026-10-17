---
name: share-transcript
description: Publish a shareable transcript of a Claude Code conversation — as a new tab on an existing artifact or as a standalone page — extracted verbatim from the session jsonl, with tool activity condensed to bracketed stage directions. Use whenever the user wants others (teammates, PR reviewers, future readers) to see the conversation behind some work, in any phrasing — "add a transcript tab", "share this conversation", "publish the chat", "attach the transcript to the PR", "show the team how we did this", "let people see our process" — even if they don't say the word "transcript".
---

# Share Transcript

Turn the current (or any past) Claude Code session into a polished, publishable transcript: the user's and Claude's messages verbatim, tool activity summarized as stage directions.

## Workflow

1. **Locate the session file(s).** Sessions live in `~/.claude/projects/<munged-cwd>/*.jsonl` where `<munged-cwd>` is the working directory with `/` and `.` replaced by `-`. One conversation can span several files (session-ID rollovers, compactions), and history-copying is inconsistent: sometimes the newest file carries the full history, sometimes only the slice since the last compaction. So always verify both ends — the candidate file's first real user message must match the conversation's actual start, and its tail must contain the most recent messages. If the newest file starts mid-conversation (its first "user" entry is a compaction summary), find the older file holding the earlier history and stitch: extract each, then join at the overlap (later files repeat messages after their summary point — dedupe by matching text, keeping one copy).

2. **Extract.** Run the bundled script (needs the `markdown` package):
   ```bash
   uv run --with markdown python scripts/extract_transcript.py --jsonl <session.jsonl> --out turns.html --user-name <FirstName>
   ```
   It emits `<div class="turn u|c">` blocks ready for either output mode. See the script for what it filters and why; the critical rules it encodes:
   - Skip `isMeta` entries — the harness injects skill instructions as user-role messages, and without this filter they get misattributed to the user (this bug shipped once; the user caught their "own" words they never said).
   - Skip `isSidechain` (subagent traffic), tool_result-only messages, and compaction summaries; strip `<system-reminder>` and command-wrapper tags *inside* kept messages (a real user message can share an entry with a `/command` block).
   - Tool calls become bracketed italic stage-direction lines, coalesced per turn, deduplicated, capped with "+N more".

3. **Audit before showing anyone.** Print every user turn's first ~110 characters and read them: each one must be something the user plausibly typed. Injected or duplicated-looking text gets investigated in the jsonl (check `isMeta`, timestamps), never shrugged off. Also grep the output for leak markers: `system-reminder`, `untrusted-data`, `<function`, `command-name`.

4. **Review for sensitive content, then agree on redactions.** Scan the full transcript for anything that could embarrass or reflect poorly on any person, anything confidential, and anything too personal for the audience. Propose specific redactions to the user and get agreement before publishing — don't silently decide. When applying a redaction:
   - Replace the text with a visible `[redacted]` chip (`<span style="background:#e8e8e8;color:#666;padding:0 0.3em;border-radius:3px;">[redacted]</span>`), and redact *echoes* too — later turns that quote or paraphrase the redacted text.
   - A visible redaction is itself a signal that something was cut. If redactions are needed at all, raise with the user whether sharing this transcript is worth it before proceeding.
   - The header note must describe conventions only ("messages reproduced verbatim; bracketed lines summarize tool activity; ends at …"). It must not claim completeness ("unabridged", "nothing redacted") or mention redactions.

5. **Assemble.** Two modes:
   - **Standalone page** (default; also the PR mode): fill `assets/standalone.html` — replace `{{TITLE}}`, `{{KICKER}}`, `{{SUBTITLE}}`, `{{NOTE}}`, `{{TURNS}}`.
   - **Tab on an existing artifact**: read `references/artifact-tab.md` first — it covers class namespacing, the tab bar, and merge-with-live-version rules.
   In both modes, jump links must anchor the exact message `<p>` (consecutive user messages merge into one display turn, so a turn-level anchor lands on the wrong message) and scroll via `onclick="...scrollIntoView({behavior:'smooth'});return false;"` — bare `#hash` navigation is unreliable inside the artifact viewer frame.

6. **Verify the render yourself** (headless Chrome screenshot or equivalent) before publishing: tabs/anchors work, turns display, nothing overflows.

7. **Publish and deliver.** Publish as an artifact (when updating an existing artifact from a different conversation, pass its `url`; keep its favicon stable). Also save a local copy where the user keeps deliverables. Remember that org-shared artifacts go live to viewers immediately on publish.

## PR flavor

For "attach the transcript to this PR" (authoring or review sessions): publish the standalone page as an artifact and link it from the PR description inside the agent-authored, block-quoted section (per the repo's posting conventions). Never commit the transcript file to the PR branch — it's not part of the change.

## Ongoing conversations

The transcript necessarily ends before the request that produced it. Say where it ends in the note ("Ends at the request to build this transcript"). If the conversation continues and the user wants updates, re-run extraction and rebuild — the script is idempotent over the growing jsonl. When the surrounding document keeps evolving after the transcript is cut, add a second note: "Transcript current through <date>. Later edits appear in the <other tab/page> only."
