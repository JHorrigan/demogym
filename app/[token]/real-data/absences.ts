/** What the prototype does not do, gathered in one place rather than left to conversation. */
export const ABSENCES = [
  {
    term: "Nothing is sent",
    detail:
      "There is no email, SMS or messaging integration. Approve records a decision against the member and stops there, and the row says so.",
  },
  {
    term: "No suppression, no frequency cap",
    detail:
      "This system knows nothing about what else the member was sent this week. Both would have to exist before anything left the building.",
  },
  {
    term: "No holdout group",
    detail:
      "Nobody was deliberately left uncontacted, so there is nothing to compare an outcome against. This project does not claim the intervention works.",
  },
  {
    term: "No accuracy figure",
    detail:
      "Scoring the rule against the generator's own leavers would measure whether it recovered a pattern that was injected on purpose. The share of approved drafts that needed an edit is in the header instead, because a person rewriting a message is a real measurement.",
  },
  {
    term: "No seasonality",
    detail:
      "January and August do not behave alike in this industry, and the rule does not know that. A member's baseline is their own trailing twelve weeks and nothing else.",
  },
  {
    term: "No authentication",
    detail:
      "A shared link token and nothing more. There are no accounts, so there is no record of which person approved anything, only that somebody did.",
  },
  {
    term: "No observability",
    detail:
      "No logging, metrics or alerting. A failed model call is visible to whoever pressed the button and to nobody else.",
  },
  {
    term: "Members under four weeks are unscored",
    detail:
      "There is no established pattern to measure a change against yet. They appear in the member count and in no band.",
  },
  {
    term: "The data is as fresh as the last run",
    detail:
      "Nothing ingests and nothing is scheduled. The estate was seeded once and scored once, and both are commands somebody runs.",
  },
];
