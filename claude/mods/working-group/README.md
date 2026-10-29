*Written by Claude (an AI agent) at David's request, from the notes of the session that built it. David uses the mod daily but did not write or review the code or this README line by line.*

# working-group

A tiny Claude Code mod for the Claude desktop app's Code tab. While a session is running a turn, it files that session under a sidebar group called **Working**. When the turn ends, it moves the session back to wherever it was. The result: the sidebar is a flat list of sessions that are ready for you, plus one group of sessions that are busy.

## The problem

The Code tab sorts sessions into status buckets: Needs input, Working, Ready for review, Idle. With "group by status" off, the plain list shows no status at all. With it on, sessions that are waiting on a person get split between Ready for review (anything with a live PR) and Idle (everything else), so there is no single list to work through.

What I wanted: one flat list of sessions ready for a person, plus one group for sessions that are running.

## Things that do not work

The grouping cannot be patched or rolled back. The Code tab's renderer is fetched at launch from Anthropic's asset server; the copy bundled in the app is only a fallback, and the app bundle has integrity checks on. The buckets are gated by a server-side flag and an account setting, neither changeable locally.

## The fix

A mod (a plugin hooks module) with two hooks:

- `turn.start`: record the session's current sidebar group, then move the session into **Working** (creating the group if it is missing).
- `turn.complete`: if the session is still in Working, move it back to the recorded group, or to Ungrouped.

It skips subagent turns, leaves the session alone if something else moved it mid-turn, and writes any failure to the session's status line as `working-group: <error>`. Turn status grouping off in the sidebar, and you get the custom sections plus one flat list.

## Install

Tested with Claude Code 2.1.308 and 2.1.309 inside the Claude desktop app on macOS, October 2026. The plugin API is marked early access and may change.

1. Copy this folder somewhere, for example `~/.claude/mods/working-group`.
2. Add to `~/.claude/settings.json`:

   ```json
   "env": { "CLAUDE_CODE_PLUGIN_DIRS": "/Users/<you>/.claude/mods/working-group" },
   "permissions": { "allow": [
     "mcp__ccd_session_mgmt__get_session",
     "mcp__ccd_sidebar__list_groups",
     "mcp__ccd_sidebar__create_group",
     "mcp__ccd_sidebar__move_sessions"
   ] }
   ```

   The allow rules matter in auto permission mode: without them the classifier refuses the mod's sidebar calls as self-modification, and it also refuses an agent's attempts to add the rules for you. Add them yourself, or approve the agent's edit in chat.

3. In the sidebar filter menu, set group-by to none on the Sessions section and on the Working section once it exists. Otherwise you get two Working headers, the custom section and the built-in status bucket.
4. Desktop sessions load plugins at process start. Existing sessions pick up the mod after `/reload-plugins` or an app restart; new sessions get it at once.

## Two quirks of the desktop app's tools

Both are pinned by the tests in `hooks/register.test.ts`, which run with `claude plugin test <this folder>`.

- `move_sessions` answers plain text ("Moved 1 session(s) to ..."), unlike `list_groups` and `get_session`, which answer JSON. Parse only the JSON answers.
- `move_sessions` rejects `group_id: null` with "No custom group with that id", although its description says null means Ungrouped. Pass `section_id: "sessions"` instead.

Also: the `ccd_*` tools come from the desktop app through the SDK, not from an MCP server, so a mod reaches them with `$.tool.call({ tool: 'mcp__ccd_sidebar__list_groups' })`, not `$.mcp.call`.

## Files

- `.claude-plugin/plugin.json`: manifest.
- `hooks/hooks.json`: names the module.
- `hooks/register.ts`: the two hooks.
- `hooks/register.test.ts`: five tests against an engine stand-in.
- `types/index.d.ts`: declares the one value the mod stores, the group to return to.
