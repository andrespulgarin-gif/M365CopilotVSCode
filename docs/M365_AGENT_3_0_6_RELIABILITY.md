# M365 Copilot 3.0.6 — focused agent reliability fixes

The **complete** M365CopilotVSCode extension remains the base. This release does not introduce another agent, another set of autonomy settings, new approval dialogs, or an alternative authentication path. It does not include or publish corporate Aura source.

## Problems reproduced from user transcript

- A tool call proposed a `replace` where `oldText` and `newText` were byte-for-byte equal, yet the assistant reported a completed source implementation.
- The requested Java 11 build variant was supplied, but the model selected Java 8, later made unsupported assumptions about which JVM Maven actually used, and did not execute the correct alternative.
- A paste-style text attachment was referenced in `@m365`, but the participant only handled images and Uri/Location code attachments; text-typed reference values were not included.
- Later follow-ups were answered by the VS Code **GitHub Copilot** participant rather than `@m365`, and only that separate participant reported access to terminal history without command execution. This must not be confused with a failure of `@m365`'s own terminal tool.

## What changes

- `tools/replaceText.ts` now reports an explicit, localized `NO_CHANGE` error if a replacement's old and new contents are identical. No edit gets staged, and the model receives a clear instruction to compare existing code and either make a substantive change or acknowledge that no change is needed. Existing Keep/Undo behavior is untouched.
- `src/attachmentText.ts` reads user-provided string and text-MIME chat references (the data payload VS Code exposes for pasted text), without silently clipping their content. It skips implicit references and non-text payloads; unreadable text reports that limitation instead of inventing content.
- `src/participant.ts` and `src/participantPrompts.ts` incorporate readable pasted text into the **existing** `@m365` framing. URI/Location and image handling remain unchanged.
- The existing bilingual `m365copilot.skills.agentSkills` guidance is clearer on checking actual diffs, not calling a no-op implementation, and selecting the user's requested build version while measuring the real process runtime.
- Tests cover no-op editing, long pasted text, binary text references, unreadable attachment data and original-agent framing.
- Package and generated userscript versions are synchronized to 3.0.6. There are no new dependencies or settings.

## What does not change

Original M365 session handling and browser bridge, provider model selection, command execution and approvals, workspace tools, UI, worker delegation, existing loop limits and settings, project-index functions and Git integration. No corporate code is uploaded.

This does **not** make an unreliable model fully reliable. Prompt improvements can help, but the user should verify the actual diff and Maven result. A `-Djava.version` property alone does not establish which JVM runs Maven; a project-specific wrapper may behave differently. Observe `mvn -version` and the actual command output.

## Testing

The CI runs a baseline-preservation test, TypeScript checks, lint for touched production files, build, all existing plus new regression tests, package VSIX and records hashes. Tests use a simulated M365 service and do not establish real-model accuracy.

## User test

1. Install the 3.0.6 VSIX over M365, leave Aura M365 Lab disabled, reload VS Code and select the model normally.
2. Make sure each continuation is addressed to `@m365` if you intend to use our participant; the chat can otherwise switch to the built-in GitHub Copilot participant.
3. Attach a pasted text reference and ask `@m365` to quote a distinctive non-sensitive phrase from it without taking actions. A pasted-text reference must be provided by the host as a string or text-MIME payload for it to be readable.
4. For a no-op edit, expect an explicit `NO_CHANGE` error rather than a false successful edit.
5. For build tasks, verify that the model selects the specified Java version and does not infer successful compilation from editor diagnostics. Do not put real report contents or personal data in debugging prompts.

Branch: `fix-m365-agent-noop-attachments`. `main` is unchanged.
