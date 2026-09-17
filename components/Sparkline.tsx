const WIDTH = 104;
const HEIGHT = 30;
/** Room for the 2px stroke and the end marker's ring. */
const INSET = 5;

/**
 * Twelve weekly readings as a line, with the most recent marked.
 *
 * `floor` and `ceiling` are passed in rather than taken from this row's own
 * readings, so every sparkline on the screen shares one scale. Scaled to itself, a
 * flat site would draw the same dramatic shape as a site in decline, and the
 * comparison the column exists for would be invented rather than read.
 *
 * The scale spans the readings across the whole estate rather than starting at
 * zero. Anchored at zero, a band running from a tenth to a third of the members
 * compresses into the top of the box and a nine-point move draws as almost
 * nothing. Truncating a value scale usually misleads, and three things stop it
 * here: the rate itself and the move against last week are both on the row as
 * numbers, and the scale is the same on every row, so what the shape supports is a
 * comparison between rows rather than a reading of level. The band is named in the
 * label and under the table.
 *
 * The line is 2px with round joins in the de-emphasised ink. There is no axis, no
 * grid and no per-point tooltip: twelve points across this width leaves them 8px
 * apart, which is under a usable hit target. The reading is carried by the change
 * column beside it and by the twelve figures in the accessible label.
 */
export default function Sparkline({
  values,
  floor,
  ceiling,
  label,
}: {
  values: number[];
  floor: number;
  ceiling: number;
  label: string;
}) {
  if (values.length < 2) {
    return <span className="text-ink-faint text-xs">Not enough history</span>;
  }

  const span = ceiling - floor || 1;
  const points = values.map((value, index) => ({
    x: INSET + (index * (WIDTH - INSET * 2)) / (values.length - 1),
    y: HEIGHT - INSET - ((value - floor) / span) * (HEIGHT - INSET * 2),
  }));
  const last = points[points.length - 1];

  return (
    <svg
      width={WIDTH}
      height={HEIGHT}
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      role="img"
      aria-label={label}
      className="block overflow-visible"
    >
      <title>{label}</title>
      <polyline
        points={points.map(({ x, y }) => `${x},${y}`).join(" ")}
        fill="none"
        stroke="var(--color-ink-faint)"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* The current reading, ringed in the surface colour so it stays legible
          where it sits on the line. */}
      <circle cx={last.x} cy={last.y} r={4} fill="var(--color-ink)" stroke="var(--color-raised)" strokeWidth={2} />
    </svg>
  );
}
