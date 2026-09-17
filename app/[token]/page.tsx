import { Empty } from "@/components/States";

export default function Estate() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Estate</h1>
        <p className="text-ink-dim mt-2 max-w-2xl text-sm leading-relaxed">
          One row per site, ranked by the share of members at risk rather than the count, because a
          site with twice the members will always have more of them.
        </p>
      </div>

      <Empty heading="The estate table lands in the next slice">
        The shell, the design language and the shared states are in place. 008 puts the six sites in
        here with their bands, their revenue at risk and a twelve-point trend.
      </Empty>
    </div>
  );
}
