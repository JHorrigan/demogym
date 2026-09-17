/**
 * The running cost of every model call the system has made.
 *
 * Read from the token counts the API returns, never estimated. It shows zero until
 * somebody drafts something, and zero is the true figure rather than a placeholder:
 * no call has been made. 011 wires it to the stored rows.
 */
export default function CostReadout({ calls, pence }: { calls: number; pence: number }) {
  return (
    <div className="text-right">
      <p className="label">Inference cost</p>
      <p className="figure mt-1 text-sm">
        {pence.toFixed(2)}p
        <span className="text-ink-dim ml-2 text-xs">
          {calls} {calls === 1 ? "call" : "calls"}
        </span>
      </p>
    </div>
  );
}
