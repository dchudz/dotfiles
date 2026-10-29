import type { EngineInterface, Register, ToolCallResult } from 'claude-code'

const GROUP_NAME = 'Working'
const home = { plugin: 'working-group', key: 'home' } as const

function text(ran: ToolCallResult): string {
  if (ran.deny !== undefined) throw new Error(ran.deny)
  if (ran.isError) throw new Error(ran.text ?? 'tool error')
  return ran.text ?? ''
}

function parse(ran: ToolCallResult): unknown {
  return JSON.parse(text(ran))
}

async function currentGroupId($: EngineInterface): Promise<string | null> {
  const session = parse(
    await $.tool.call({ tool: 'mcp__ccd_session_mgmt__get_session', session_id: 'self' }),
  ) as { group: { id: string } | null }
  return session.group?.id ?? null
}

async function workingGroupId($: EngineInterface): Promise<string> {
  const groups = parse(await $.tool.call({ tool: 'mcp__ccd_sidebar__list_groups' })) as {
    id: string
    name: string
  }[]
  const found = groups.find(g => g.name === GROUP_NAME)
  if (found) return found.id
  const created = parse(
    await $.tool.call({ tool: 'mcp__ccd_sidebar__create_group', name: GROUP_NAME }),
  ) as { id: string }
  return created.id
}

// move_sessions rejects `group_id: null`; Ungrouped is the "sessions" section.
async function moveSelf($: EngineInterface, groupId: string | null): Promise<void> {
  const destination = groupId === null ? { section_id: 'sessions' } : { group_id: groupId }
  text(
    await $.tool.call({ tool: 'mcp__ccd_sidebar__move_sessions', session_ids: ['self'], ...destination }),
  )
}

export const register: Register = on => {
  on('turn.start', async ($, e, next) => {
    if (e.agentId !== undefined) return next(e)
    try {
      const working = await workingGroupId($)
      const current = await currentGroupId($)
      if (current !== working) {
        await $.state.set(home, current)
        await moveSelf($, working)
      }
      $.ui.status(undefined)
    } catch (error) {
      $.ui.status(`working-group: ${(error as Error).message.slice(0, 120)}`)
    }
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    if (e.agentId !== undefined) return next(e)
    try {
      const working = await workingGroupId($)
      const current = await currentGroupId($)
      if (current === working) {
        const { value } = await $.state.get(home)
        await moveSelf($, value ?? null)
      }
    } catch (error) {
      $.ui.status(`working-group: ${(error as Error).message.slice(0, 120)}`)
    }
    return next(e)
  })
}
