// How notifications look. Anything can post one with notify({ title, body,
// level, icon, action }); replace this mod to restyle them all. Click to
// run its action (e.g. go to the agent) and dismiss it.

import { View, div, image, svg, PathBuilder } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { props, openOverlay, closeOverlay, run, theme, checking } from "herdr";

const DOT = { error: "blocked", warning: "working", info: "accent" };
const tablet = PathBuilder.fill().add_polygon([
  [2, 0], ["95%", 0], ["100%", 11], ["100%", "96%"],
  ["99%", "100%"], ["5%", "100%"], [0, "82%"], [0, 2],
]).build();
const seal = PathBuilder.fill().add_polygon([[10, 0], [20, 10], [10, 20], [0, 10]]).build();

function tabletLayer(color, inset, drop = 0) {
  return window.paint_path(tablet, color).absolute()
    .top(inset + drop).bottom(inset - drop).left(inset).right(inset);
}

export default class Toast extends View {
  init() {
    const { overlay, cairnFrame, ...notification } = props() ?? {};
    if (checking() || !overlay || cairnFrame) return;
    // Reframe as a native toast so Herdr still stacks and expires it.
    // The initial notification inherits Herdr's rounded wrapper by default.
    openOverlay({
      mod: "cairn-toast",
      kind: "toast",
      frame: "none",
      notification: { ...notification, cairnFrame: true },
    });
    closeOverlay(overlay);
  }

  render() {
    const t = theme();
    const p = props() ?? {};
    // Herdr 0.1.16 uses info with agent.focus for background completions.
    const done = p.level === "success" || (p.level === "info" && p.action?.name === "agent.focus");
    const color = done ? t.done : t[DOT[p.level] ?? "accent"];
    const login = /^([a-z0-9][a-z0-9_.-]{0,31}) needs login; run hc machine login \1$/.exec(p.body ?? "");
    const command = login ? `hc machine login ${login[1]}` : null;
    const text = (value) => p.fitHeight
      ? div().child(value)
      : div().truncate().child(typeof value === "string" ? value.split("\n", 1)[0] : value);
    return h_flex()
      .id("toast")
      .when(p.fitHeight, (el) => el.w_full().min_h(70).flex_none().py(12))
      .when(!p.fitHeight, (el) => el.size_full())
      .px(18)
      .gap(12)
      .items_center()
      .relative()
      .cursor_pointer()
      .on_hover((inside, cx) => { this.hovered = inside; cx.notify(); })
      .child(tabletLayer("#10141b50", 2, 2))
      .child(tabletLayer("#10141b70", 4, 2))
      .child(tabletLayer(t.accent, 4))
      .child(tabletLayer(this.hovered ? t.raised : t.canvas, 5))
      .on_click(() => {
        if (p.action?.name) run(p.action.name, p.action.args ?? {});
        closeOverlay(p.overlay);
      })
      .child(done
        ? div().relative().size(20).flex_none().flex().items_center().justify_center()
          .child(window.paint_path(seal, color).absolute().top(0).left(0).size_full())
          .child(svg("mods/workspace-chrome/check.svg").size(13).text_color(t.canvas))
        : p.icon ? image(p.icon).w(18).h(18).flex_none()
          : div().size(8).flex_none().bg(color))
      .child(
        v_flex()
          .flex_1()
          .overflow_hidden()
          .child(text(login ? `${login[1]} needs a login: run` : p.title ?? "").font_semibold().text_size(13).text_color(t.foreground))
          .when(!login && Boolean(p.body), (el) => el.child(text(p.body).text_size(12).text_color(t.muted).tooltip(p.body)))
          .when(Boolean(login), (el) => el.child(h_flex().gap(8).items_center()
            .child(div().flex_1().min_w(0).truncate().tooltip(command).text_size(12).text_color(t.muted).child(command))
            .child(div().id("toast-login-copy").flex_none().px(6).py(3).rounded(4).bg(t.raised)
              .text_size(12).text_color(t.foreground).cursor_pointer().hover(s => s.bg(t.hover))
              .on_click((_e, cx) => { cx.stop_propagation(); cx.write_to_clipboard(command); this.copied = true; cx.notify(); })
              .child(this.copied ? "Copied" : "Copy")))),
      );
  }
}
