/** A term and what there is to say about it, hairline-ruled and stacking at phone width. */
export default function Pairs({ items }: { items: { term: string; detail: string }[] }) {
  return (
    <dl className="border-rule border-t">
      {items.map(({ term, detail }) => (
        <div key={term} className="border-rule border-b py-3 sm:grid sm:grid-cols-[13rem_1fr] sm:gap-6">
          <dt className="font-medium">{term}</dt>
          <dd className="text-ink-dim mt-1 leading-relaxed sm:mt-0">{detail}</dd>
        </div>
      ))}
    </dl>
  );
}
