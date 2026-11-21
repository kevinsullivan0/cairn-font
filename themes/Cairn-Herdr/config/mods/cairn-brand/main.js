import { View, div, image, svg } from "gpui-kit";
import { h_flex, v_flex } from "gpui-base";
import { checking, nextCommand, notify, theme, run, props, window, shared, setShared, updates, layout } from "herdr";
import { chooseArt, initArtPicker, openArtPicker, renderArtPicker, syncAutomaticArt } from "./art_picker.js";

function find(node, id) {
  if (node?.id === id) return node;
  for (const child of node?.children ?? []) {
    const found = find(child, id);
    if (found) return found;
  }
  return null;
}

// The sidebar's rail goes by its width, not a flag: dragging its edge narrows it too.
const narrow = () => (find(layout(), "sidebar")?.size?.px ?? Infinity) < 160;

// To the rail (on macOS wide enough for the traffic lights), or back to the width it had.
function toggleSidebar() {
  const width = find(layout(), "sidebar")?.size?.px;
  if (!narrow()) setShared("sidebar.width", width);
  // Mods edited before the rail went by width still read the flag.
  setShared("sidebar.collapsed", !narrow());
  run("layout.resize", { id: "sidebar", px: narrow() ? (shared("sidebar.width") ?? 268) : window()?.platform === "macos" ? 76 : 44 });
}

export default class WorkspaceChrome extends View {
  init(_props, cx) {
    if (props()?.artPicker) {
      initArtPicker(this);
      return;
    }
    if (!props()?.galleryArt || checking()) return;
    const update = () => syncAutomaticArt().catch(() => {});
    cx.spawn(async () => { await update(); });
    cx.timer.every(30_000, () => { return update(); });
    cx.spawn(async () => {
      for (;;) {
        const command = await nextCommand();
        if (command === "art") openArtPicker({ x: 16, y: 52 });
        else if (command.startsWith("art-")) {
          try { await chooseArt(command.slice(4)); }
          catch (error) { notify({ title: "Sidebar art", body: error.message || String(error), level: "error" }); }
        }
      }
    });
  }

  button(id, label, action, tooltip) {
    const t = theme();
    return div().id(id).size(26).flex_none().flex().items_center().justify_center().rounded(6).text_color(t.muted).hover(s => s.bg(t.hover).text_color(t.foreground))
      .when(Boolean(tooltip), el => el.tooltip(tooltip))
      .on_mouse_down("left", (_e, cx) => cx.stop_propagation()).on_click(action).child(label);
  }
  render() {
    if (props()?.artPicker) return renderArtPicker(this);
    const t = theme();
    const collapsed = narrow();
    if (props()?.footer) {
      const row = (id, icon, label, dim, action) => h_flex().id(id).h(28).px(8).gap(9).items_center().rounded(8)
        .when(collapsed, el => el.relative().w(32).px(0).justify_center().tooltip(label))
        .text_color(dim ? t.dim : t.muted).hover(s => s.bg(t.hover).text_color(t.foreground)).cursor_pointer()
        .on_click(action).child(svg(`mods/cairn-brand/${icon}.svg`).size(14))
        .when(!collapsed, el => el.child(label));
      const ready = div().size(6).rounded_full().bg(t.accent);
      return v_flex().relative().size_full().bg(t.chrome).border_t(1).border_color(t.border).px(8).pt(4).pb(8).text_size(13)
        .when(collapsed, el => el.px(0).items_center())
        .child(row("settings", "settings", "Settings", false, () => run("app.settings"))
          .when(Boolean(updates().app.ready), el => el.child(collapsed ? ready.absolute().top(5).right(6) : ready)))
        .child(row("machine", "plus", "Add machine", true, () => run("mod.open", { name: "machine-add" })))
        .when(Boolean(props()?.galleryArt) && !collapsed, el =>
          el.child(this.button("sidebar-art", svg("mods/cairn-brand/art.svg").size(16),
            () => openArtPicker(), "Sidebar art").absolute().top(5).right(9)));
    }
    return h_flex().size_full().bg(t.chrome).pl(collapsed ? 6 : 14).pr(10).gap(4).items_center().text_size(13.5)
      .when(window()?.platform === "macos" && !window()?.fullscreen && !collapsed, el => el.pl(76))
      .when(!collapsed, el => el.child(h_flex().flex_1().gap(8).items_center().child(image("mods/cairn-brand/cairn-inlay.svg").w(22).h(10).flex_none()).child(div().font_family("Cairn").text_size(18).font_semibold().text_color(t.foreground).child(props()?.title ?? "Herdr"))))
      .when(!collapsed, el => el.child(this.button("search", image("mods/cairn-brand/compass-vector.svg").size(17),
        () => run("mod.open", { name: "picker-clock" }), "Find a tab")))
      // On the macOS rail the traffic lights fill the row; the agents list's » unfolds it.
      .when(!(collapsed && window()?.platform === "macos"), el => el.child(this.button("sidebar-toggle", svg("mods/cairn-brand/sidebar.svg").size(15), toggleSidebar)));
  }
}
