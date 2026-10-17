# Adding a transcript tab to an existing artifact

Use this mode when the transcript belongs behind an existing deliverable (a briefing, a report) and should share its URL.

## Before touching anything

- If this conversation didn't publish the artifact's latest version, WebFetch its URL and diff against your local copy — other sessions (or the user) may have edited it. Merge onto the live version; never overwrite blind, and never pass `force` unless the user explicitly chooses to discard the other version.
- Recover the artifact's existing favicon (grep the session jsonl for `"favicon"` if unknown) and keep it — a changed favicon reads as a different page.
- Keep the artifact's `<title>` stable.

## Structure

Insert a tab bar as the first child of the page's main container, wrap the existing content in a panel, and append the transcript panel plus a small `showTab` toggle:

```html
<div class="tabbar" role="tablist">
  <button class="tabbtn" role="tab" id="t-doc" aria-selected="true" aria-controls="p-doc" onclick="showTab('doc')">{{Doc name}}</button>
  <button class="tabbtn" role="tab" id="t-tr" aria-selected="false" aria-controls="p-tr" onclick="showTab('tr')">Claude conversation transcript</button>
</div>
<div class="tpanel active" id="p-doc" role="tabpanel">…existing content…</div>
<div class="tpanel" id="p-tr" role="tabpanel">
  <p class="tr-note">…conventions note…</p>
  …turns…
  <p class="tr-note">Transcript current through {{date}}. Later edits appear in the {{doc name}} tab only.</p>
</div>
<script>
function showTab(which) {
  var doc = which === 'doc';
  document.getElementById('p-doc').classList.toggle('active', doc);
  document.getElementById('p-tr').classList.toggle('active', !doc);
  document.getElementById('t-doc').setAttribute('aria-selected', doc);
  document.getElementById('t-tr').setAttribute('aria-selected', !doc);
  window.scrollTo(0, 0);
}
</script>
```

Tab label: "Claude conversation transcript" — not "Conversation transcript", which sounds like a meeting transcript.

## Gotchas learned the hard way

- **Namespace the transcript classes** (`tr-turn`, `tr-who`, `tr-msg`, `tr-note`) before merging — the host document likely already uses names like `.who`. Post-process the extractor output:
  `turns.replace('class="turn ', 'class="tr-turn ').replace('class="who"', 'class="tr-who"').replace('class="msg"', 'class="tr-msg"')` and prefix the CSS accordingly.
- **Panels use `display:none`**, so hash targets inside the hidden panel can't be scrolled to at load. Default the doc panel to active.
- **Jump links:** anchor the exact message `<p>` (consecutive user messages merge into one display turn — a turn-level id lands readers on the wrong message). Scroll with `onclick="document.getElementById(ID).scrollIntoView({behavior:'smooth'});return false;"`; bare `#hash` href navigation is unreliable inside the artifact viewer frame. Add `style="scroll-margin-top:1rem"` to the target.
- **Style the transcript with the host document's tokens** (its CSS variables, fonts) rather than importing a second palette — the two tabs should read as one document.
- **Rebuild from a pristine base** when re-running: assembly edits are not idempotent, so keep the original document and regenerate tabs + panel from it each time rather than editing an already-assembled copy.
