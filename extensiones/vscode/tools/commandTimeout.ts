/**
 * An individual terminal command's timeout is independent of the model's
 * per-response timeout and the chat participant's total task duration.
 * A requested value of 0 disables only this command-local timer.
 */
export const DEFAULT_COMMAND_TIMEOUT_SECONDS = 60;

/**
 * Node's setTimeout() wraps intervals larger than 2^31 - 1 milliseconds to
 * approximately 1 ms. Schedule large values in safe pieces rather than
 * accidentally killing a long-running build immediately.
 */
const MAX_NODE_TIMEOUT_MS = 2_147_483_647;
const MAX_NODE_TIMEOUT = BigInt(MAX_NODE_TIMEOUT_MS);

export interface CommandTimerScheduler {
  set(callback: () => void, delayMs: number): unknown;
  clear(handle: unknown): void;
}

const nativeScheduler: CommandTimerScheduler = {
  set: (callback, delayMs) => setTimeout(callback, delayMs),
  clear: (handle) => clearTimeout(handle as ReturnType<typeof setTimeout>),
};

/** Undefined preserves the existing one-minute default; 0 means unlimited. */
export function commandTimeoutSeconds(requested: unknown): number {
  if (requested === undefined || requested === null) return DEFAULT_COMMAND_TIMEOUT_SECONDS;
  if (typeof requested !== "number" || !Number.isSafeInteger(requested) || requested < 0) {
    throw new RangeError("timeoutSeconds must be a non-negative safe integer (0 disables the timeout).");
  }
  return requested;
}

/**
 * Start a cancellable timeout. No timer is scheduled for zero. All other
 * positive safe-integer second values are honoured without a 300s cap.
 * The optional scheduler makes long-delay and cancellation tests deterministic.
 */
export function startCommandTimeout(
  timeoutSeconds: number,
  onTimeout: () => void,
  scheduler: CommandTimerScheduler = nativeScheduler,
): () => void {
  if (!Number.isSafeInteger(timeoutSeconds) || timeoutSeconds < 0) {
    throw new RangeError("timeoutSeconds must be a non-negative safe integer.");
  }
  if (timeoutSeconds === 0) return () => {};

  let remaining = BigInt(timeoutSeconds) * 1_000n;
  let active = true;
  let handle: unknown;
  const arm = () => {
    const delay = remaining > MAX_NODE_TIMEOUT ? MAX_NODE_TIMEOUT : remaining;
    handle = scheduler.set(() => {
      if (!active) return;
      remaining -= delay;
      if (remaining === 0n) {
        active = false;
        onTimeout();
      } else {
        arm();
      }
    }, Number(delay));
  };
  arm();
  return () => {
    if (!active) return;
    active = false;
    scheduler.clear(handle);
  };
}
