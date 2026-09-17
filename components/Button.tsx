import type { ButtonHTMLAttributes, ReactNode } from "react";

type Tone = "primary" | "quiet";

const TONE: Record<Tone, string> = {
  primary: "bg-accent text-paper border-accent hover:opacity-90",
  quiet: "bg-raised text-ink border-edge hover:bg-paper",
};

/**
 * A squared button. The edge clears 3:1 against both grounds, so the control is
 * identifiable without relying on its label alone.
 */
export default function Button({
  children,
  tone = "quiet",
  ...rest
}: { children: ReactNode; tone?: Tone } & ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      {...rest}
      className={`border px-3 py-1.5 text-sm transition-opacity disabled:cursor-not-allowed disabled:opacity-45 ${TONE[tone]}`}
    >
      {children}
    </button>
  );
}
