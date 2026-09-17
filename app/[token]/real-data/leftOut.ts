/**
 * Datasets considered and cut, each with what it would add. The test every one failed
 * is whether an operator certainly has it, without new hardware and without a member
 * remembering to do anything.
 */
export const LEFT_OUT = [
  {
    term: "Exit scans and dwell time",
    detail:
      "Most turnstiles read on the way in only. With an exit scan a thirty-minute visit could be told from a ninety-minute one, and a member tapering off would show up before their attendance did.",
  },
  {
    term: "Member-to-equipment usage",
    detail:
      "Needs connected consoles and the member logging in at the machine, which many do not. It would allow telling a member their preferred machine has arrived, and noticing the equipment they quietly stopped using.",
  },
  {
    term: "Sets, reps and loads",
    detail:
      "Needs a connected strength circuit. Progression stalling is a stronger churn signal than attendance on its own, because it appears while the member is still turning up.",
  },
  {
    term: "Free weights and racks",
    detail:
      "Not instrumented anywhere, and there is no realistic route to it today. It is listed because it is the part of the gym floor this kind of system is blindest to.",
  },
  {
    term: "Wearables and heart rate",
    detail:
      "Member-owned and rarely shared. It would give intensity rather than attendance alone, so a member going through the motions could be told from one training hard.",
  },
  {
    term: "Live occupancy sensing",
    detail:
      "Real technology, unlikely at six sites. It would give measured utilisation rather than pressure inferred from entry counts.",
  },
  {
    term: "Machine hour counters",
    detail:
      "The closest call on this list. Cardio machines count their own hours for service intervals and need no member login, so the data is reliable wherever the estate is networked. It would turn replacement planning from inferred into measured.",
  },
  {
    term: "Payment events and failures",
    detail:
      "Certain data, cut for scope. A failed payment appears days before a cancellation, and showing that this system had flagged the member weeks earlier is the strongest commercial argument the retention feature has.",
  },
  {
    term: "Class bookings and no-shows",
    detail:
      "Certain data, cut for scope. A booked class nobody turns up to is a sharper statement of disengagement than simply not coming.",
  },
  {
    term: "Equipment fault history",
    detail:
      "Cut when the equipment catalogue and the unit register stayed one table. Failure rates against age and site footfall give a replacement schedule rather than a list of what is broken today.",
  },
];
