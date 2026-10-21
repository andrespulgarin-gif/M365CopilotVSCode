import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { resolve, dirname } from "node:path";
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../../..");
const contract = JSON.parse(readFileSync(resolve(here, "fixtures/full-base-contract.json"), "utf8"));
const pkg = JSON.parse(readFileSync(resolve(root, "extensiones/vscode/package.json"), "utf8"));
assert.equal(pkg.version, "3.0.7");
for (const [key, expected] of Object.entries(contract.manifestHashes)) {
  const value = key === "contributes" ? structuredClone(pkg[key]) : pkg[key];
  if (key === "contributes") {
    const tool = value.languageModelTools.find((entry) => entry.name === "m365_run_command");
    assert.ok(tool, "original terminal tool must be preserved");
    assert.deepEqual(tool.inputSchema.properties.timeoutSeconds, {
      type: "integer",
      minimum: 0,
      description: "Optional command timeout in seconds (default 60). 0 disables the command-local timeout; otherwise the requested positive value is honored, including long builds.",
    }, "only the intended terminal-timeout schema may change");
    tool.inputSchema.properties.timeoutSeconds = {
      type: "integer",
      minimum: 1,
      maximum: 300,
      description: "Kill the command after this many seconds (default 60).",
    };
  }
  assert.equal(createHash("sha256").update(JSON.stringify(value)).digest("hex"), expected, `baseline manifest contract changed: ${key}`);
}
for (const [file, expected] of Object.entries(contract.unchangedFiles)) {
  const path = resolve(root, file);
  assert.ok(existsSync(path), `baseline file removed: ${file}`);
  assert.equal(createHash("sha256").update(readFileSync(path)).digest("hex"), expected, `baseline file changed: ${file}`);
}
assert.ok(!JSON.stringify(pkg.contributes).includes("auram365"), "no Lab participant or settings");
console.log(`BASE PARITY PASS: ${Object.keys(contract.unchangedFiles).length} unchanged files; identity, every contribution, approvals, authentication, transport, dependencies and scripts preserved.`);
