export type BandName = "high" | "medium" | "low" | "unflagged";

const FILL: Record<BandName, string> = {
  high: "bg-high",
  medium: "bg-medium",
  low: "bg-low",
  unflagged: "bg-ink-faint",
};

const LABEL: Record<BandName, string> = {
  high: "High",
  medium: "Medium",
  low: "Low",
  unflagged: "Not flagged",
};

/**
 * A band, as a squared tag with a leading block of colour.
 *
 * The word carries the meaning and the colour reinforces it. The three band colours
 * sit within half a stop of each other in lightness, because each has to clear
 * 4.5:1 against the paper, so telling them apart cannot rest on colour alone.
 */
export default function Band({ band }: { band: BandName }) {
  return (
    <span className="border-rule bg-raised inline-flex items-center gap-2 border px-2 py-1 text-xs">
      <span aria-hidden className={`h-2.5 w-2.5 ${FILL[band]}`} />
      {LABEL[band]}
    </span>
  );
}
