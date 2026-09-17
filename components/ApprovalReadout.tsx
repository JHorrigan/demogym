/**
 * How many approvals needed an edit, out of how many approvals.
 *
 * The only quality figure this project can honestly produce. Accuracy against the
 * generator's own labels would measure whether the scorer recovered a pattern the
 * generator injected; how often a person had to rewrite a draft measures something
 * real.
 *
 * The counts rather than a percentage. Five approvals do not support one, and a
 * figure like 40% implies a precision that is not there.
 */
export default function ApprovalReadout({
  approved,
  edited,
}: {
  approved: number;
  edited: number;
}) {
  return (
    <div className="text-right">
      <p className="label">Edited before approval</p>
      <p className="figure mt-1 text-sm">
        {approved === 0 ? (
          <span className="text-ink-dim">None yet</span>
        ) : (
          <>
            {edited} <span className="text-ink-dim">of</span> {approved}
          </>
        )}
      </p>
    </div>
  );
}
