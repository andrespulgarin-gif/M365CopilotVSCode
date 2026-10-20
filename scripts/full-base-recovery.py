# One-time checked migration on the isolated full-M365 branch.
# CI commits the resulting ordinary source edits only after all validation passes.
from pathlib import Path
import json, hashlib
root = Path.cwd()
original_files = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts and 'node_modules' not in p.relative_to(root).parts}
original_manifest = json.loads(original_files['extensiones/vscode/package.json'])
def read(p): return (root / p).read_text()
def write(p, s): (root / p).write_text(s)
def replace(p, a, b):
    s = read(p)
    assert s.count(a) == 1, (p, s.count(a), a[:100])
    write(p, s.replace(a, b))
replace('extensiones/vscode/package.json', '"version": "3.0.4"', '"version": "3.0.5"')
new_en = [
 'ENGINEERING DISCIPLINE:',
 '- Work toward the authorized outcome, not only the next literal command. Necessary reading, tracing, reproduction and validation belong to that task; unrelated refactors, new features and expanded permissions do not.',
 '- Before asking the user about a technical uncertainty, inspect the supplied paths, configuration and available evidence. Ask only when a consequential decision or required access cannot be resolved there. Respect an explicit request to explain, plan, review, or not execute.',
 '- Use the existing host/tool approvals and the user\'s chosen autonomy settings. Do not add a conversational approval after every step of an already authorized task. A denied tool call, missing permission, service refusal or user cancellation is not an obstacle to bypass.',
 '- Preserve working code, existing dependencies and project conventions. Do not introduce test frameworks, comments, dependencies or cleanup against the user\'s constraints. Use the existing tests when allowed.',
 '- Investigate a failure before concluding. Keep the exact command, working directory, actual executable, exit status and causal error separate from hypotheses. A runtime found on PATH is not necessarily the one required by the project; check explicitly supplied executable paths before declaring it missing.',
 '- A failed indexed search is not proof that a file is absent. Read a known file or use another permitted discovery path. Generated logs may not be indexed; inspect their actual content and tail rather than repeatedly searching the same index.',
 '- Truncated output is incomplete evidence. Retrieve the relevant range or tail before naming a cause. A configured registry or mirror is not proof of the endpoint used by a failed request; use the actual transfer error. A missing process exit code is not zero and editor diagnostics are not a successful build.',
 '- Reuse verified paths and findings. After an ordinary technical failure, choose a materially different, relevant diagnostic instead of blindly repeating it or handing runnable steps back to the user. Transient failures may be retried within the existing policy; do not retry denied actions or create endless loops.',
 '- Distinguish the active shell before writing commands. Avoid increasingly nested quoting across PowerShell and cmd; when useful, create and execute a small inspectable script within the authorized scope. Never disable TLS or security policy to make a build pass.',
 '- Continue independent authorized work when one part is blocked. Do not stop merely to announce that an issue was found; explain the verified blocker only after the relevant available diagnostics are exhausted. Do not pretend you executed steps that were merely proposed.',
 '- Verify against the requested outcome and report the concrete files, commands, results and remaining gaps. Separate proposed, applied, built, tested and runtime-verified states. Keep the final response natural: no mandatory evidence IDs, artificial success schema or forced extra tools for a question already answered.',
 '- Review correctness, readability, architecture, security and performance without expanding the task. Preserve user edits and respect a request to stop or change direction.',
]
new_es = [
 'DISCIPLINA DE INGENIERÍA:',
 '- Trabaja hacia el resultado autorizado, no solo hacia el siguiente comando literal. Leer, trazar, reproducir y validar lo necesario pertenece a esa tarea; los refactors ajenos, las nuevas funciones y ampliar permisos no.',
 '- Antes de preguntar al usuario por una incertidumbre técnica, inspecciona las rutas, configuración y evidencia proporcionadas. Pregunta solo si una decisión relevante o un acceso necesario no se resuelve allí. Respeta una petición explícita de explicar, planear, revisar o no ejecutar.',
 '- Usa las aprobaciones existentes del host y de las herramientas y el nivel de autonomía elegido por el usuario. No añadas una aprobación conversacional después de cada paso ya autorizado. Una herramienta denegada, falta de permiso, rechazo del servicio o cancelación no se debe eludir.',
 '- Conserva el código funcional, dependencias y convenciones del proyecto. No introduzcas frameworks de pruebas, comentarios, dependencias ni limpieza contra las restricciones del usuario. Usa las pruebas existentes cuando esté permitido.',
 '- Investiga el fallo antes de concluir. Separa comando exacto, directorio, ejecutable real, estado de salida y error causal de las hipótesis. El runtime encontrado en PATH no es necesariamente el requerido; comprueba las rutas de ejecutables proporcionadas antes de decir que falta.',
 '- Una búsqueda indexada sin resultados no demuestra que el archivo no existe. Lee la ruta conocida o usa otra búsqueda permitida. Los logs generados pueden no estar indexados; examina el contenido real y el final en lugar de repetir búsquedas en el mismo índice.',
 '- Una salida truncada es evidencia incompleta. Recupera el rango o final relevante antes de nombrar la causa. Un registry o mirror configurado no demuestra el endpoint del fallo: usa el error real de transferencia. Un código de salida desconocido no es cero y los diagnósticos del editor no prueban que compiló.',
 '- Reutiliza rutas y hallazgos verificados. Tras un fallo técnico ordinario, usa un diagnóstico pertinente y materialmente distinto en lugar de repetirlo a ciegas o devolver al usuario pasos que puedes ejecutar. Los fallos transitorios pueden reintentarse bajo la política existente; no reintentes acciones denegadas ni crees bucles interminables.',
 '- Distingue el shell activo antes de escribir comandos. Evita acumular comillas anidadas entre PowerShell y cmd; cuando sirva, crea y ejecuta un script pequeño e inspeccionable dentro del alcance autorizado. Nunca desactives TLS ni políticas de seguridad para hacer pasar una compilación.',
 '- Continúa el trabajo independiente autorizado cuando una parte esté bloqueada. No termines solo por encontrar un problema; informa el bloqueo verificado después de agotar los diagnósticos disponibles pertinentes. No presentes acciones propuestas como ejecutadas.',
 '- Verifica el resultado pedido e informa archivos, comandos, resultados y pendientes concretos. Distingue propuesto, aplicado, compilado, probado y verificado en runtime. Mantén una respuesta final natural: sin IDs de evidencia obligatorios, esquema artificial de éxito ni herramientas extra forzadas para una pregunta ya resuelta.',
 '- Revisa corrección, legibilidad, arquitectura, seguridad y rendimiento sin ampliar la tarea. Conserva cambios del usuario y respeta que pida detenerse o cambiar de dirección.',
]
for locale, rules in [('en', new_en), ('es', new_es)]:
    p = f'extensiones/vscode/src/locales/{locale}.ts'
    s = read(p)
    start = s.index('  "prompt.skill.agentSkills": [')
    end = s.index('  "prompt.skill.graphify":', start)
    block = '  "prompt.skill.agentSkills": [\n' + ''.join('    ' + json.dumps(rule, ensure_ascii=False) + ',\n' for rule in rules) + '  ].join("\\n"),\n'
    write(p, s[:start] + block + s[end:])
replace('extensiones/vscode/src/transcript.ts',
 '  return `${text.slice(0, budget.maxChars).trimEnd()}\\n${t("prompt.olderResultShortened", text.length - budget.maxChars)}`;',
 '  const headChars = Math.ceil(Math.max(0, budget.maxChars) * 0.6);\n'
 '  const tailChars = Math.max(0, budget.maxChars - headChars);\n'
 '  const tail = tailChars > 0 ? text.slice(-tailChars) : "";\n'
 '  return `${text.slice(0, headChars).trimEnd()}\\n${t("prompt.olderResultShortened", text.length - headChars - tailChars)}\\n${tail.trimStart()}`;')
replace('extensiones/vscode/src/subagentCore.ts',
 '    const resultText = await executeTool(finishedCall.name, finishedCall.input);\n    lastResultText = resultText;',
 '''    let resultText: string;
    try {
      resultText = await executeTool(finishedCall.name, finishedCall.input);
    } catch (error) {
      if (signal.aborted) {
        return { ok: false, outcome: "cancelled", summary: t("subagent.cancelled"), steps: step };
      }
      resultText = t("tool.error", error instanceof Error ? error.message : String(error));
    }
    if (signal.aborted) {
      return { ok: false, outcome: "cancelled", summary: t("subagent.cancelled"), steps: step };
    }
    lastResultText = resultText;''')
replace('extensiones/vscode/src/subagentCore.ts',
 '''    const text =
      budget.older || budget.duplicate
        ? condenseToolResult(step.result, budget)
        : clip(step.result, budget.maxChars);''',
 '    const text = condenseToolResult(step.result, budget);')
replace('extensiones/vscode/src/participantPrompts.ts',
 '''  return turns
    .filter((turn) => turn.text.trim())
    .slice(-MAX_HISTORY_TURNS)
    .map((turn) => {
      const text = turn.text.trim();
      const clipped =
        text.length > MAX_HISTORY_TURN_CHARS ? `${text.slice(0, MAX_HISTORY_TURN_CHARS)}…` : text;
      return `${turn.role === "user" ? "User" : "Assistant"}: ${clipped}`;
    })
    .join("\\n\\n");''',
 '''  const nonempty = turns.filter((turn) => turn.text.trim());
  const recentStart = Math.max(0, nonempty.length - MAX_HISTORY_TURNS);
  return nonempty
    .filter((turn, index) => turn.role === "user" || index >= recentStart)
    .map((turn) => {
      const text = turn.text.trim();
      const clipped =
        turn.role === "assistant" && text.length > MAX_HISTORY_TURN_CHARS
          ? `${text.slice(0, MAX_HISTORY_TURN_CHARS)}…`
          : text;
      return `${turn.role === "user" ? "User" : "Assistant"}: ${clipped}`;
    })
    .join("\\n\\n");''')
p = 'extensiones/vscode/tools/terminalOutput.ts'
write(p, read(p) + '''
/** Bounded capture which continues retaining the tail after the buffer fills. */
export class TerminalOutputCapture {
  private head = "";
  private tail = "";
  private total = 0;
  private readonly headLimit: number;
  private readonly tailLimit: number;

  constructor(maxChars: number) {
    this.headLimit = Math.ceil(maxChars / 2);
    this.tailLimit = Math.floor(maxChars / 2);
  }

  push(chunk: string): void {
    this.total += chunk.length;
    const room = this.headLimit - this.head.length;
    const prefix = room > 0 ? chunk.slice(0, room) : "";
    this.head += prefix;
    const rest = chunk.slice(prefix.length);
    if (this.tailLimit > 0) {
      this.tail = (this.tail + rest).slice(-this.tailLimit);
    }
  }

  text(): string {
    const omitted = this.total - this.head.length - this.tail.length;
    return omitted > 0
      ? `${this.head}\\n${t("run.charsOmitted", omitted)}\\n${this.tail}`
      : this.head + this.tail;
  }
}
''')
p = 'extensiones/vscode/tools/terminal.ts'
replace(p, 'import { cleanTerminalOutput, truncateOutput } from "./terminalOutput";', 'import { cleanTerminalOutput, truncateOutput, TerminalOutputCapture } from "./terminalOutput";')
replace(p, '  let raw = "";', '  const raw = new TerminalOutputCapture(MAX_OUTPUT_CHARS * 4);')
replace(p, '''        if (raw.length < MAX_OUTPUT_CHARS * 4) {
          raw += chunk.slice(0, MAX_OUTPUT_CHARS * 4 - raw.length);
        }''', '        raw.push(chunk);')
replace(p, 'output: cleanTerminalOutput(raw, command),', 'output: cleanTerminalOutput(raw.text(), command),')
replace(p, 'output: cleanTerminalOutput(`${stdout}${stderr}`, command),', 'output: cleanTerminalOutput(`${stdout}${stderr}` || error?.message || "", command),')
p = root / 'extensiones/vscode/test/e2e.mts'
s = p.read_text()
s = s.replace('  renderTranscript,\n  retrievalText,', '  renderTranscript,\n  condenseToolResult,\n  retrievalText,', 1)
s = s.replace('import { replaceTextOnce } from "../tools/replaceText.ts";', 'import { replaceTextOnce } from "../tools/replaceText.ts";\nimport { TerminalOutputCapture, cleanTerminalOutput, truncateOutput } from "../tools/terminalOutput.ts";', 1)
new = r'''
// Full M365 regressions: keep the original runtime and controls.
function testEvidenceTails() {
  setLocale("en");
  const error = "[ERROR] Transfer failed for https://packages.example.invalid/libs/item.pom: PKIX path building failed";
  const raw = "$ build\r\nBUILD START\r\n" + "progress-only\r\n".repeat(25_000) + error + "\r\nBUILD FAILED\r\n";
  for (const chunkSize of [4096, 8191, raw.length]) {
    const capture = new TerminalOutputCapture(80_000);
    for (let offset = 0; offset < raw.length; offset += chunkSize) {
      capture.push(raw.slice(offset, offset + chunkSize));
    }
    const retained = capture.text();
    assert.ok(retained.length < 81_000, "the existing terminal buffer remains bounded");
    const output = truncateOutput(cleanTerminalOutput(retained, "$ build"), 20_000);
    assert.match(output, /BUILD START/);
    assert.ok(output.includes(error), "the real failing endpoint and causal error survive");
    assert.match(output, /BUILD FAILED/);
    assert.match(output, /characters omitted/);
  }
  const short = new TerminalOutputCapture(80_000);
  short.push("one\r\n");
  short.push("two\r\n");
  assert.equal(short.text(), "one\r\ntwo\r\n");
  const compacted = condenseToolResult("file heading\n" + "noise".repeat(10_000) + error, {
    maxChars: 800, duplicate: false, older: true,
  });
  assert.match(compacted, /file heading/);
  assert.ok(compacted.includes(error), "old-result compaction must retain the causal tail");
  assert.match(compacted, /older result shortened/);
  assert.ok(condenseToolResult("some output", { maxChars: 0, duplicate: false, older: true }).length < 150);
  console.log("  ✓ evidence: terminal and old-result tails retain failures at every tested chunk size");
}

function testPreservedParticipantDirections() {
  setLocale("en");
  const original = "ORIGINAL GOAL\n" + "keep the existing behavior; ".repeat(2_000) + "\nDO NOT INSTALL DEPENDENCIES";
  const turns = [
    { role: "user" as const, text: original },
    ...Array.from({ length: 8 }, (_, i) => ({ role: "assistant" as const, text: "status " + i })),
    { role: "user" as const, text: "Use the provided runtime, not whichever one is on PATH." },
  ];
  const framing = buildParticipantFraming({ command: undefined, request: "Continue the same task", history: turns });
  assert.ok(framing.includes(original), "the original goal is neither clipped nor dropped on Continue");
  assert.equal(framing.split(original).length - 1, 1, "do not duplicate original directions");
  assert.match(framing, /Use the provided runtime/);
  assert.match(framing, /Continue the same task$/);
  for (const language of ["en", "es"] as const) {
    setLocale(language);
    const enabled = renderSkills({ ponytail: false, agentSkills: true, graphify: false });
    assert.match(enabled, /PATH/);
    assert.match(enabled, /TLS/);
    assert.ok(enabled.includes(language === "en" ? "denied tool call" : "herramienta denegada"));
    assert.ok(enabled.includes(language === "en" ? "no mandatory evidence IDs" : "sin IDs de evidencia obligatorios"));
    assert.equal(renderSkills({ ponytail: false, agentSkills: false, graphify: false }), "");
  }
  setLocale("es");
  console.log("  ✓ full @m365: long user constraints survive follow-ups; existing skill switch still works");
}

async function testToolFailureRemainsEvidence() {
  setLocale("en");
  const prompts: string[] = [];
  const calls: string[] = [];
  const server = await startScriptedServer(
    (index) => index === 0
      ? `<m365_tool_call>{"name":"${M365_TOOL_NAMES.runCommand}","input":{"command":"build"}}</m365_tool_call>`
      : index === 1
        ? `<m365_tool_call>{"name":"${M365_TOOL_NAMES.readFile}","input":{"path":"build.log"}}</m365_tool_call>`
        : "The dependency transport failed; source compilation has not been reached.",
    (frame) => prompts.push(String(frame.arguments[0].message.text)),
  );
  try {
    const result = await runToolLoop({
      framing: "Investigate the failed build without changing permissions.",
      profile: makeProfile(server.port), tone: null, maxSteps: 4,
      signal: new AbortController().signal,
      offeredTools: [{ name: M365_TOOL_NAMES.runCommand }, { name: M365_TOOL_NAMES.readFile }],
      endpointBase: mockBase(server.port),
      executeTool: async (name) => {
        calls.push(name);
        if (name === M365_TOOL_NAMES.runCommand) throw new Error("Process launch failed: executable not found");
        return "header\n" + "progress".repeat(10_000) + "\nCAUSAL_ERROR https://packages.example.invalid/item.pom PKIX";
      },
    });
    assert.equal(result.outcome, "done");
    assert.deepEqual(calls, [M365_TOOL_NAMES.runCommand, M365_TOOL_NAMES.readFile]);
    assert.match(prompts[1]!, /Process launch failed: executable not found/);
    assert.match(prompts[2]!, /CAUSAL_ERROR https:\/\/packages\.example\.invalid\/item\.pom PKIX/);
    assert.equal(prompts.length, 3);
  } finally { server.close(); }
  setLocale("es");
  console.log("  ✓ full loop: rejected executor becomes evidence; a different diagnostic and its causal tail reach the next turn");
}

async function testNoLabLimitsOrCompletionGate() {
  setLocale("en");
  let calls = 0;
  const server = await startScriptedServer((index) => index < 14
    ? `<m365_tool_call>{"name":"${M365_TOOL_NAMES.readFile}","input":{"path":"state.txt"}}</m365_tool_call>`
    : "Done. The requested investigation is complete.");
  try {
    const result = await runToolLoop({
      framing: "Read the changing state while working on the same investigation.",
      profile: makeProfile(server.port), tone: null, maxSteps: Number.POSITIVE_INFINITY,
      maxWallClockMs: Number.POSITIVE_INFINITY, signal: new AbortController().signal,
      offeredTools: [{ name: M365_TOOL_NAMES.readFile }], endpointBase: mockBase(server.port),
      executeTool: async () => { calls += 1; return "state " + calls; },
    });
    assert.equal(calls, 14, "no imported 12-call cap or four-identical-operation veto");
    assert.equal(result.outcome, "done");
    assert.equal(result.summary, "Done. The requested investigation is complete.");
  } finally { server.close(); }
  let turns = 0;
  const controller = new AbortController();
  const cancelled = await startScriptedServer(() => {
    turns += 1;
    return `<m365_tool_call>{"name":"${M365_TOOL_NAMES.readFile}","input":{"path":"state.txt"}}</m365_tool_call>`;
  });
  try {
    const result = await runToolLoop({
      framing: "Inspect the state.", profile: makeProfile(cancelled.port), tone: null, maxSteps: 5,
      signal: controller.signal, offeredTools: [{ name: M365_TOOL_NAMES.readFile }],
      endpointBase: mockBase(cancelled.port),
      executeTool: async () => { controller.abort(); throw new Error("cancelled by user"); },
    });
    assert.equal(result.outcome, "cancelled");
    assert.equal(turns, 1, "cancellation is not turned into an automatic recovery attempt");
  } finally { cancelled.close(); }
  setLocale("es");
  console.log("  ✓ native loop: user budgets, normal final text and cancellation preserved; no Lab gates");
}

'''
assert s.count('async function main() {') == 1
s = s.replace('async function main() {', new + '\nasync function main() {')
s = s.replace('  testSkills();\n', '  testSkills();\n  testEvidenceTails();\n  testPreservedParticipantDirections();\n', 1)
s = s.replace('  await testToolLoopForcedRetry();\n', '  await testToolLoopForcedRetry();\n  await testToolFailureRemainsEvidence();\n  await testNoLabLimitsOrCompletionGate();\n', 1)
p.write_text(s)
keys = ['name','publisher','main','engines','activationEvents','extensionDependencies','extensionKind','contributes','dependencies','devDependencies','scripts']
contract = {'sourceCommit':'c062fe6a5d032068600f909d17ea36cd2dae663c','manifestHashes':{k:hashlib.sha256(json.dumps(original_manifest[k],separators=(',',':'),ensure_ascii=False).encode()).hexdigest() for k in keys if k in original_manifest},'unchangedFiles':{}}
for rel, original in original_files.items():
    current = root / rel
    if not current.is_file() or current.read_bytes() != original: continue
    if rel.startswith(('packages/core/','extensiones/browser/','extensiones/vscode/src/','extensiones/vscode/tools/','extensiones/vscode/userscript/')) or rel in ['pnpm-lock.yaml','pnpm-workspace.yaml','package.json']:
        contract['unchangedFiles'][rel] = hashlib.sha256(original).hexdigest()
fix = root / 'extensiones/vscode/test/fixtures'
fix.mkdir(exist_ok=True)
(fix / 'full-base-contract.json').write_text(json.dumps(contract,indent=2,ensure_ascii=False)+'\n')
(root / 'extensiones/vscode/test/base-parity.mjs').write_text('''import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { resolve, dirname } from "node:path";
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../../..");
const contract = JSON.parse(readFileSync(resolve(here, "fixtures/full-base-contract.json"), "utf8"));
const pkg = JSON.parse(readFileSync(resolve(root, "extensiones/vscode/package.json"), "utf8"));
assert.equal(pkg.version, "3.0.5");
for (const [key, expected] of Object.entries(contract.manifestHashes)) {
  assert.equal(createHash("sha256").update(JSON.stringify(pkg[key])).digest("hex"), expected, `baseline manifest contract changed: ${key}`);
}
for (const [file, expected] of Object.entries(contract.unchangedFiles)) {
  const path = resolve(root, file);
  assert.ok(existsSync(path), `baseline file removed: ${file}`);
  assert.equal(createHash("sha256").update(readFileSync(path)).digest("hex"), expected, `baseline file changed: ${file}`);
}
assert.ok(!JSON.stringify(pkg.contributes).includes("auram365"), "no Lab participant or settings");
console.log(`BASE PARITY PASS: ${Object.keys(contract.unchangedFiles).length} unchanged files; identity, every contribution, approvals, authentication, transport, dependencies and scripts preserved.`);
''')
print('Full M365 migration applied; unchanged baseline file hashes:', len(contract['unchangedFiles']))
Path(__file__).unlink()
