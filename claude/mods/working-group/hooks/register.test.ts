import { expect, test } from 'claude-code/testing'

const WORKING = { id: 'cg-working', name: 'Working' }
const OTHER = { id: 'cg-other', name: 'Other' }

/** An engine stand-in for the sidebar: the session's group and the groups that exist.
 *  Answers as the desktop app does: JSON from list_groups / create_group / get_session,
 *  plain text from move_sessions, and a refusal of `group_id: null`. */
function sidebar(on: Parameters<Parameters<typeof test>[1]>[1], start: { group: string | null; groups: { id: string; name: string }[] }) {
  const state = { group: start.group, groups: [...start.groups], moves: 0, status: undefined as string | undefined }
  on('turn.start', (_, e) => ({ turnId: e.turnId }))
  on('turn.complete', (_, e) => ({ text: (e as { text?: string }).text ?? '' }))
  on('ui.status', (_, e) => { state.status = (e as { text?: string }).text; return { value: undefined } })
  // A stand-in sets `text` itself: core fills it only for a real tool's answer.
  const answer = (text: string) => ({ result: { content: [{ type: 'text', text }] }, text }) as never
  const json = (value: unknown) => answer(JSON.stringify(value))
  on('tool.call', (_, e) => {
    switch (e.tool) {
      case 'mcp__ccd_session_mgmt__get_session':
        return json({ sessionId: 'local_self', group: state.group === null ? null : { id: state.group } })
      case 'mcp__ccd_sidebar__list_groups':
        return json(state.groups)
      case 'mcp__ccd_sidebar__create_group': {
        const created = { id: `cg-${state.groups.length}`, name: String((e as { name?: unknown }).name) }
        state.groups.push(created)
        return json(created)
      }
      case 'mcp__ccd_sidebar__move_sessions': {
        const { group_id, section_id } = e as { group_id?: string | null; section_id?: string }
        if (group_id === null) return { result: 'No custom group with that id', text: 'No custom group with that id', isError: true } as never
        state.moves += 1
        state.group = section_id === 'sessions' ? null : (group_id ?? section_id ?? null)
        return answer(`Moved 1 session(s) to ${state.group ?? 'Ungrouped'}`)
      }
      default:
        return { result: {} }
    }
  })
  return state
}

const turn = { text: 'hi', turnId: 't1' }
const done = { ...turn, reason: 'answer' as const, answer: 'ok', durationMs: 1, isAborted: false }

test('an ungrouped session goes to Working for the turn and back to Ungrouped', async ($, on) => {
  const s = sidebar(on, { group: null, groups: [] })
  await $.turn.start(turn)
  expect(s.status).toBe(undefined)
  expect(s.groups.map(g => g.name)).toEqual(['Working'])
  expect(s.group).toBe('cg-0')
  await $.turn.complete(done)
  expect(s.group).toBe(null)
  expect(s.moves).toBe(2)
})

test('a grouped session returns to its own group', async ($, on) => {
  const s = sidebar(on, { group: OTHER.id, groups: [OTHER, WORKING] })
  await $.turn.start(turn)
  expect(s.group).toBe(WORKING.id)
  await $.turn.complete(done)
  expect(s.group).toBe(OTHER.id)
})

test('a session already in Working keeps its remembered home', async ($, on) => {
  const s = sidebar(on, { group: OTHER.id, groups: [OTHER, WORKING] })
  await $.turn.start(turn)
  // A second start while still in Working (a reload mid-turn) must not record Working as home.
  await $.turn.start({ ...turn, turnId: 't2' })
  await $.turn.complete({ ...done, turnId: 't2' })
  expect(s.group).toBe(OTHER.id)
})

test('a session moved elsewhere mid-turn is left there', async ($, on) => {
  const s = sidebar(on, { group: null, groups: [WORKING] })
  await $.turn.start(turn)
  s.group = OTHER.id
  await $.turn.complete(done)
  expect(s.group).toBe(OTHER.id)
  expect(s.moves).toBe(1)
})

test('a subagent turn moves nothing', async ($, on) => {
  const s = sidebar(on, { group: null, groups: [] })
  await $.turn.start({ ...turn, agentId: 'a1' })
  await $.turn.complete({ ...done, agentId: 'a1' })
  expect(s.moves).toBe(0)
  expect(s.groups).toEqual([])
})
