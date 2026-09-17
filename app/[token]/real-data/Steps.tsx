/** An ordered list where the order is load-bearing, numbered in the figure face. */
export default function Steps({ items }: { items: string[] }) {
  return (
    <ol className="border-rule border-t">
      {items.map((item, index) => (
        <li key={item} className="border-rule flex gap-4 border-b py-3">
          <span className="figure text-ink-faint shrink-0">{String(index + 1).padStart(2, "0")}</span>
          <span className="text-ink-dim leading-relaxed">{item}</span>
        </li>
      ))}
    </ol>
  );
}
