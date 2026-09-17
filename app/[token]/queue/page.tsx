import { Empty } from "@/components/States";

export default function Queue() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">At-risk queue</h1>
        <p className="text-ink-dim mt-2 max-w-2xl text-sm leading-relaxed">
          Every member in a band, High first, each with the reason that put them there. High rows
          carry the drafting controls; Medium and Low carry a band and a reason and nothing else.
        </p>
      </div>

      <Empty heading="No messages drafted">
        The queue opens empty on purpose. A reviewer drafts one member at a time, or presses Draft
        all, and nothing is written until somebody asks for it. 009 and 011 build this.
      </Empty>
    </div>
  );
}
