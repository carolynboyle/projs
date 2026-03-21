# projs_project_creation_flow.svg

**Path:** docs/images/projs_project_creation_flow.svg
**Syntax:** text
**Generated:** 2026-03-21 11:14:03

```
<svg width="100%" viewBox="0 0 680 980" xmlns="http://www.w3.org/2000/svg">
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
  <style>
    text { font-family: sans-serif; fill: #333; }
    .th { font-size: 14px; font-weight: 500; fill: #1a1a1a; }
    .ts { font-size: 12px; fill: #555; }
    .arr { stroke: #888; stroke-width: 1; fill: none; }

    /* c-gray */
    .c-gray rect, .c-gray polygon { fill: #F1EFE8; stroke: #5F5E5A; }
    .c-gray .th { fill: #2C2C2A; }
    .c-gray .ts { fill: #5F5E5A; }

    /* c-teal */
    .c-teal rect { fill: #E1F5EE; stroke: #0F6E56; }
    .c-teal .th { fill: #085041; }
    .c-teal .ts { fill: #0F6E56; }

    /* c-purple */
    .c-purple rect { fill: #EEEDFE; stroke: #534AB7; }
    .c-purple .th { fill: #26215C; }
    .c-purple .ts { fill: #534AB7; }

    /* c-amber */
    .c-amber rect { fill: #FAEEDA; stroke: #854F0B; }
    .c-amber .th { fill: #412402; }
    .c-amber .ts { fill: #854F0B; }

    /* c-coral */
    .c-coral rect { fill: #FAECE7; stroke: #993C1D; }
    .c-coral .th { fill: #4A1B0C; }
    .c-coral .ts { fill: #993C1D; }

    polygon { fill: #fff; stroke: #888; stroke-width: 0.5; }
  </style>
</defs>

<!-- ── APP STARTS ── -->
<g class="c-gray">
  <rect x="220" y="30" width="240" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="52" text-anchor="middle" dominant-baseline="central">App starts</text>
</g>

<!-- Draft check diamond -->
<line x1="340" y1="74" x2="340" y2="108" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<polygon points="340,108 430,140 340,172 250,140"/>
<text class="ts" x="340" y="136" text-anchor="middle" dominant-baseline="central">Drafts</text>
<text class="ts" x="340" y="153" text-anchor="middle" dominant-baseline="central">exist?</text>

<!-- No → main menu -->
<line x1="250" y1="140" x2="182" y2="140" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<text class="ts" x="215" y="133" text-anchor="middle">no</text>

<!-- Yes → list drafts -->
<line x1="430" y1="140" x2="480" y2="140" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<text class="ts" x="453" y="133" text-anchor="middle">yes</text>

<!-- Resume/Discard box -->
<g class="c-amber">
  <rect x="480" y="112" width="160" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="560" y="133" text-anchor="middle" dominant-baseline="central">List drafts</text>
  <text class="ts" x="560" y="151" text-anchor="middle" dominant-baseline="central">Resume or discard?</text>
</g>

<!-- Discard → delete -->
<line x1="560" y1="168" x2="560" y2="210" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<text class="ts" x="575" y="193">discard</text>
<g class="c-gray">
  <rect x="480" y="210" width="160" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="560" y="232" text-anchor="middle" dominant-baseline="central">Delete draft file</text>
</g>
<!-- Discard loops back to main menu -->
<path d="M560 254 L560 290 L100 290 L100 168" fill="none" stroke="#aaa" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>

<!-- Resume → pre-populate -->
<line x1="560" y1="112" x2="560" y2="58" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<text class="ts" x="575" y="88">resume</text>
<g class="c-teal">
  <rect x="480" y="14" width="160" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="560" y="29" text-anchor="middle" dominant-baseline="central">Pre-populate</text>
  <text class="ts" x="560" y="47" text-anchor="middle" dominant-baseline="central">wizard / prompts</text>
</g>
<!-- Pre-populate dashes to data gathering -->
<path d="M480 36 L340 36 L340 108" fill="none" stroke="#aaa" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>

<!-- ── MAIN MENU ── -->
<g class="c-gray">
  <rect x="20" y="112" width="160" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="100" y="133" text-anchor="middle" dominant-baseline="central">Main menu</text>
  <text class="ts" x="100" y="151" text-anchor="middle" dominant-baseline="central">CLI or GUI</text>
</g>

<!-- Main menu → new project -->
<line x1="100" y1="168" x2="100" y2="320" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<text class="ts" x="108" y="252">new project</text>

<!-- Main menu → import (through diamond) -->
<path d="M180 140 L340 140 L340 172" fill="none" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<text class="ts" x="248" y="133">import</text>

<!-- ── NEW/IMPORT DIAMOND ── -->
<text class="ts" x="340" y="308" text-anchor="middle" font-style="italic">data gathering — CLI prompts or GUI wizard</text>
<polygon points="340,188 430,220 340,252 250,220"/>
<text class="ts" x="340" y="215" text-anchor="middle" dominant-baseline="central">New or</text>
<text class="ts" x="340" y="231" text-anchor="middle" dominant-baseline="central">import?</text>

<!-- New path down -->
<line x1="340" y1="252" x2="340" y2="320" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<text class="ts" x="348" y="288">new</text>

<!-- Import path right -->
<line x1="430" y1="220" x2="490" y2="220" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<text class="ts" x="457" y="213">import</text>
<g class="c-purple">
  <rect x="490" y="192" width="160" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="570" y="213" text-anchor="middle" dominant-baseline="central">Select existing</text>
  <text class="ts" x="570" y="231" text-anchor="middle" dominant-baseline="central">directory</text>
</g>

<!-- ── GATHER DETAILS ── -->
<g class="c-purple">
  <rect x="20" y="320" width="160" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="100" y="341" text-anchor="middle" dominant-baseline="central">Gather details</text>
  <text class="ts" x="100" y="359" text-anchor="middle" dominant-baseline="central">name · lang · license</text>
</g>
<g class="c-purple">
  <rect x="220" y="320" width="240" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="341" text-anchor="middle" dominant-baseline="central">Gather details</text>
  <text class="ts" x="340" y="359" text-anchor="middle" dominant-baseline="central">name · lang · license · path</text>
</g>

<!-- ── CREATE DRAFTS ── -->
<line x1="100" y1="376" x2="100" y2="420" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="340" y1="376" x2="340" y2="420" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="570" y1="248" x2="570" y2="400" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>

<g class="c-teal">
  <rect x="20" y="420" width="160" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="100" y="441" text-anchor="middle" dominant-baseline="central">Create draft</text>
  <text class="ts" x="100" y="459" text-anchor="middle" dominant-baseline="central">draft_[timestamp].json</text>
</g>
<g class="c-teal">
  <rect x="220" y="420" width="240" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="441" text-anchor="middle" dominant-baseline="central">Create draft</text>
  <text class="ts" x="340" y="459" text-anchor="middle" dominant-baseline="central">draft_[timestamp].json</text>
</g>
<g class="c-teal">
  <rect x="490" y="400" width="160" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="570" y="421" text-anchor="middle" dominant-baseline="central">Create draft</text>
  <text class="ts" x="570" y="439" text-anchor="middle" dominant-baseline="central">draft_[timestamp].json</text>
</g>

<!-- ── GATHER SETUP ── -->
<line x1="100" y1="476" x2="100" y2="520" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="340" y1="476" x2="340" y2="520" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="570" y1="456" x2="570" y2="520" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>

<g class="c-purple">
  <rect x="20" y="520" width="160" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="100" y="541" text-anchor="middle" dominant-baseline="central">Gather setup</text>
  <text class="ts" x="100" y="559" text-anchor="middle" dominant-baseline="central">gitignore · commands</text>
</g>
<g class="c-purple">
  <rect x="220" y="520" width="240" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="541" text-anchor="middle" dominant-baseline="central">Gather setup</text>
  <text class="ts" x="340" y="559" text-anchor="middle" dominant-baseline="central">gitignore · commands · docs?</text>
</g>
<g class="c-purple">
  <rect x="490" y="520" width="160" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="570" y="541" text-anchor="middle" dominant-baseline="central">Gather setup</text>
  <text class="ts" x="570" y="559" text-anchor="middle" dominant-baseline="central">gitignore · commands · docs?</text>
</g>

<text class="ts" x="340" y="598" text-anchor="middle" font-style="italic">draft saved after each step</text>

<!-- ── MERGE TO ProjectDraft ── -->
<line x1="100" y1="576" x2="100" y2="635" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="340" y1="576" x2="340" y2="635" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="570" y1="576" x2="570" y2="635" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>

<g class="c-teal">
  <rect x="170" y="635" width="340" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="656" text-anchor="middle" dominant-baseline="central">ProjectDraft assembled</text>
  <text class="ts" x="340" y="674" text-anchor="middle" dominant-baseline="central">all fields · is_import flag · step</text>
</g>
<path d="M100 635 L170 663" fill="none" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<path d="M570 635 L510 663" fill="none" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>

<!-- ── EXECUTE ── -->
<line x1="340" y1="691" x2="340" y2="730" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<text class="ts" x="340" y="722" text-anchor="middle" font-style="italic">shared backend — creator.py</text>

<g class="c-coral">
  <rect x="170" y="732" width="340" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="753" text-anchor="middle" dominant-baseline="central">ProjectCreator.execute(draft)</text>
  <text class="ts" x="340" y="771" text-anchor="middle" dominant-baseline="central">create_directory · readme · docs · gitignore</text>
</g>

<!-- is_import diamond -->
<line x1="340" y1="788" x2="340" y2="830" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<polygon points="340,830 430,860 340,890 250,860"/>
<text class="ts" x="340" y="856" text-anchor="middle" dominant-baseline="central">is_import</text>
<text class="ts" x="340" y="872" text-anchor="middle" dominant-baseline="central">?</text>

<!-- No → mkdir -->
<line x1="250" y1="860" x2="142" y2="860" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<text class="ts" x="194" y="853" text-anchor="middle">no</text>
<g class="c-gray">
  <rect x="20" y="836" width="120" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="80" y="858" text-anchor="middle" dominant-baseline="central">mkdir</text>
</g>
<line x1="80" y1="880" x2="80" y2="924" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<path d="M80 924 L170 938" fill="none" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>

<!-- Yes → skip mkdir -->
<line x1="430" y1="860" x2="488" y2="860" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<text class="ts" x="456" y="853" text-anchor="middle">yes</text>
<g class="c-gray">
  <rect x="490" y="836" width="160" height="44" rx="8" stroke-width="0.5"/>
  <text class="th" x="570" y="858" text-anchor="middle" dominant-baseline="central">skip mkdir</text>
</g>
<line x1="570" y1="880" x2="570" y2="924" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>
<path d="M570 924 L510 938" fill="none" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>

<!-- ── PROMOTE ── -->
<g class="c-teal">
  <rect x="170" y="910" width="340" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="931" text-anchor="middle" dominant-baseline="central">Promote draft → manifest</text>
  <text class="ts" x="340" y="949" text-anchor="middle" dominant-baseline="central">save manifest · delete draft file</text>
</g>
<line x1="340" y1="888" x2="340" y2="908" stroke="#888" stroke-width="1" marker-end="url(#arrow)"/>

</svg>

```
