---
name: snooze
description: Park the current Claude Code session in David's "backburner" sidebar group and bring it back to Ungrouped at a chosen time. Use whenever David says "/snooze", "snooze this", "snooze for 3 days", "park this until Tuesday", or asks in any phrasing for this session to go away for a while and come back later.
---

# /snooze

`/snooze <when>` = `/remind <when>` plus a move to the "backburner" group right now. The reminder's
arrival already moves the session back to Ungrouped and marks it unread, so the session leaves
David's to-do list today and returns on its own.

1. Follow the `remind` skill (`~/.claude/skills/remind/SKILL.md`) end to end:
   parse the time, write the reminder text (if David gave none, one or two sentences on what the
   session is waiting on and the next action), create the scheduled task with the remind prompt
   template. A day with no time means 9:35 am.
2. Then move this session to backburner: `ToolSearch`
   `select:mcp__ccd_sidebar__list_groups,mcp__ccd_sidebar__move_sessions`, find the group named
   `backburner` in `list_groups` (create it with `create_group` only if it is missing), and
   `move_sessions` with `session_ids: ["self"]` and that `group_id`. Moving the session itself
   needs no approval.
3. Reply in one line: `Snoozed to backburner until <Day Mon D, h:mm am>: <text>.`

When the reminder fires, the remind skill's arrival steps apply unchanged (move to Ungrouped, mark
unread, restate the next action).
