/**
 * Text pasted into a VS Code chat may arrive as a ChatPromptReference.value,
 * not as part of ChatRequest.prompt. Keep these user-supplied bytes in the
 * participant's framing instead of inventing an unavailable attachment.
 *
 * This module intentionally does not import vscode, so its behavior can be
 * regression-tested with ordinary reference-shaped fixtures.
 */
export interface TextAttachmentReference {
  readonly id: string;
  readonly modelDescription?: string;
  readonly value: unknown;
}

export interface AttachedText {
  readonly name: string;
  readonly text: string;
}

const TEXT_CONTENT_TYPE = /^(?:text\/|application\/(?:json|xml|yaml|x-yaml|javascript|typescript|x-javascript|x-typescript|markdown|x-markdown)(?:;|$))/i;

export async function pastedTextOf(
  references: readonly TextAttachmentReference[],
): Promise<AttachedText[]> {
  const collected: AttachedText[] = [];
  for (const reference of references) {
    if (reference.id.startsWith("vscode.implicit")) continue;
    const name = reference.modelDescription?.trim() || reference.id;
    const value = reference.value;
    if (typeof value === "string") {
      if (value.trim()) collected.push({ name, text: value });
      continue;
    }
    if (!value || typeof value !== "object") continue;
    const binary = value as { mimeType?: unknown; data?: unknown };
    if (typeof binary.mimeType !== "string" || !TEXT_CONTENT_TYPE.test(binary.mimeType)) {
      continue;
    }
    if (typeof binary.data !== "function") {
      collected.push({ name, text: "[Attached text is not readable by this extension.]" });
      continue;
    }
    try {
      const bytes: unknown = await (binary.data as () => Promise<unknown>)();
      if (!(bytes instanceof Uint8Array)) {
        collected.push({ name, text: "[Attached text could not be retrieved as bytes.]" });
        continue;
      }
      const text = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
      if (text.trim()) collected.push({ name, text });
    } catch {
      collected.push({ name, text: "[Attached text could not be read; it has not been supplied to the model.]" });
    }
  }
  return collected;
}

export function renderPastedText(attachments: readonly AttachedText[]): string {
  if (!attachments.length) return "";
  return attachments.map(({ name, text }) =>
    `[User-provided attached text: ${name}]\n${text}\n[End attached text: ${name}]`,
  ).join("\n\n");
}
