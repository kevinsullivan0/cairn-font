// The four views are one work. A manual selection holds until Auto is chosen again.
export const gallery = "cairn-gallery";
export const artKey = "cairn.sidebar.art";
const directory = "backgrounds/cairn";
export const phases = [
  ["morning", "Morning"],
  ["afternoon", "Afternoon"],
  ["evening", "Evening"],
  ["night", "Night"],
];
export const studies = [
  ["beacon", "The Last Beacon", "the-last-beacon.png"],
  ["crossing", "The High Crossing", "the-high-crossing.png"],
  ["gardens", "Windward Gardens", "windward-gardens.png"],
];

export function phaseAt(hour) {
  if (hour >= 5 && hour < 12) return "morning";
  if (hour >= 12 && hour < 17) return "afternoon";
  if (hour >= 17 && hour < 21) return "evening";
  return "night";
}

export function artState(record) {
  const validCustom = typeof record?.custom === "string" &&
    /^backgrounds\/cairn\/custom\/image-[0-9]+-[0-9a-f]+\.jpg$/.test(record.custom);
  const custom = validCustom ? record.custom : null;
  const all = ["auto", "plain", ...phases.map(([id]) => id), ...studies.map(([id]) => id)];
  const mode = all.includes(record?.mode) || (record?.mode === "custom" && custom)
    ? record.mode
    : "auto";
  return { mode, custom };
}

export function backgroundForArt(record, hour) {
  const { mode, custom } = artState(record);
  if (mode === "plain") return "#213930";
  if (mode === "custom") return { image: custom, fit: "cover" };
  const preset = studies.find(([id]) => id === mode);
  if (preset) return { image: `${directory}/${preset[2]}`, fit: "cover" };
  const phase = mode === "auto" ? phaseAt(hour) : mode;
  return { image: `${directory}/cycle/${phase}.jpg`, fit: "cover" };
}

export function sameBackground(left, right) {
  if (typeof left === "string" || typeof right === "string") return left === right;
  return left?.image === right?.image && left?.fit === right?.fit;
}

export function findSlot(node, id) {
  if (node?.id === id) return node;
  for (const child of node?.children ?? []) {
    const found = findSlot(child, id);
    if (found) return found;
  }
  return null;
}

export function localImagePath(value, userHome) {
  let path = value.trim();
  if ((path.startsWith("'") && path.endsWith("'")) || (path.startsWith('"') && path.endsWith('"'))) {
    path = path.slice(1, -1);
  }
  if (path.startsWith("file:///")) path = decodeURIComponent(path.slice(7));
  if (path.startsWith("~/")) path = `${userHome}/${path.slice(2)}`;
  if (!path.startsWith("/") || /[\0\r\n]/.test(path) ||
      !/\.(png|jpe?g|heic|webp|tiff?)$/i.test(path)) {
    throw new Error("Paste the full path to a PNG, JPEG, WebP, HEIC, or TIFF image.");
  }
  return path;
}
