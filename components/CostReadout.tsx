/**
 * The running cost of every model call the system has made.
 *
 * Read from the token counts the API returned, never estimated, and shown in the
 * currency it was billed in. Converting to pence would need a rate this project has
 * not measured, which would turn the one number here that is a measurement into an
 * estimate. The unit is in the label rather than beside the figure, so the figure
 * stays a figure.
 *
 * It shows zero until somebody drafts something, and zero is the true figure rather
 * than a placeholder: no call has been made.
 */
export default function CostReadout({ calls, cents }: { calls: number; cents: number }) {
  return (
    <div className="text-right">
      <p className="label">Inference cost, US cents</p>
      <p className="figure mt-1 text-sm">
        {cents.toFixed(2)}
        <span className="text-ink-dim ml-3 text-xs">
          {calls} {calls === 1 ? "call" : "calls"}
        </span>
      </p>
    </div>
  );
}
