import Link from "next/link";

import type { SiteCount } from "@/lib/queue";

/**
 * The site filter, as links rather than a control.
 *
 * A link needs no client state, keeps the filter in the URL so it can be sent to
 * somebody, and each option carries the count it will narrow to, so the filter
 * says what it does before it is pressed.
 */
export default function SiteFilter({
  token,
  sites,
  selected,
  total,
}: {
  token: string;
  sites: SiteCount[];
  selected: number | null;
  total: number;
}) {
  return (
    <div>
      <p className="label mb-2">Site</p>
      <div className="flex flex-wrap gap-2">
        <Option token={token} site={null} label="All sites" count={total} selected={selected === null} />
        {sites.map((site) => (
          <Option
            key={site.id}
            token={token}
            site={site.id}
            label={site.name}
            count={site.atRisk}
            selected={selected === site.id}
          />
        ))}
      </div>
    </div>
  );
}

function Option({
  token,
  site,
  label,
  count,
  selected,
}: {
  token: string;
  site: number | null;
  label: string;
  count: number;
  selected: boolean;
}) {
  return (
    <Link
      href={site === null ? `/${token}/queue` : `/${token}/queue?site=${site}`}
      aria-current={selected ? "true" : undefined}
      className={`border px-3 py-1.5 text-sm ${
        selected
          ? "border-ink bg-ink text-paper"
          : "border-edge bg-raised text-ink hover:bg-paper"
      }`}
    >
      {label}
      <span className={`figure ml-2 text-xs ${selected ? "text-paper/70" : "text-ink-dim"}`}>
        {count}
      </span>
    </Link>
  );
}
