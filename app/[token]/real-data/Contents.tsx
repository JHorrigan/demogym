import { SECTIONS } from "./sections";

/** The eight sections as a rail at the top, because the page is long enough to want one. */
export default function Contents() {
  return (
    <nav aria-label="On this page" className="border-rule bg-raised border px-5 py-4">
      <p className="label">On this page</p>
      <ol className="mt-3 grid gap-x-10 gap-y-2 sm:grid-cols-2">
        {SECTIONS.map(({ id, title }, index) => (
          <li key={id} className="flex gap-3 text-sm">
            <span className="figure text-ink-faint">{String(index + 1).padStart(2, "0")}</span>
            <a href={`#${id}`} className="text-ink-dim hover:text-ink underline-offset-4 hover:underline">
              {title}
            </a>
          </li>
        ))}
      </ol>
    </nav>
  );
}
