/**
 * Ranked filename discovery supplements (not replaces) the content index.
 * Logs are intentionally advertised by path only: their contents may be
 * sensitive, huge or remote, and should be read on demand with host approval.
 */
const REF_RE = /\.(?:drawio|md|markdown|mdx|txt|log)$/i;
const EXPLICIT_NAME_RE = /[a-z0-9_.-]+\.(?:drawio|md|markdown|mdx|txt|log)\b/gi;
const EVIDENCE_INTENT_RE =
  /\b(?:diagram|diagrama|drawio|architecture|arquitectura|document|documentacion|documentation|rollover|handoff|evidence|evidencia|logs?|historial|enrollment|fulfill|flow|flujo)\b/i;
const STOP_WORDS = new Set([
  "that", "this", "with", "from", "para", "esta", "este", "como",
  "where", "what", "which", "enrollment", "fulfill", "service",
]);

export function isEvidencePath(path: string): boolean {
  return REF_RE.test(path) && !/(?:^|\/)(?:node_modules|\.git|target)\//i.test(path);
}

export function evidenceFileHints(
  query: string,
  paths: readonly string[],
  limit = 8,
): string[] {
  const explicit = [...query.matchAll(EXPLICIT_NAME_RE)]
    .map((match) => match[0].toLowerCase());
  const focused = explicit.length > 0;
  if (!focused && !EVIDENCE_INTENT_RE.test(query)) return [];
  const words = [...new Set((query.toLowerCase().match(/[a-z0-9]{4,}/g) ?? [])
    .filter((word) => !STOP_WORDS.has(word)))].slice(0, 40);
  const scored: { path: string; score: number }[] = [];
  for (const path of paths) {
    if (!isEvidencePath(path)) continue;
    const lower = path.toLowerCase().replace(/\\/g, "/");
    const name = lower.slice(lower.lastIndexOf("/") + 1);
    const exact = explicit.some((target) => name === target);
    const near = explicit.some((target) => name.includes(target) || target.includes(name));
    const matches = words.filter((word) => lower.includes(word)).length;
    const score = (exact ? 1000 : near ? 120 : 0) + matches * 8
      + (/\.drawio$/i.test(path) && /diagram|drawio|arquitectura|architecture/i.test(query) ? 10 : 0)
      + (/\.log$/i.test(path) && /\blogs?\b/i.test(query) ? 10 : 0);
    if (score > (focused ? 0 : 7)) scored.push({ path, score });
  }
  return scored
    .sort((a, b) => b.score - a.score || a.path.localeCompare(b.path))
    .slice(0, Math.max(0, Math.min(limit, 20)))
    .map((entry) => entry.path);
}

export function renderEvidenceHints(paths: readonly string[]): string {
  if (!paths.length) return "";
  return "Relevant local files (paths only; contents have NOT been read, and logs are not indexed):\n"
    + paths.map((path) => "- " + path).join("\n")
    + "\nOpen the exact file with a workspace read tool, or discover it with file_search/list_dir."
    + " Do not infer that missing indexed matches mean missing project evidence.";
}
