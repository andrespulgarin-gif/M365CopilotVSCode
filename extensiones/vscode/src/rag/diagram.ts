import { inflateRawSync } from "node:zlib";

/**
 * Indexable text extracted from draw.io pages. The returned line numbers are
 * virtual text lines, never original XML source line numbers.
 */
const MAX_SOURCE_CHARS = 3_000_000;
const MAX_PAGE_BYTES = 1_000_000;
const MAX_LABELS_PER_PAGE = 450;
const MAX_RENDERED_CHARS = 60_000;

function decodeEntities(value: string): string {
  const entities: Record<string, string> = {
    amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " ",
  };
  return value.replace(/&(?:#x([0-9a-f]+)|#([0-9]+)|([a-z]+));/gi, (raw, hex, decimal, named) => {
    if (hex || decimal) {
      const point = Number.parseInt(hex ?? decimal, hex ? 16 : 10);
      return Number.isFinite(point) && point >= 0 && point <= 0x10ffff
        ? String.fromCodePoint(point)
        : raw;
    }
    return entities[String(named).toLowerCase()] ?? raw;
  });
}

function attribute(attrs: string, name: string): string | undefined {
  const match = new RegExp("\\b" + name + "\\s*=\\s*([\"'])(.*?)\\1", "i").exec(attrs);
  return match ? decodeEntities(match[2]) : undefined;
}

function textLabel(raw: string | undefined): string {
  if (!raw) return "";
  const decoded = decodeEntities(raw)
    .replace(/<\s*br\s*\/?>/gi, " ")
    .replace(/<\s*\/(?:div|p|li)\s*>/gi, " ")
    .replace(/<[^>]*>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  return decoded.slice(0, 500);
}

function pageXml(body: string): string {
  const trimmed = body.trim();
  if (trimmed.includes("<mxGraphModel") || trimmed.includes("<mxCell")) return trimmed;
  if (!/^[a-z0-9+/=\s]+$/i.test(trimmed) || trimmed.length > MAX_SOURCE_CHARS) return "";
  try {
    const decoded = inflateRawSync(Buffer.from(trimmed, "base64"), {
      maxOutputLength: MAX_PAGE_BYTES,
    }).toString("utf8");
    return decodeURIComponent(decoded);
  } catch {
    return "";
  }
}

function pageText(name: string, body: string): string[] {
  const xml = pageXml(body);
  if (!xml) return ["Page: " + name, "Page content could not be extracted"];
  const nodes = new Map<string, string>();
  const edges: { from: string; to: string; label: string }[] = [];
  let count = 0;
  for (const match of xml.matchAll(/<mxCell\b([^>]*?)\/?>/gi)) {
    if (++count > MAX_LABELS_PER_PAGE * 3) break;
    const attrs = match[1];
    const id = attribute(attrs, "id") ?? "";
    const label = textLabel(attribute(attrs, "value"));
    if (attribute(attrs, "edge") === "1") {
      edges.push({
        from: attribute(attrs, "source") ?? "",
        to: attribute(attrs, "target") ?? "",
        label,
      });
    } else if (label && id) {
      nodes.set(id, label);
    }
  }
  const out = ["Page: " + name];
  for (const label of [...nodes.values()].slice(0, MAX_LABELS_PER_PAGE))
    out.push("Node: " + label);
  for (const edge of edges.slice(0, MAX_LABELS_PER_PAGE)) {
    const from = nodes.get(edge.from) ?? "";
    const to = nodes.get(edge.to) ?? "";
    if (from || to || edge.label)
      out.push("Flow: " + from + " -> " + to + (edge.label ? " [" + edge.label + "]" : ""));
  }
  return out;
}

export function drawioSearchText(source: string): string {
  if (source.length > MAX_SOURCE_CHARS) return "";
  const lines = ["# Draw.io extracted text (virtual lines, not XML line numbers)"];
  const pages = [...source.matchAll(/<diagram\b([^>]*)>([\s\S]*?)<\/diagram>/gi)];
  if (pages.length > 0) {
    for (const page of pages.slice(0, 12)) {
      lines.push(...pageText(attribute(page[1], "name") ?? "Untitled", page[2]));
      if (lines.join("\n").length >= MAX_RENDERED_CHARS) break;
    }
  } else if (source.includes("<mxGraphModel")) {
    lines.push(...pageText("Diagram", source));
  }
  const result = lines.join("\n");
  return lines.length > 1 ? result.slice(0, MAX_RENDERED_CHARS) : "";
}
