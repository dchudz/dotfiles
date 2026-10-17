"""Extract a shareable transcript from a Claude Code session jsonl.

Emits <div class="turn u|c"> blocks: user/assistant messages verbatim (markdown
rendered, HTML-escaped first), tool calls coalesced into bracketed italic
stage-direction lines. Filters harness noise -- see comments on each rule.

Usage:
    uv run --with markdown python extract_transcript.py \
        --jsonl <session.jsonl> --out turns.html --user-name David
Omit --jsonl to auto-pick the newest session file for the current project.
"""

import argparse, glob, html, json, os, re
import markdown

MD = markdown.Markdown(extensions=["fenced_code", "tables", "nl2br", "sane_lists"])

# Tags that wrap harness content *inside* an otherwise-real user message
# (e.g. a /command block sharing an entry with typed text).
WRAPPER_TAGS = ["system-reminder", "local-command-caveat", "command-name",
                "command-message", "command-args", "local-command-stdout"]


def clean_user_text(t):
    for tag in WRAPPER_TAGS:
        t = re.sub(rf"<{tag}>.*?</{tag}>", "", t, flags=re.S)
    return t.strip()


def base(p):
    return p.rstrip("/").split("/")[-1]


def describe_tool(name, inp):
    """One short human line per tool call, or None to omit as noise.

    MCP tools are matched by their trailing action name (server IDs vary per
    installation). Unknown tools fall back to a cleaned-up name -- never drop
    a tool silently unless it's pure bookkeeping.
    """
    inp = inp or {}
    act = name.split("__")[-1] if name.startswith("mcp__") else name
    if name == "Bash":
        return "Ran: " + (inp.get("description") or inp.get("command", "")[:70])
    if name == "Read":
        p = inp.get("file_path", "")
        return "Read fetched attachment" if "tool-results" in p else f"Read {base(p)}"
    if name == "Write":
        return f"Wrote {base(inp.get('file_path', ''))}"
    if name in ("Edit", "MultiEdit", "NotebookEdit"):
        return f"Edited {base(inp.get('file_path', ''))}"
    # Bookkeeping / harness-internal: no reader value.
    if name in ("Grep", "Glob", "ToolSearch", "TodoWrite", "TaskCreate", "TaskUpdate",
                "TaskList", "TaskGet", "ListAgents", "ListSkills", "Skill") \
            or name.startswith("mcp__ccd_session__"):
        return None
    if name == "WebFetch":
        return f"Fetched {inp.get('url', '')[:80]}"
    if name == "WebSearch":
        return f"Web search: {inp.get('query', '')[:70]}"
    if name == "Artifact":
        return "Published/updated the artifact"
    if name == "SendUserFile":
        return "Sent file(s): " + ", ".join(base(f) for f in (inp.get("files") or [])[:4])
    if name == "Agent":
        return f"Ran subagent: {inp.get('description', '')}"
    if name == "AskUserQuestion":
        return "Presented options"
    if "execute_sql" in act:
        return "DB query: " + re.sub(r"\s+", " ", inp.get("query", ""))[:80]
    if act.startswith("slack_"):
        verb = act.replace("slack_", "").replace("_", " ")
        extra = f": {inp.get('query', '')[:50]}" if "search" in verb else ""
        return f"Slack {verb}{extra}"
    if "granola" in act or act in ("get_meeting_transcript", "get_meetings", "list_meetings"):
        return {"get_meeting_transcript": "Read Granola transcript"}.get(act, "Granola: " + act.replace("_", " "))
    if act == "search_calls":
        return f"Searched call recordings: {str(inp.get('query', ''))[:50]}"
    if act == "get_call_details":
        return "Read call transcript"
    if act in ("search_files", "list_recent_files"):
        return f"Searched Drive: {inp.get('query', '')[:50]}"
    if act in ("read_file_content", "download_file_content", "get_file_metadata"):
        return "Read Drive file"
    if act in ("search_threads", "get_thread", "get_message"):
        return "Gmail: " + act.replace("_", " ")
    if "event" in act or "calendar" in act:
        return "Checked calendar"
    if name.startswith("mcp__Claude_Browser__"):
        return "Browser: " + act.replace("_", " ")
    if name.startswith("mcp__"):
        return act.replace("_", " ")
    return name


def md_to_html(t):
    MD.reset()
    return MD.convert(html.escape(t))  # escape first: message text is data, not markup


def find_session_jsonl():
    munged = re.sub(r"[/.]", "-", os.getcwd())
    files = glob.glob(os.path.expanduser(f"~/.claude/projects/{munged}/*.jsonl"))
    if not files:
        raise SystemExit(f"no session files found for project dir {munged}; pass --jsonl")
    return max(files, key=os.path.getmtime)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--user-name", default="User")
    args = ap.parse_args()
    src = args.jsonl or find_session_jsonl()

    turns = []  # [{"role": "u"|"c", "items": [("text"|"act", str), ...]}]

    def add(role, kind, content):
        if turns and turns[-1]["role"] == role:
            turns[-1]["items"].append((kind, content))
        else:
            turns.append({"role": role, "items": [(kind, content)]})

    for line in open(src):
        try:
            e = json.loads(line)
        except Exception:
            continue
        # isMeta: harness-injected content (skill instructions etc.) arrives as
        # user-role messages; without this filter it gets attributed to the user.
        # isSidechain: subagent traffic. isApiErrorMessage: harness error text
        # stored as an assistant message the model never wrote.
        if e.get("isSidechain") or e.get("isMeta") or e.get("isApiErrorMessage"):
            continue
        t = e.get("type")
        if t == "user":
            c = e.get("message", {}).get("content")
            texts, has_img = [], False
            if isinstance(c, str):
                texts = [c]
            elif isinstance(c, list):
                for b in c:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "text":
                        texts.append(b.get("text", ""))
                    elif b.get("type") == "image":
                        has_img = True
            raw = "\n\n".join(texts)
            if "This session is being continued from a previous conversation" in raw:
                continue  # compaction summary, not a user message
            txt = clean_user_text(raw)
            if has_img:
                txt = ("[Screenshot attached]\n\n" + txt).strip()
            if txt:
                add("u", "text", txt)
        elif t == "assistant":
            for b in e.get("message", {}).get("content", []):
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text" and b.get("text", "").strip():
                    add("c", "text", b["text"].strip())
                elif b.get("type") == "tool_use":
                    d = describe_tool(b.get("name", ""), b.get("input"))
                    if d:
                        add("c", "act", d)

    out = []
    for turn in turns:
        who = args.user_name if turn["role"] == "u" else "Claude"
        cls = turn["role"]
        parts, acts = [], []

        def flush_acts():
            if not acts:
                return
            seen, ordered = set(), []
            for a in acts:
                if a not in seen:
                    seen.add(a)
                    ordered.append(a)
            shown = ordered[:10]
            more = len(ordered) - len(shown)
            line = "; ".join(shown) + (f"; … +{more} more tool calls" if more > 0 else "")
            parts.append(f'<p class="act">[{html.escape(line)}]</p>')
            acts.clear()

        for kind, content in turn["items"]:
            if kind == "act":
                acts.append(content)
            else:
                flush_acts()
                parts.append(md_to_html(content))
        flush_acts()
        out.append(f'<div class="turn {cls}"><div class="who">{who}</div><div class="msg">'
                   + "\n".join(parts) + "</div></div>")

    with open(args.out, "w") as f:
        f.write("\n\n".join(out))
    n_u = sum(1 for t in turns if t["role"] == "u")
    print(f"source: {src}")
    print(f"turns: {len(turns)} ({args.user_name} {n_u}, Claude {len(turns) - n_u})")


if __name__ == "__main__":
    main()
