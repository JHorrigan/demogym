import { Empty } from "@/components/States";
import { sql } from "@/lib/database";

export const dynamic = "force-dynamic";

/**
 * A placeholder until 009 builds the queue.
 *
 * It reads the `site` parameter the estate screen links with, so selecting a site
 * demonstrably arrives somewhere that knows which site was chosen. Filtering rows
 * by it is 009's work, because there are no rows here to filter.
 */
export default async function Queue({
  searchParams,
}: {
  searchParams: Promise<{ site?: string }>;
}) {
  const { site } = await searchParams;
  const name = await siteName(site);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">At-risk queue</h1>
        <p className="text-ink-dim mt-2 max-w-2xl text-sm leading-relaxed">
          Every member in a band, High first, each with the reason that put them there. High rows
          carry the drafting controls; Medium and Low carry a band and a reason and nothing else.
        </p>
      </div>

      {name ? (
        <p className="border-rule bg-raised border px-4 py-3 text-sm">
          <span className="label">Site</span>
          <span className="mt-1 block font-medium">{name}</span>
        </p>
      ) : null}

      <Empty heading="No messages drafted">
        {name
          ? `The queue for ${name} lands in 009, and the drafting controls on it in 011.`
          : "The queue lands in 009, and the drafting controls on it in 011."}{" "}
        It opens empty on purpose: a reviewer drafts one member at a time, and nothing is written
        until somebody asks for it.
      </Empty>
    </div>
  );
}

async function siteName(site: string | undefined): Promise<string | null> {
  const id = Number(site);
  if (!site || !Number.isInteger(id)) {
    return null;
  }
  const rows = await sql`select name from sites where id = ${id}`;
  return rows.length === 0 ? null : String(rows[0].name);
}
