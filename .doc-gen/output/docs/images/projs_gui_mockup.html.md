# projs_gui_mockup.html

**Path:** docs/images/projs_gui_mockup.html
**Syntax:** html
**Generated:** 2026-03-25 09:30:03

```html

<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 13px; }
  .win { background: #d4d0c8; border: 2px solid; border-color: #fff #808080 #808080 #fff; width: 100%; }
  .titlebar { background: linear-gradient(to right, #000080, #1084d0); color: white; padding: 3px 6px; font-weight: bold; font-size: 12px; display: flex; justify-content: space-between; align-items: center; }
  .titlebar-btns span { background: #d4d0c8; color: #000; border: 1px solid; border-color: #fff #808080 #808080 #fff; padding: 0 4px; font-size: 11px; margin-left: 2px; cursor: default; }
  .menubar { background: #d4d0c8; padding: 2px 4px; border-bottom: 1px solid #808080; display: flex; gap: 4px; }
  .menubar span { padding: 2px 6px; cursor: default; }
  .menubar span:hover { background: #000080; color: white; }
  .body { display: flex; height: 520px; }
  .sidebar { width: 160px; background: #d4d0c8; border-right: 2px solid; border-color: #808080 #fff #fff #808080; padding: 6px 4px; display: flex; flex-direction: column; gap: 2px; }
  .sidebar-title { font-size: 11px; color: #444; padding: 2px 4px 4px; font-weight: bold; border-bottom: 1px solid #808080; margin-bottom: 4px; }
  .nav-item { padding: 4px 8px; cursor: default; border: 1px solid transparent; display: flex; align-items: center; gap: 6px; }
  .nav-item:hover { border-color: #000080; background: #e8e4d8; }
  .nav-item.active { background: #000080; color: white; border: 1px solid #000040; }
  .nav-step { width: 16px; height: 16px; border: 1px solid; border-color: #808080 #fff #fff #808080; background: #d4d0c8; display: inline-flex; align-items: center; justify-content: center; font-size: 10px; flex-shrink: 0; }
  .nav-item.active .nav-step { background: #1084d0; color: white; border-color: #000040; }
  .nav-item.done .nav-step { background: #008000; color: white; border-color: #005000; }
  .nav-item.done { color: #444; }
  .main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
  .panel-title { background: #d4d0c8; padding: 6px 10px; border-bottom: 2px solid; border-color: #808080 #fff #fff #808080; font-weight: bold; font-size: 12px; display: flex; align-items: center; gap: 8px; }
  .panel-body { flex: 1; padding: 12px; overflow-y: auto; background: #d4d0c8; }
  .groupbox { border: 2px solid; border-color: #808080 #fff #fff #808080; padding: 8px 10px 10px; margin-bottom: 12px; position: relative; }
  .groupbox-label { position: absolute; top: -8px; left: 8px; background: #d4d0c8; padding: 0 4px; font-size: 11px; font-weight: bold; }
  .field-row { display: flex; align-items: center; margin-bottom: 8px; gap: 8px; }
  .field-label { width: 90px; text-align: right; font-size: 12px; flex-shrink: 0; }
  .field-input { flex: 1; border: 2px solid; border-color: #808080 #fff #fff #808080; background: white; padding: 2px 4px; font-size: 12px; height: 22px; }
  .field-input.multiline { height: 48px; resize: none; }
  .dual-list { display: flex; gap: 4px; align-items: center; }
  .listbox-wrap { flex: 1; }
  .listbox-label { font-size: 11px; margin-bottom: 2px; color: #444; }
  .listbox { border: 2px solid; border-color: #808080 #fff #fff #808080; background: white; height: 130px; overflow-y: auto; width: 100%; }
  .list-item { padding: 2px 6px; cursor: default; font-size: 12px; }
  .list-item:hover { background: #000080; color: white; }
  .list-item.selected { background: #000080; color: white; }
  .list-item.muted { color: #888; font-style: italic; }
  .xfer-btns { display: flex; flex-direction: column; gap: 3px; padding: 0 2px; margin-top: 16px; }
  .xbtn { background: #d4d0c8; border: 2px solid; border-color: #fff #808080 #808080 #fff; padding: 2px 6px; font-size: 11px; cursor: default; text-align: center; min-width: 28px; }
  .xbtn:active { border-color: #808080 #fff #fff #808080; }
  .statusbar { background: #d4d0c8; border-top: 2px solid; border-color: #808080 #fff #fff #808080; padding: 2px 8px; display: flex; gap: 12px; font-size: 11px; color: #444; }
  .statusbar-pane { border: 1px solid; border-color: #808080 #fff #fff #808080; padding: 1px 6px; flex: 1; }
  .btn-row { display: flex; justify-content: flex-end; gap: 6px; margin-top: 8px; }
  .btn { background: #d4d0c8; border: 2px solid; border-color: #fff #808080 #808080 #fff; padding: 3px 14px; font-size: 12px; cursor: default; }
  .btn:hover { background: #e8e4d8; }
  .btn.primary { font-weight: bold; }
  .auto-cmd { background: #f0f0e8; border: 1px solid #999; padding: 3px 8px; font-size: 11px; color: #666; font-style: italic; margin-bottom: 6px; }
</style>

<div class="win">
  <div class="titlebar">
    <span>projs — Project Manager</span>
    <div class="titlebar-btns">
      <span>_</span><span>□</span><span>×</span>
    </div>
  </div>
  <div class="menubar">
    <span>File</span><span>Project</span><span>Tools</span><span>View</span><span>Help</span>
  </div>
  <div class="body">
    <div class="sidebar">
      <div class="sidebar-title">New Project</div>
      <div class="nav-item done"><span class="nav-step">✓</span> Details</div>
      <div class="nav-item done"><span class="nav-step">✓</span> Language</div>
      <div class="nav-item active"><span class="nav-step">3</span> Commands</div>
      <div class="nav-item"><span class="nav-step">4</span> Gitignore</div>
      <div class="nav-item"><span class="nav-step">5</span> Review</div>
      <div style="margin-top: auto; border-top: 1px solid #808080; padding-top: 6px;">
        <div class="sidebar-title">Projects</div>
        <div class="nav-item">projs</div>
        <div class="nav-item">story-gems</div>
        <div class="nav-item">keytrack</div>
      </div>
    </div>
    <div class="main">
      <div class="panel-title">
        Step 3 of 5 — Commands
      </div>
      <div class="panel-body">
        <div class="groupbox">
          <span class="groupbox-label">Launch sequence</span>
          <div class="auto-cmd">[auto]  cd ~/projects/newproject  (always runs first, not editable)</div>
          <div class="dual-list">
            <div class="listbox-wrap">
              <div class="listbox-label">Available commands</div>
              <div class="listbox">
                <div class="list-item selected">Create virtual environment</div>
                <div class="list-item">Activate venv</div>
                <div class="list-item">Initialize git</div>
                <div class="list-item">Initial commit</div>
                <div class="list-item">Add custom...</div>
              </div>
            </div>
            <div class="xfer-btns">
              <div class="xbtn">&gt;</div>
              <div class="xbtn">&gt;&gt;</div>
              <div class="xbtn">&lt;</div>
              <div class="xbtn">&lt;&lt;</div>
            </div>
            <div class="listbox-wrap">
              <div class="listbox-label">Selected (in order)</div>
              <div class="listbox">
                <div class="list-item">Create virtual environment</div>
                <div class="list-item selected">Initialize git</div>
                <div class="list-item">nano .</div>
              </div>
            </div>
            <div class="xfer-btns">
              <div class="xbtn">▲</div>
              <div class="xbtn">▼</div>
            </div>
          </div>
        </div>
        <div class="btn-row">
          <div class="btn">← Back</div>
          <div class="btn primary">Next →</div>
        </div>
      </div>
    </div>
  </div>
  <div class="statusbar">
    <div class="statusbar-pane">Project: newproject</div>
    <div class="statusbar-pane">Language: Python</div>
    <div class="statusbar-pane">Step 3 of 5</div>
  </div>
</div>

```
