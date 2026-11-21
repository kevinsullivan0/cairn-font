import { div } from "gpui-kit";
import { h_flex, Input, InputState, v_flex } from "gpui-base";
import { exists, mkdir, unlink } from "fs/promises";
import {
  appHome, closeOverlay, exec, home, layout, openOverlay, props,
  readTextFile, run, setShared, shared, theme, window, writeTextFile,
} from "herdr";
import {
  artKey, artState, backgroundForArt, findSlot, gallery, localImagePath,
  phaseAt, phases, sameBackground, studies,
} from "./art_model.js";

function preference() {
  return artState(shared(artKey));
}

// Use Herdr's compare-and-swap writer. Its live file reload preserves click
// settings, unlike layout.set, and a retry merges concurrent layout edits.
async function setBackground(background, stillWanted) {
  const path = `${appHome()}/layouts/${gallery}.json`;
  if (background.image && !await exists(`${appHome()}/${background.image}`)) {
    throw new Error("This artwork file is unavailable.");
  }
  for (let retry = 0; retry < 3; retry++) {
    const before = await readTextFile(path);
    if (before === null) throw new Error("The Cairn Gallery layout is unavailable.");
    const tree = JSON.parse(before);
    const sidebar = findSlot(tree, "sidebar");
    if (!sidebar) throw new Error("The Cairn Gallery sidebar is unavailable.");
    if (!stillWanted() || sameBackground(sidebar.background, background)) return;
    sidebar.background = background;
    try {
      await writeTextFile(path, JSON.stringify(tree, null, 2) + "\n", before);
      return;
    } catch (error) {
      if (!String(error).includes("file changed") || retry === 2) throw error;
    }
  }
}

export async function syncAutomaticArt() {
  if (shared("layout") !== gallery || preference().mode !== "auto") return;
  const hour = new Date().getHours();
  const desired = backgroundForArt({ mode: "auto" }, hour);
  const sidebar = findSlot(layout(), "sidebar");
  if (!sidebar || sameBackground(sidebar.background, desired)) return;
  await setBackground(desired, () => shared("layout") === gallery && preference().mode === "auto"
    && phaseAt(new Date().getHours()) === phaseAt(hour));
}

export async function chooseArt(mode, custom = preference().custom) {
  if (shared("layout") !== gallery) throw new Error("Open Cairn Gallery to change its artwork.");
  const previous = preference();
  const next = artState({ mode, custom });
  if (next.mode !== mode) throw new Error("Choose an available artwork.");
  setShared(artKey, next);
  try {
    const hour = new Date().getHours();
    await setBackground(backgroundForArt(next, hour), () => {
      const current = preference();
      return shared("layout") === gallery && current.mode === next.mode && current.custom === next.custom;
    });
  } catch (error) {
    const current = preference();
    if (current.mode === next.mode && current.custom === next.custom) setShared(artKey, previous);
    throw error;
  }
}

export function openArtPicker(at = "pointer") {
  openOverlay({ mod: "cairn-brand", props: { artPicker: true }, kind: "popup", width: 252, at });
}

export function initArtPicker(view) {
  view.pathInput = InputState.new({ placeholder: "/path/to/image.png" });
  view.editingImage = false;
  view.artError = "";
  view.artBusy = false;
}

async function copyImage(value) {
  const source = localImagePath(value, home());
  const suffix = Math.random().toString(16).slice(2) || "0";
  const relative = `backgrounds/cairn/custom/image-${Date.now()}-${suffix}.jpg`;
  const destination = `${appHome()}/${relative}`;
  await mkdir(`${appHome()}/backgrounds/cairn/custom`, { recursive: true });
  try {
    const mac = window()?.platform === "macos";
    const command = mac ? "/usr/bin/sips" : "magick";
    const args = mac
      ? ["-s", "format", "jpeg", "-s", "formatOptions", "87", "-Z", "1408", source, "--out", destination]
      : [source, "-auto-orient", "-resize", "1408x1408>", "-background", "#213930",
         "-alpha", "remove", "-strip", "-quality", "87", destination];
    const result = await exec(command, args, { timeout: 12000 });
    if (result.code !== 0 || !await exists(destination)) throw new Error("Herdr could not read that image.");
    return relative;
  } catch (error) {
    try { await unlink(destination); } catch {}
    throw error;
  }
}

function perform(view, cx, action) {
  if (view.artBusy) return;
  view.artBusy = true;
  view.artError = "";
  cx.notify();
  cx.spawn(async cx => {
    try {
      await action();
      closeOverlay(props()?.overlay);
    } catch (error) {
      view.artError = error.message || String(error);
    } finally {
      view.artBusy = false;
      cx.notify();
    }
  });
}

export async function importImage(value) {
  const old = preference().custom;
  const custom = await copyImage(value);
  try {
    await chooseArt("custom", custom);
  } catch (error) {
    try { await unlink(`${appHome()}/${custom}`); } catch {}
    throw error;
  }
  if (old && old !== custom) {
    try { await unlink(`${appHome()}/${old}`); } catch {}
  }
}

function resetSidebarWidth() {
  const width = 256;
  run("layout.resize", { id: "sidebar", px: width });
  setShared("sidebar.width", width);
  setShared("sidebar.collapsed", false);
  closeOverlay(props()?.overlay);
}

export function renderArtPicker(view) {
  const t = theme();
  const state = preference();
  const select = mode => (_event, cx) => perform(view, cx, () => chooseArt(mode));
  const row = (id, label, click, selected = false) => h_flex().id(id).items_center()
    .justify_between().h(27).px(8).rounded(4).text_size(12)
    .text_color(selected ? t.foreground : t.muted).bg(selected ? t.selected : t.popover)
    .hover(s => s.bg(t.hover).text_color(t.foreground)).cursor_pointer().on_click(click)
    .child(label)
    .when(selected, el => el.child(div().text_color(t.accent).child("✓")));
  const currentPhase = phaseAt(new Date().getHours());
  const phaseName = phases.find(([id]) => currentPhase === id)[1];
  return v_flex().w_full().p(8).gap(4).bg(t.popover).text_color(t.foreground)
    .on_drop((event, cx) => {
      cx.stop_propagation();
      if (event.paths.length === 1) perform(view, cx, () => importImage(event.paths[0]));
      else {
        view.artError = "Drop one image at a time.";
        cx.notify();
      }
    })
    .child(div().px(8).pb(3).text_size(11).text_color(t.dim).child("Sidebar art"))
    .child(row("art-auto", state.mode === "auto" ? `Daylight cycle · ${phaseName}` : "Daylight cycle",
      select("auto"), state.mode === "auto"))
    .child(h_flex().gap(2).children(phases.map(([id, name]) => div().id(`art-${id}`)
      .flex_1().h(23).flex().items_center().justify_center().rounded(4).text_size(10.5)
      .text_color(state.mode === id ? t.foreground : t.muted)
      .bg(state.mode === id ? t.selected : t.surface).hover(s => s.bg(t.hover))
      .cursor_pointer().on_click(select(id)).child(name))))
    .child(div().h(1).my(2).bg(t.border))
    .children(studies.map(([id, label]) => row(`art-${id}`, label, select(id), state.mode === id)))
    .child(row("art-plain", "Plain forest", select("plain"), state.mode === "plain"))
    .when(Boolean(state.custom), el => el.child(row("art-custom", "Custom image", select("custom"), state.mode === "custom")))
    .when(!view.editingImage, el => el.child(row("art-import", state.custom ? "Replace custom image…" : "Use a local image…",
      (_event, cx) => { view.editingImage = true; cx.notify(); })))
    .when(view.editingImage, el => el
      .child(div().px(6).text_size(10.5).text_color(t.dim).child("Drop an image here or paste its path."))
      .child(h_flex().gap(4)
      .child(Input.new(view.pathInput).flex_1().min_w(0).h(28).px(6).rounded(4)
        .border(1).border_color(t.input).bg(t.background).text_color(t.foreground).text_size(11))
      .child(div().id("art-load").px(7).h(28).flex().items_center().rounded(4)
        .text_size(11).bg(t.solid).text_color(t.solid_foreground).cursor_pointer()
        .on_click((_event, cx) => perform(view, cx, () => importImage(view.pathInput.value())))
        .child(view.artBusy ? "…" : "Use"))))
    .child(div().h(1).my(2).bg(t.border))
    .child(row("reset-sidebar-width", "Reset sidebar width to 256 px", resetSidebarWidth))
    .when(Boolean(view.artError), el => el.child(div().px(6).py(3).text_size(11)
      .text_color(t.blocked).child(view.artError)));
}
