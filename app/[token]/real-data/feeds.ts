/** The four systems a real deployment reads, and what each one replaces here. */
export const FEEDS = [
  {
    term: "Access control and turnstile scans",
    detail:
      "Replaces the entries table. Every membership gym already runs one, and this is the single feed the whole scoring rule rests on.",
  },
  {
    term: "Membership and billing",
    detail:
      "Replaces the members table. Plan, monthly price, the date somebody joined and the date they left.",
  },
  {
    term: "The asset register",
    detail:
      "Replaces the equipment table. It is the list an operator already keeps for purchasing and insurance, so nothing new has to be recorded to get it.",
  },
  {
    term: "Class booking and CRM",
    detail:
      "Nothing here reads it yet. It is how an approved message would be delivered, suppressed against whatever else the member was sent, and attributed afterwards.",
  },
];
