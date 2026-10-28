from pathlib import Path
import json,base64,colorsys,html
ROOT=Path(__file__).resolve().parents[1]
P={
'dark':{'name': 'Hearthstone', 'bg': '#2e3440', 'alt': '#3b4252', 'sidebar': '#343c49', 'raised': '#434c5e', 'fg': '#cac4b8', 'muted': '#b3afa1', 'border': '#556273', 'focus': '#c6b298', 'selection': '#4b4d49', 'highlight': '#514e44', 'red': '#ed9a7f', 'orange': '#eeaf7d', 'gold': '#dbc08b', 'green': '#afcd92', 'cyan': '#89cec4', 'blue': '#93bce0', 'purple': '#c0a4dc', 'pink': '#de9fba', 'active_line': '#323935', 'button_face': '#3f4853', 'button_hover': '#48535f', 'button_pressed': '#303845', 'button_label': '#cac4b8', 'button_primary_label': '#d5c5ae', 'button_edge': '#8d8f86', 'button_light': '#6b747e', 'button_shadow': '#202630', 'bold': '#d8adb3'},
'light':dict(name='Limestone',bg='#eee5d3',alt='#e8ddc6',sidebar='#e3d8c1',raised='#dbcfb5',fg='#463c30',muted='#695a48',border='#b5a383',focus='#7d511a',selection='#d7be8d',highlight='#d9bc79',red='#934738',orange='#805019',gold='#745613',green='#496333',cyan='#2b655d',blue='#3c5e83',purple='#76508a',pink='#874263',bold='#83485c',button_face='#e4d7bd',button_hover='#ded0b3',button_pressed='#d5c5a6',button_label='#463c30',button_primary_label='#69471d',button_edge='#88745b',button_light='#fff7e8',button_shadow='#b1a084')}
def rgb(c):return ', '.join(str(int(c[i:i+2],16)) for i in (1,3,5))
def lum(c):
 v=[int(c[i:i+2],16)/255 for i in (1,3,5)];v=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v];return sum(a*b for a,b in zip(v,[.2126,.7152,.0722]))
def cr(a,b):
 a,b=sorted([lum(a),lum(b)]);return (b+.05)/(a+.05)
contrast={};css=['''/* Cairn Ash 1.6 — stone, bronze, patina. No plugin dependency.
   Keep body/UI/code font preferences. Cairn is reserved for title, H1, H2.
   Color roles and dimensions use Obsidian's native CSS variables.
*/''']
for mode,p in P.items():
 checks={}
 for role in ['fg','bold','muted','focus','red','orange','gold','green','cyan','blue','purple','pink']:
  for surface in ['bg','alt','sidebar']:
   checks[role+'_on_'+surface]=round(cr(p[role],p[surface]),2)
 for surface in ['selection','highlight','raised']:
  checks['fg_on_'+surface]=round(cr(p['fg'],p[surface]),2)
 tint=[int(p['green'][i:i+2],16) for i in (1,3,5)];background=[int(p['bg'][i:i+2],16) for i in (1,3,5)];line='#'+''.join(f'{round(a*.08+b*.92):02x}' for a,b in zip(tint,background));p['active_line']=line
 for role in ['fg','bold','muted','focus','red','orange','gold','green','cyan','blue','purple','pink']:checks[role+'_on_active_line']=round(cr(p[role],line),2)
 checks['accent_button']=round(cr(p['bg'],p['focus']),2)
 assert min(checks.values())>=4.5,(mode,{k:v for k,v in checks.items() if v<4.5})
 contrast[mode]=checks
 h,l,s=colorsys.rgb_to_hls(*[int(p['focus'][i:i+2],16)/255 for i in (1,3,5)])
 neutral=['bg','sidebar','alt','alt','raised','border','border','muted','muted','fg','fg']
 v={f'color-base-{n}':p[c] for n,c in zip(['00','05','10','20','25','30','35','40','50','60','70'],neutral)}
 v['color-base-40']='#736b59' if mode=='dark' else '#b5a383'
 v['color-base-50']='#8d826c' if mode=='dark' else '#95866b'
 v['color-base-60']=p['muted'];v['color-base-70']=p['fg']
 v['color-base-100']=p['fg']
 for name,color in [('red','red'),('orange','orange'),('yellow','gold'),('green','green'),('cyan','cyan'),('blue','blue'),('purple','purple'),('pink','pink')]:
  v['color-'+name]=p[color];v['color-'+name+'-rgb']=rgb(p[color])
 v.update({'accent-h':str(round(h*360)),'accent-s':str(round(s*100))+'%','accent-l':str(round(l*100))+'%',
 'background-primary':p['bg'],'background-primary-alt':p['alt'],'background-secondary':p['sidebar'],'background-secondary-alt':p['alt'],
 'background-modifier-hover':p['raised'],'background-modifier-active-hover':p['raised'],'background-modifier-border':p['border'],'background-modifier-border-hover':p['focus'],'background-modifier-border-focus':p['focus'],
 'background-modifier-form-field':p['sidebar'],'background-modifier-message':p['raised'],
 'text-normal':p['fg'],'text-muted':p['muted'],'text-faint':p['muted'],'text-accent':p['focus'],'text-accent-hover':p['gold'],
 'text-on-accent':p['bg'],'text-selection':p['selection'],'text-highlight-bg':p['highlight'],
 'text-success':p['green'],'text-warning':p['gold'],'text-error':p['red'],'caret-color':p['focus'],
 'interactive-normal':p['alt'],'interactive-hover':p['raised'],'interactive-accent':p['focus'],'interactive-accent-hover':p['gold'],
 'background-modifier-error':('#49302b' if mode=='dark' else '#e9cbc0'),'background-modifier-error-rgb':rgb(p['red']),'background-modifier-success':('#303a2b' if mode=='dark' else '#d7dfc3'),'background-modifier-success-rgb':rgb(p['green']),
 'h1-color':p['red'],'h2-color':p['gold'],'h3-color':p['green'],'h4-color':p['purple'],'h5-color':p['cyan'],'h6-color':p['blue'],
 'cursor-line-background':'rgba('+rgb(p['green'])+', 0.08)','cairn-cursor-rail':p['focus'],'cairn-groove-light':('#697078' if mode=='dark' else '#f8f1e1'),'cairn-groove-dark':('#242a34' if mode=='dark' else '#b8a685'),'cairn-button-face':p.get('button_face',p['alt']),'cairn-button-hover':p.get('button_hover',p['raised']),'cairn-button-pressed':p.get('button_pressed',p['sidebar']),'cairn-button-label':p.get('button_label',p['fg']),'cairn-button-primary-label':p.get('button_primary_label',p['focus']),'cairn-button-edge':p.get('button_edge',p['border']),'cairn-button-light':p.get('button_light',('#6b747e' if mode=='dark' else '#f8f1e1')),'cairn-button-shadow':p.get('button_shadow',('#202630' if mode=='dark' else '#b8a685')),'inline-title-color':p['red'],'bold-color':p['bold'],'italic-color':p['cyan'],
 'link-color':p['focus'],'link-color-hover':p['gold'],'link-external-color':p['blue'],'link-external-color-hover':p['cyan'],'link-unresolved-color':p['purple'],
 'code-background':p['sidebar'],'code-normal':p['fg'],'code-comment':p['muted'],'code-function':p['gold'],'code-keyword':p['purple'],'code-operator':p['cyan'],'code-property':p['blue'],'code-string':p['green'],'code-value':p['orange'],'code-important':p['red'],'code-punctuation':p['muted'],'code-tag':p['red'],
 'nav-item-color':p['muted'],'nav-item-color-hover':p['fg'],'nav-item-color-active':p['focus'],'nav-item-color-selected':p['fg'],'nav-item-background-hover':p['alt'],'nav-item-background-active':p['raised'],
 'tab-background-active':p['bg'],'tab-container-background':p['sidebar'],'tab-text-color':p['muted'],'tab-text-color-focused-active-current':p['focus'],'tab-outline-color':p['border'],'tab-divider-color':p['border'],
 'titlebar-background':p['sidebar'],'titlebar-background-focused':p['sidebar'],'titlebar-text-color-focused':p['muted'],
 'ribbon-background':p['sidebar'],'ribbon-background-collapsed':p['sidebar'],'status-bar-background':p['sidebar'],'status-bar-text-color':p['muted'],'status-bar-border-color':p['border'],
 'icon-color':p['muted'],'icon-color-hover':p['fg'],'icon-color-active':p['focus'],'icon-color-focused':p['focus'],
 'input-placeholder-color':p['muted'],'search-clear-button-color':p['muted'],'search-result-background':p['alt'],
 
 'metadata-label-text-color':p['muted'],'metadata-label-text-color-hover':p['fg'],'metadata-border-color':p['border'],'metadata-property-background-hover':p['alt'],
 'tag-color':p['cyan'],'tag-background':p['sidebar'],'tag-color-hover':p['fg'],'tag-background-hover':p['raised'],'tag-border-color':p['border'],'tag-border-color-hover':p['focus'],
 'checkbox-color':p['focus'],'checkbox-color-hover':p['gold'],'checkbox-border-color':p['muted'],'checkbox-border-color-hover':p['focus'],'checkbox-marker-color':p['bg'],'checklist-done-color':p['muted'],
 'table-border-color':p['border'],'table-header-background':p['sidebar'],'table-header-color':p['fg'],'table-row-alt-background':p['alt'],'table-row-background-hover':p['raised'],'table-selection':p['selection'],
 'blockquote-border-color':p['focus'],'blockquote-background-color':p['alt'],'blockquote-color':p['fg'],
 'hr-color':p['border'],'indentation-guide-color':p['border'],'indentation-guide-color-active':p['focus'],
 'tooltip-color':p['fg'],'tooltip-background':p['sidebar'],'notice-color':p['fg'],'notice-background':p['sidebar'],'modal-background':p['bg'],'modal-border-color':p['focus'],'prompt-background':p['bg'],'prompt-border-color':p['focus'],
 'graph-text':p['fg'],'graph-line':p['border'],'graph-node':p['muted'],'graph-node-focused':p['focus'],'graph-node-tag':p['cyan'],'graph-node-attachment':p['green'],
 'canvas-background':p['sidebar'],'canvas-dot-pattern':p['border'],'canvas-card-label-color':p['fg'],
 'color-base-100':p['fg']})
 css.append('body.theme-'+mode+' {\n'+''.join('  --'+k+': '+value+';\n' for k,value in v.items())+'}\n')
css.append('''body {
  --font-text-theme: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-interface-theme: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-monospace-theme: "JetBrainsMono Nerd Font", "SFMono-Regular", Consolas, monospace;
  --h1-font: "Cairn", var(--font-text); --h2-font: "Cairn", var(--font-text);
  --h3-font: var(--font-text); --h4-font: var(--font-text); --h5-font: var(--font-text); --h6-font: var(--font-text);
  --inline-title-font: "Cairn", var(--font-text); --inline-title-size: 2em; --inline-title-weight: 400;
  --h1-size: 1.8em; --h2-size: 1.46em; --h3-size: 1.18em; --h4-size: 1.05em; --h5-size: 1em; --h6-size: 1em;
  --h1-weight: 400; --h2-weight: 400; --h3-weight: 650; --h4-weight: 650; --h5-weight: 650; --h6-weight: 650;
  --h1-line-height: 1.3; --h2-line-height: 1.35; --heading-spacing: 1.6em;
  --line-height-normal: 1.65; --line-height-tight: 1.4; --file-line-width: 720px;
  --file-margins: 28px 32px; --p-spacing: 1em; --code-size: 0.9em;
  --code-radius: 3px; --code-border-width: 1px;
  --radius-s: 3px; --radius-m: 4px; --radius-l: 6px; --radius-xl: 8px;
  --input-radius: 3px; --button-radius: 4px; --button-corner-shape: bevel; --checkbox-radius: 3px; --input-height: 32px;
  --callout-radius: 3px; --callout-border-width: 1px 1px 1px 3px;
  --callout-border-opacity: 0.5; --callout-padding: 12px 16px; --callout-title-padding: 0;
  --table-header-weight: 650;
  --table-row-alt-background: var(--background-primary-alt);
  --tag-radius: 3px; --tag-border-width: 1px; --tag-padding-x: 0.5em; --tag-padding-y: 0.1em;
  --link-decoration: underline; --link-external-decoration: underline;
  --link-unresolved-opacity: 1; --link-unresolved-decoration-style: dotted;
  --blockquote-border-thickness: 2px; --blockquote-font-style: normal;
  --nav-item-radius: 3px; --nav-item-padding: 5px 8px 5px 18px;
  --nav-item-weight-active: 600; --tab-radius: 3px; --tab-radius-active: 3px 3px 0 0;
  --tab-font-weight: 500; --status-bar-radius: 0; --status-bar-border-width: 1px 0 0 0;
  --modal-radius: 6px;
}
/* More specific than the vault's existing Elbjorg inline-title snippet. */
body.theme-dark .inline-title, body.theme-light .inline-title { font-family: "Cairn", var(--font-text) !important; }
.inline-title { padding-bottom: 0.55em; border-bottom: 3px double var(--background-modifier-border); }
.markdown-rendered h1 { padding-bottom: 0.3em; border-bottom: 1px solid var(--background-modifier-border); }
.markdown-rendered h2 { padding-inline-start: 0.7em; border-inline-start: 3px double var(--cairn-groove-light); }
.markdown-rendered hr { border: 0; border-top: 3px double var(--hr-color); }
.markdown-rendered pre { border: 1px solid var(--background-modifier-border); }
.markdown-rendered :is(td,th), .markdown-source-view.mod-cm6 .cm-table-widget .table-cell-wrapper { padding: 8px 12px; }
.search-result-file-matched-text, .cm-s-obsidian span.obsidian-search-match-highlight { color: var(--text-normal); background-color: var(--text-highlight-bg); }
.markdown-rendered code, .cm-inline-code { font-variant-ligatures: none; }
.markdown-rendered a, .cm-link, .cm-hmd-internal-link { text-underline-offset: 0.2em; }
.nav-file-title.is-active { box-shadow: inset 2px 0 var(--interactive-accent); }
.workspace-tab-header.is-active .workspace-tab-header-inner-title { text-decoration: underline; text-decoration-color: var(--interactive-accent); text-underline-offset: 5px; }
.metadata-container { border-bottom: 1px solid var(--background-modifier-border); padding-bottom: 12px; }
.callout { box-shadow: none; }
/* Never compete with the vault's theorem/math callout styles. */
.callout:not(.theorem-callout) .callout-title { font-family: var(--font-interface); font-weight: 650; }
input[type="text"]:focus-visible, input[type="search"]:focus-visible,
textarea:focus-visible, select:focus-visible, button:focus-visible,
a:focus-visible, [tabindex="0"]:focus-visible {
  outline: 2px solid var(--background-modifier-border-focus); outline-offset: 2px;
}
/* A focused current line, including Vim normal mode. Keep its rail in the
   margin, clear of glyphs; do not add padding or shift lines when focus moves. */
.markdown-source-view.mod-cm6 .cm-editor.cm-focused .cm-line.cm-active {
  position: relative;
  background-color: var(--cursor-line-background);
  box-shadow: none;
  border-radius: 2px;
}
.markdown-source-view.mod-cm6 .cm-editor.cm-focused .cm-line.cm-active::before {
  content: "";
  position: absolute;
  inset-inline-start: -8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: var(--cairn-cursor-rail);
  pointer-events: none;
}
.cm-fat-cursor-mark, .cm-animate-fat-cursor { background-color: var(--interactive-accent); color: var(--text-on-accent); }
/* Native CodeMirror 6 Vim layer: normal/visual/replace use the measured glyph
   as a block; insert mode keeps Obsidian's ordinary caret. */
.markdown-source-view.mod-cm6 .cm-editor.cm-focused > .cm-scroller.cm-vimMode > .cm-vimCursorLayer .cm-fat-cursor {
  background-color: var(--interactive-accent);
  color: var(--text-on-accent);
  border: 0;
  border-radius: 0;
  opacity: 1;
}
.markdown-source-view.mod-cm6 .cm-editor > .cm-scroller.cm-vimMode > .cm-cursorLayer:not(.cm-vimCursorLayer) {
  display: none;
}
.markdown-source-view.mod-cm6 .cm-scroller.cm-vimMode .cm-line {
  caret-color: transparent;
}

/* Shallow stone/bevel cues stay in chrome and rules, away from body glyphs. */
.inline-title { border-bottom-color: var(--cairn-groove-light); box-shadow: 0 1px var(--cairn-groove-dark); }
.markdown-rendered blockquote { border-block: 1px solid var(--background-modifier-border); }
.workspace-tab-header.is-active { box-shadow: inset 0 1px var(--cairn-groove-light), inset 1px 0 var(--cairn-groove-dark), inset -1px 0 var(--cairn-groove-dark); }
.nav-folder-title-content { font-weight: 600; color: var(--text-normal); }
.workspace-sidedock-vault-profile { border-top: 3px double var(--background-modifier-border); }
.workspace-ribbon.mod-primary::before { background-color: var(--ribbon-background); }
.callout:not(.theorem-callout) { box-shadow: inset 0 1px var(--cairn-groove-light); }
/* Filled stone controls: bevel above, recessed edge below, clear state change.
   Native icons, tabs, warning buttons, and switches keep their own geometry. */
button:not(.clickable-icon):not(.mod-warning):not([role="tab"]) {
  background-color: var(--cairn-button-face); color: var(--cairn-button-label);
  border: 1px solid var(--cairn-button-edge); border-radius: 4px 8px 4px 8px;
  padding-inline: 14px; min-height: 34px; corner-shape: bevel;
  box-shadow: inset 0 1px var(--cairn-button-light), inset 0 -2px var(--cairn-button-shadow), 0 1px var(--cairn-button-shadow);
}
button.mod-cta:not(.clickable-icon):not(.mod-warning):not([role="tab"]), button.primary:not(.clickable-icon):not(.mod-warning):not([role="tab"]) { color: var(--cairn-button-primary-label); border-color: var(--interactive-accent); }
button:not(.clickable-icon):not(.mod-warning):not([role="tab"]):enabled:hover { background-color: var(--cairn-button-hover); }
button:not(.clickable-icon):not(.mod-warning):not([role="tab"]):enabled:active {
  background-color: var(--cairn-button-pressed); transform: translateY(1px);
  box-shadow: inset 0 2px var(--cairn-button-shadow), inset 0 -1px var(--cairn-button-light);
}
button:not(.clickable-icon):not(.mod-warning):not([role="tab"]):disabled { box-shadow: none; }

/* Recessed fields and stone ledges. Keep editor text and native focus outlines clear. */
input[type="text"], input[type="search"], input[type="number"], select {
  box-shadow: inset 0 2px var(--cairn-groove-dark), 0 1px var(--cairn-groove-light);
}
.markdown-rendered blockquote {
  border-inline-start-color: var(--cairn-groove-light);
  box-shadow: inset 0 1px var(--cairn-groove-dark), 0 1px var(--cairn-groove-dark);
}
.markdown-rendered pre { box-shadow: inset 0 2px var(--cairn-groove-dark); }
/* Restrained tool marks: a small paired incision identifies the main action. */
button.mod-cta:not(.clickable-icon):not(.mod-warning):not([role="tab"]),
button.primary:not(.clickable-icon):not(.mod-warning):not([role="tab"]) { position: relative; padding-inline-start: 27px; }
button.mod-cta:not(.clickable-icon):not(.mod-warning):not([role="tab"])::before,
button.primary:not(.clickable-icon):not(.mod-warning):not([role="tab"])::before {
  content: ""; position: absolute; left: 11px; top: calc(50% - 5px);
  width: 4px; height: 10px; border-inline: 1px solid var(--interactive-accent);
  transform: skewY(-25deg); pointer-events: none;
}
.workspace-tab-header.is-active { border-top: 1px solid var(--background-modifier-border); }
/* Per-note escape hatches; no settings plugin required. */
.cairn-plain { --h1-font: var(--font-text); --h2-font: var(--font-text); --inline-title-font: var(--font-text); }
body .cairn-plain .inline-title { font-family: var(--font-text) !important; }
.cairn-prose { --font-text: "Cairn", Georgia, serif; --line-height-normal: 1.7; }
@media (max-width: 700px) { body { --file-margins: 20px 18px; } }
@media (prefers-reduced-motion: reduce) { .workspace *, .modal *, .prompt * { scroll-behavior: auto !important; transition: none !important; animation: none !important; } }
@media print {
  body.theme-dark, body.theme-light { --text-normal: #28231d; --text-muted: #5f5445; --background-primary: white; --background-secondary: white; --background-primary-alt: #f1eee6; --inline-title-color: #28231d; }
  .markdown-rendered { color: #28231d; background: white; }
  .inline-title { border-bottom-color: #8a7860; }
  .markdown-rendered :is(h1,h2,h3,h4,h5,h6,strong,em,a) { color: #463c30; }
  .markdown-rendered pre, .markdown-rendered code { color: #28231d; background: #f1eee6; }
}
''')
css.append('''/* Flat tab strips share one silhouette in resting, hovered and current states.
   Scope to the header container: stacked tab spines retain their native layout. */
.workspace-tab-header-container {
  --tab-corner-shape: bevel;
  --tab-radius: var(--cairn-cut-corner, 2px 7px 2px 7px);
  --tab-radius-active: var(--tab-radius);
  --tab-inner-background-hover: transparent;
}
.workspace-tab-header-container .workspace-tab-header {
  border-radius: var(--tab-radius-active);
  corner-shape: var(--tab-corner-shape);
}
.workspace-tab-header-container .workspace-tab-header-inner,
.workspace-tab-header-container .workspace-tab-header.is-before-active .workspace-tab-header-inner {
  border-radius: var(--tab-radius);
  corner-shape: var(--tab-corner-shape);
}
.workspace-tab-header-container .workspace-tab-header:not(.is-active) {
  background-color: var(--background-secondary-alt);
  box-shadow: inset 0 0 0 1px var(--background-modifier-border);
}
.workspace-tab-header-container .workspace-tab-header:not(.is-active):hover {
  background-color: var(--background-modifier-hover);
  box-shadow: inset 0 0 0 1px var(--cairn-groove-light);
}
.workspace-tab-header-container .workspace-tab-header:not(.is-active):hover .workspace-tab-header-inner-title {
  color: var(--text-normal);
}
.workspace-tab-header-container .workspace-tab-header:focus-visible {
  outline: 2px solid var(--background-modifier-border-focus);
  outline-offset: -2px;
}
.workspace-tab-header-container .workspace-tab-header::before,
.workspace-tab-header-container .workspace-tab-header::after { content: none; display: none; }
/* Keep the native close affordance and its visibility rules; dress its hover. */
.workspace-tab-header-container .workspace-tab-header-inner-close-button {
  border-radius: 2px 5px 2px 5px; corner-shape: bevel;
}
''')
(ROOT/'obsidian/Cairn Ash/theme.css').write_text('\n'.join(css))
(ROOT/'obsidian/Cairn Ash/manifest.json').write_text(json.dumps({'name':'Cairn Ash','version':'1.13.0','minAppVersion':'1.6.0','author':'Cairn contributors'},indent=2)+'\n')
(ROOT/'palette.json').write_text(json.dumps({'name':'Cairn Ash','modes':P},indent=2)+'\n')
(ROOT/'contrast.json').write_text(json.dumps({'minimum_target':4.5,'pairs':contrast,'scope':'Specified text/background pairs only, including small labels, code roles, selections, highlights, and filled buttons. Does not establish readability or contrast for every plugin.'},indent=2)+'\n')
# A calmer temporary terminal. Existing global Kitty settings are not edited.
for mode,p in P.items():
 foreground='#b7b4a8' if mode=='dark' else p['fg']
 colors=([p['sidebar'],'#d39482','#a6ba92','#c6b18b','#8faeca','#b09ac6','#86b9b0',foreground,
          '#99a094','#e0a28c','#b4c89e','#d5c098','#a0c0dd','#c0abd4','#96cac0','#c6c1b4'] if mode=='dark' else
         [p['sidebar'],p['red'],p['green'],p['gold'],p['blue'],p['purple'],p['cyan'],p['fg'],
          '#695a48','#853e30','#3f592c','#664a0e','#304f72','#69437c','#235b52','#3e352b'])
 assert min(cr(c,p['bg']) for c in colors[1:])>=4.5
 assert cr(p['fg'],p['selection'])>=4.5
 conf=f'''# Cairn Ash / {p['name']} / isolated terminal trial
font_family JetBrainsMono Nerd Font
bold_font auto
italic_font auto
bold_italic_font auto
font_size 12
background {p['bg']}
foreground {foreground}
selection_background {p['selection']}
selection_foreground {p['fg']}
cursor {p['focus']}
cursor_text_color {p['bg']}
url_color {p['blue']}
active_border_color {p['focus']}
inactive_border_color {p['border']}
window_padding_width 12
background_opacity 1.0
remember_window_size no
initial_window_width 105c
initial_window_height 31c
'''+''.join(f'color{i} {c}\n' for i,c in enumerate(colors))
 (ROOT/'kitty'/f'{mode}.conf').write_text(conf)
 color_only='\n'.join(line for line in conf.splitlines() if line.split(' ',1)[0] in {'background','foreground','selection_background','selection_foreground','cursor','cursor_text_color','url_color','active_border_color','inactive_border_color'} or line.startswith('color'))+'\n'
 (ROOT/'kitty'/f'{mode}-colors.conf').write_text('# Cairn Ash / '+p['name']+' / colors only; preserves font and window preferences\n'+color_only)
 launch=f'''#!/bin/zsh
set -eu
THEME_DIR="${{0:A:h}}"
/usr/bin/open -na /Applications/kitty.app --args --config "$THEME_DIR/kitty/{mode}.conf" --title "Cairn Ash / {p['name']} trial" --directory "$THEME_DIR" /bin/zsh -l
'''
 file=ROOT/f'Try {p["name"]}.command';file.write_text(launch);file.chmod(0o755)
print(json.dumps({m:{k:v for k,v in r.items() if k in ['fg_on_bg','muted_on_bg','fg_on_selection','accent_button']} for m,r in contrast.items()},indent=2))
