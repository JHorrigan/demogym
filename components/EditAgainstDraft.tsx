/**
 * The reviewer's edit shown against what the model wrote.
 *
 * The span that changed is found by matching words in from both ends, which is exact:
 * anything marked as unchanged is character-for-character the same in both. Where an
 * edit is scattered rather than in one place, the marked span widens to cover all of
 * it, so the reading errs towards saying more changed rather than less.
 */
export default function EditAgainstDraft({ body, edited }: { body: string; edited: string }) {
  const change = changed(body, edited);

  return (
    <div className="mt-2 max-w-prose">
      <p className="label">The message, with the edit marked</p>
      <p className="mt-2 text-sm leading-relaxed whitespace-pre-line">
        {change.head}
        {change.removed ? (
          <del className="text-ink-dim decoration-ink-faint line-through">{change.removed}</del>
        ) : null}
        {change.added ? (
          <ins className="border-accent border-b-2 font-medium no-underline">{change.added}</ins>
        ) : null}
        {change.tail}
      </p>
    </div>
  );
}

type Change = { head: string; removed: string; added: string; tail: string };

/** The unchanged ends, and what sits between them in each version. */
function changed(body: string, edited: string): Change {
  const before = words(body);
  const after = words(edited);

  let head = 0;
  while (head < before.length && head < after.length && before[head] === after[head]) {
    head += 1;
  }

  let tail = 0;
  while (
    tail < before.length - head &&
    tail < after.length - head &&
    before[before.length - 1 - tail] === after[after.length - 1 - tail]
  ) {
    tail += 1;
  }

  return {
    head: before.slice(0, head).join(""),
    removed: before.slice(head, before.length - tail).join(""),
    added: after.slice(head, after.length - tail).join(""),
    tail: before.slice(before.length - tail).join(""),
  };
}

/** Words and the whitespace between them, so rejoining returns the original exactly. */
function words(text: string): string[] {
  return text.split(/(\s+)/);
}
