import SyntheticDataStrip from "@/components/SyntheticDataStrip";

export default function Refused() {
  return (
    <div className="flex min-h-dvh flex-col">
      <SyntheticDataStrip />

      <main className="mx-auto flex w-full max-w-lg flex-1 flex-col justify-center px-4 py-16 sm:px-6">
        {/* Not the label class, which uppercases. The name is lower case on purpose. */}
        <p className="text-ink-dim text-sm">demogym</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">This link is not valid</h1>
        <div className="border-rule bg-raised border-l-edge mt-6 border border-l-4 px-5 py-5">
          <p className="text-sm leading-relaxed">
            demogym is reachable only through the full link it was sent with. Check the address
            against the message it arrived in, including the part after the domain.
          </p>
          <p className="text-ink-dim mt-3 text-sm leading-relaxed">
            If the link is right and this page still appears, the token has been rotated and a new
            link is needed.
          </p>
        </div>
      </main>
    </div>
  );
}
