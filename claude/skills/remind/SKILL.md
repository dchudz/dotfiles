---
name: remind
description: Bring the current Claude Code session back to David's attention at a later time, like Slack's /remind. Use whenever David says "/remind", "remind me", "bring this back on Tuesday", "come back to this at 3", "resurface this", "ping me about this later", "put this on my list for Thursday", or asks in any phrasing for this session to reappear at a time, with or without a reminder text. Also handles "/remind list" and "/remind cancel <id>". Receiving side: use when a message arrives in this session that begins "Reminder from /remind".
---

# /remind

Makes this session resurface in the sidebar at a chosen time: it moves itself to Ungrouped (David's to-do list), marks itself unread, and restates what to do. Works from any group David has filed the session under, because delivery is by session id.

Mechanism: a one-time scheduled task (`mcp__scheduled-tasks__create_scheduled_task` with `fireAt`) whose only job is to send a message into this session. The message carries the instructions, so this session does the move itself when it arrives (a session moving *itself* needs no approval; another session moving it would prompt David, which is useless when he is away).

## Setting a reminder

Load tools first: `ToolSearch` with `select:mcp__ccd_session_mgmt__get_session,mcp__scheduled-tasks__create_scheduled_task`.

1. **Parse the time.** Local time (America/New_York). Today's date is in the conversation context. Accept "in 2 hours", "tomorrow 9am", "tuesday 9:35", "oct 20 3pm", "next monday". A day with no time means 9:35 am. If the time is genuinely ambiguous, ask once in text with a recommended answer; otherwise do not ask.
2. **Reminder text.** Use David's words if he gave any. If not, write one or two sentences saying what this session is waiting on and the concrete next action, specific enough that he can act without rereading the session (names, phone numbers, PR numbers, links).
3. **Session id.** `get_session` with `session_id: "self"`; use its `sessionId` and `title`.
4. **Create the task.**
   - `taskId`: `remind-<short-slug>-<YYYYMMDD-HHMM>`
   - `title`: `Remind: <short text>`
   - `description`: one line
   - `fireAt`: ISO 8601 with offset, e.g. `2026-10-13T09:35:00-04:00`
   - `notifyOnCompletion`: true
   - `prompt`: the template below, filled in.
5. **Reply in one line:** `Reminder set for <Day Mon D, h:mm am>: <text>.` Add the caveat that scheduled tasks only fire while the desktop app is open (otherwise on next launch) only if David has not been told in this session.

### Task prompt template

```
This prompt was written by an AI agent (Claude), not by a human. Verify anything you rely on.

Your only job: deliver a reminder into the existing Claude Code desktop session with id <SESSION_ID> (title "<SESSION_TITLE>").

Step 1. Send exactly this message to that session (SendMessage with `to` set to the session id, or mcp__ccd_session_mgmt__send_message with session_id set to it):

"Reminder from /remind, set <SET_DATE> for <FIRE_DATE>. First move this session to Ungrouped (move_sessions with session_ids ["self"] and section_id "sessions") and mark it unread (set_unread self true). Then tell David: <REMINDER_TEXT>"

Step 2. If the messaging tool reports anything other than delivered or queued, fall back to doing the move yourself: mcp__ccd_sidebar__move_sessions with session_ids ["<SESSION_ID>"] and section_id "sessions", then mcp__ccd_sidebar__set_unread on that id with unread true. Report what happened.

Do nothing else. Do not call anyone, send email or Slack, or edit files.
```

## When a reminder arrives in this session

A message beginning "Reminder from /remind" (shown as "From Remind: ..."). Do exactly this and nothing else:

1. `ToolSearch` `select:mcp__ccd_sidebar__move_sessions,mcp__ccd_sidebar__set_unread`.
2. `move_sessions` with `session_ids: ["self"]`, `section_id: "sessions"`.
3. `set_unread` with `session_id: "self"`, `unread: true`.
4. Reply to David with the reminder text and the next action, answer-first, a few lines at most. Do not start on the work itself unless the reminder says to.

## List and cancel

- `/remind list`: `mcp__scheduled-tasks__list_scheduled_tasks`, show the tasks whose id starts with `remind-`, one line each: fire time, text, task id.
- `/remind cancel <id or description>`: `mcp__scheduled-tasks__delete_scheduled_task`. A fired one-time task disables itself; deleting it is still fine.

## Notes

- The create tool's "(tomorrow)" label in its result is often wrong; trust the fireAt date you passed.
- Tool approvals are stored per task, so a fresh task's run may pause on a permission prompt the first time it uses the messaging tool. If a reminder matters and David will be away, suggest "Run now" on it once in the Scheduled sidebar section (this also delivers the reminder immediately).
