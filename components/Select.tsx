/**
 * A squared dropdown, in the same language as the button.
 *
 * A native `select` rather than a built one: it is reachable by keyboard without
 * anything being written, and on a phone it opens the platform's own picker, which
 * is better than anything this project would build for it. The chevron is drawn
 * because the platform's own arrow does not match a squared control.
 */
export default function Select({
  label,
  value,
  options,
  onChange,
  disabled = false,
}: {
  label: string;
  value: string;
  options: readonly string[];
  onChange: (value: string) => void;
  disabled?: boolean;
}) {
  return (
    <label className="block">
      <span className="label mb-2 block">{label}</span>
      <span className="relative block">
        <select
          value={value}
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
          className="border-edge bg-raised text-ink w-full appearance-none border py-1.5 pr-9 pl-3 text-sm capitalize disabled:cursor-not-allowed disabled:opacity-45"
        >
          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        <svg
          aria-hidden
          viewBox="0 0 12 8"
          className="text-ink-dim pointer-events-none absolute top-1/2 right-3 h-2 w-3 -translate-y-1/2"
        >
          <path d="M1 1.5 6 6.5 11 1.5" fill="none" stroke="currentColor" strokeWidth="1.5" />
        </svg>
      </span>
    </label>
  );
}
