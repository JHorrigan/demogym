export default function Refused() {
  return (
    <main className="mx-auto flex min-h-dvh max-w-md flex-col justify-center gap-4 px-6 py-16">
      <h1 className="text-2xl font-semibold tracking-tight">This link is not valid</h1>
      <p className="text-ink-dim leading-relaxed">
        demogym is reachable only through the full link it was sent with. Check the address against
        the message it arrived in, including the part after the domain.
      </p>
      <p className="text-ink-dim leading-relaxed">
        If the link is right and this page still appears, the token has been rotated and a new link
        is needed.
      </p>
    </main>
  );
}
