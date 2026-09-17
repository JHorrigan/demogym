# Specification

Status: in progress. The estate, the scoring rule and the two model features are settled. The screens are sketched. Open questions are listed at the end.

## The problem

Gym operators hold a dataset most industries would envy. Every membership gym has access control, so it has a timestamped record of when each member physically turned up. Most use it to open a door and for nothing else.

Attendance decay is the earliest reliable signal that a member is about to cancel, and it appears weeks before the cancellation does. demogym scores that signal from entry records alone, has a language model draft the approach to each member at risk, and gives a site manager a written briefing on what is happening at their site.

Retention was chosen because it is the largest single lever on an operator's profit, it runs entirely on data every operator already has, it needs a judgement about where a language model belongs and where it does not, and it has an obvious human-in-the-loop guardrail that makes the safety design visible rather than theoretical.

## What this is

A working prototype on synthetic data, not a product. All data is generated. No real member data, no real operator, no real site.

Nothing is sent to anybody. There is no outbound email, SMS or messaging integration. A model drafts, a person decides, and the decision is recorded.

The estate is deliberately small so the queue is reviewable by one person and every number on screen can be traced by hand. A six-site chain averaging fifty members is not a viable business. The rules work identically at a hundred times the size, and the demonstration is the reasoning, not the row count.

## The data

Seven tables. Four hold the estate, three hold what the system produced from it.

```sql
sites        -- id, name, region, opened_on
members      -- id, site_id, account_number, joined_on, left_on, plan, monthly_price
entries      -- id, member_id, site_id, entered_at
equipment    -- id, site_id, name, category, installed_on, status, down_since
risk_scores  -- member_id, scored_on, band, reason,
             --   baseline, recent_rate, decay, typical_gap, gap_multiple
drafts       -- member_id, scored_on, attempt, tone, length, offer,
             --   subject, body, rationale,
             --   model, input_tokens, output_tokens, cost_usd_cents,
             --   decision, edited_body, decided_at
briefings    -- site_id, generated_on, body, model, input_tokens, output_tokens, cost_usd_cents
```

| | Volume | Window |
|---|---|---|
| Sites | 6 | |
| Members | around 300, varying by site | |
| Entries | around 12,000 | the last 6 months |
| Equipment | around 100 units | installed over the last few years |
| Risk scores | around 3,600 | weekly, the last 12 weeks |
| Drafts | up to 40 | written on demand, empty until someone asks |
| Briefings | 6 | written on demand, one per site |

An eighth table, `model_calls`, holds a day and a count. It is bookkeeping rather than data: it is the counter behind the daily cap, and it exists because the cap counts requests the endpoint accepted rather than rows that were written. A call that fails writes no draft and still has to count, or a model that refused everything would be an unlimited one.

`entries` records arrival only. There is no exit time and therefore no session and no dwell time, because most turnstiles do not scan on the way out.

`equipment` is one table rather than a catalogue and a unit register, because the capex feature that needed the split is not built. Fault history is reduced to a current `status` and `down_since`, which is what the briefing needs.

Both readings behind a band are stored rather than just the band, so any `reason` string can be checked against the numbers that produced it. Costs are stored in US cents because that is the currency the API bills in, and converting at write time would turn a measurement into an estimate.

## Where this data would really come from

Nothing here is generated in a real deployment. Entry rows arrive from the access control or turnstile system, which every membership gym already runs. Equipment rows come from the asset register the operator keeps for purchasing and insurance. In this project both are manufactured, and replacing the generator with those feeds is the first work a real deployment would do.

Every dataset in this specification was chosen because an operator certainly has it. Anything that depends on a technology they might not own, or on a member remembering to do something, was deliberately left out. Those exclusions are recorded under limitations, with what each would add.

## Scoring

Scoring is arithmetic. It is deterministic, auditable and free to run. No language model is involved.

The rule that matters: decay is measured against each member's own established pattern, never a global threshold. A member who attended four times a week for five months and has not appeared in nine days is in trouble. A member who has always attended twice a month and has not appeared in nine days is behaving normally. A global "no visit in fourteen days" rule flags the second and misses the first, which is precisely backwards.

### Inputs

For each member active on the scoring date, meaning joined and not left, two readings are taken.

**Baseline**, the member's own established rate in visits per week.

- Joined more than 12 weeks before the scoring date: the median of the weekly visit counts over the trailing 12 weeks. A median rather than a mean, so one holiday does not move it.
- Joined between 4 and 12 weeks before: visits per week over their own first four weeks.
- Joined less than 4 weeks before: not scored. Nobody can tell in week one, and the real-data page says so.

**Recent rate**, visits per week over the trailing 3 weeks. Three weeks gives even a fortnightly attender an expected 1.5 visits, so the comparison means something.

**Typical gap**, the median days between consecutive visits over the baseline window.

From those, `decay` is the recent rate divided by the baseline, and `gap_multiple` is days since the last visit divided by the typical gap.

### The rule

A member takes the worse of the two readings. A sharp drop in rate and a long silence are each sufficient alone.

| Band | Decay at or below | or gap multiple at or above |
|---|---|---|
| High | 0.25 | 4 |
| Medium | 0.45 | 3 |
| Low | 0.65 | 2 |

Anything above those is not flagged.

**The minimum-baseline guard.** The decay ratio governs only members with a baseline of at least one visit per week. Below that, the gap reading governs alone, because a ratio built on one or two visits is noise. This is what keeps the twice-a-month member off the queue while the four-times-a-week member reaches High at about day seven.

**No visits in the baseline window** bands High without further calculation.

Members are banded rather than ranked on a raw score, because an operations team works a queue and not a leaderboard. Within a band the queue orders by monthly price.

### Reason strings

Every score carries a plain-English `reason` generated from the arithmetic. It names the reading that drove the band and the numbers behind it, so someone reading the queue can see why a member is there without opening anything else. That string is also the grounding the model is given at drafting time. The model is never handed raw history to interpret.

## Feature one: drafting the intervention

The model writes the message to a member at risk. It does not decide who is at risk, and it does not decide what is offered.

**What it receives.** Computed facts only, never raw entry rows. The `reason` string, the band, tenure, plan, monthly price, site, and facts derived by arithmetic: their usual day of the week, their usual time of day, their baseline rate, the date they last came. Every fact in the prompt traces back to a number, so the draft can say the member usually came on Tuesday mornings without the model having inferred it.

**Who can be drafted.** The High band at the most recent scoring date only, which the thresholds are tuned to keep at around twenty members. Medium and Low rows carry a band and a reason with no drafted message, because a drafted message for a Low-band member is work nobody will do today.

**Nothing is drafted until someone asks.** The queue opens with no messages in it. A reviewer drafts one member at a time, or presses Draft all, which fills the queue one message at a time as each call returns. See 0008.

**The reviewer sets the terms.** Three dropdowns before each call. Tone: warm, direct or encouraging. Length: short at around forty words, or standard at around a hundred and twenty. Offer: none, a free class, a guest pass, or a personal training session. No free text reaches the model, so every prompt the system can produce is one somebody chose from a list.

The offer is a human choice and not the model's. An offer has a price, which makes it an economic decision rather than a language one, and no model decides what the business gives away.

**Redraft.** A reviewer who does not like a draft changes a setting and asks for another. One redraft per member, enforced by an attempt count on the row, and both versions are kept. A daily cap across every model call sits behind that, enforced server side.

**The actions are Approve, Edit and Reject.** They keep the names the equivalent production tool would use. Every decision is recorded with the action, the edit if there was one, and the timestamp.

**A decided row reads "Approved, not sent".** The header says the same thing, but the row states it too, because a row is what gets cropped into a screenshot and travels without the header. A row reading only "Approved" beside a member's name and a message asserts something that did not happen.

**An edit is stored beside the draft, not over it.** The interface shows the edit against what the model wrote, and carries the share of approvals that needed an edit at all. That share is the only honest quality measure this project can produce. Accuracy against the generator's own labels would measure whether the scorer recovered an injected pattern. How often a person had to rewrite a draft measures something real.

## Feature two: the site briefing

On request, per site, the model writes a short briefing for whoever runs that site. Briefings start empty and are generated by pressing a button, exactly as drafts are. It reads computed facts and writes prose. It does not query anything and it does not do arithmetic.

**What it receives.** The site's at-risk counts by band, how they moved against the previous week, and the direction of travel across the twelve weekly scoring dates. Which attendance slots have thinned, by day of week and time of day. Which equipment is currently out of service and for how long. A projection of which members are likely to lapse within six weeks on current readings, and what that is worth per month.

**What it produces.** A paragraph naming the situation, a short ordered list of who to contact first with the reason for that order, and any link it can see between the facts, stated explicitly as a hypothesis to check rather than a finding. If six members at risk are weekday-morning regulars and both treadmills have been down eleven days, saying so is useful. Saying it caused the churn is not, and the prompt forbids it.

This is the feature that justifies equipment data existing. Without a second domain, a briefing narrates one number.

The projection is arithmetic and the plan is the model's. That division is the point: a client who asks how the forecast works gets a calculation, not a prompt.

## What the model does not do

It does not decide who is at risk. It does not compute a score, a band, a projection or a cost. It does not choose who to contact, only the order in which to work an already-computed list, with its reasoning visible. It never sees a raw entry row.

Everything the model is given was derived by code that can be read and checked. That boundary is worth more to a client than a third feature.

## Model and cost

The build uses `gpt-5.6-luna` with a pinned model ID so runs are reproducible, for drafting, for briefings and for any redraft. Which model is right is left to measurement rather than assumption, and a later slice compares it against `gpt-5-nano` below and `gpt-5-mini` above on the same members, judged on how often a person had to edit the output. See 0007.

Token counts come back on every call and are written to the row that produced them. Cost is measured from the API response, never estimated, and the running total is shown in the interface. A full sweep is about twenty drafts, up to twenty redrafts and six briefings. Forty-six calls, roughly two and a half pence, so cost is not a constraint here. It is shown because an operator running dozens of sites asks what this costs per member per month before they ask anything else.

## When a call fails

Every row in the queue is in one of four states: not drafted, drafting, drafted, or failed. A failed row says so on the row, and says which of three things happened.

- **Could not reach the model.** Transient. Worth trying again.
- **No credit remaining.** Trying again will not help, and the message says so rather than inviting a pointless retry.
- **Daily limit reached.** Not a failure at all. This is the cap from 0008 working, and it reads as a limit rather than a fault.

Telling the first two apart matters more than it looks. OpenAI returns 429 for both rate limiting and an exhausted balance, and their documentation is explicit that retrying a billing or quota error will not restore access. The status code alone is therefore not enough, and the error body is read to decide which of the two happened. Catching 429 and backing off is right for one case and exactly wrong for the other.

| Retried, bounded, honouring `Retry-After` | Returned immediately |
|---|---|
| 429 rate limit | 429 credit exhausted or spend limit reached |
| 500 server error | 401 authentication |
| 503 model overload | 400 bad request |
| Timeout, dropped connection | 403 geographic restriction |

**Prevention comes before recovery.** Draft all keeps at most four calls in flight. Nearly all the rate limiting this system could suffer would be self-inflicted by firing twenty at once, and a constant is cheaper than a recovery path. Whatever retrying the OpenAI client already performs is confirmed against the installed version before any is added on top, so there are never two retry budgets multiplying each other.

**A failure costs nothing.** The attempt count on the row moves only when a draft is stored, so a rate limit never silently consumes a member's one redraft.

**A truncated message is discarded.** If generation stopped because it hit the token ceiling rather than finishing, the message ends mid-sentence, and a half-written message is worse than none.

**There is no fallback to a cheaper model.** It is a real pattern and it would be wrong here. A rate limit applies to the account rather than the model, an exhausted balance certainly does, and a silent substitution would make both the pinned model ID and the measured cost figure meaningless.

**The row is written from the response before the endpoint returns**, so a call that was billed is not also lost.

Draft all does not stop when one member fails. The rest of the sweep continues, and failed rows are retried on their own.

The daily cap counts requests the endpoint accepts, so a retried call can push the true number of calls slightly above it. The retry bound is small and the cap is generous, so that drift is accepted rather than tracked.

## The screens

Three screens. It should look like an internal operations tool, because that is what it would be. Persistent in the header: a synthetic-data banner, and the running inference cost.

**Estate.** One row per site. Active members, counts by band, at-risk rate, monthly revenue at risk, equipment currently out of service, and a twelve-point trend of the at-risk rate alongside the change against last week. The default sort is at-risk rate descending, because a site with twice the members will always have more at-risk members, and ranking on the count reports which site is biggest rather than which is in trouble. The trend and the change are shown together: the change says what moved this week, the trend says whether it has been moving for a while, and only the pair separates a site in decline from one that had a bad week. Selecting a site opens its queue and a button to generate its briefing.

**At-risk queue.** Every member in a band, High first, filterable by site. Each row carries the member, site, band, tenure, monthly price and the reason string. High rows also carry the draft controls, the drafted subject and message once it exists, and the actions.

**Running this on real data.** The page that says what this is not. What it would connect to, what the prototype does not do, the regulatory position, and what the first week of a real engagement looks like.

## Deliberately absent

Each of these was considered and left out because the data behind it is not something an operator certainly has. Each entry records what it would add.

- **Exit scans and dwell time.** Most turnstiles are entry-only. With exit scanning, a thirty-minute visit could be told from a ninety-minute one, and decay would be detectable earlier.
- **Member-to-equipment usage.** Needs connected consoles and the member logging in at the machine, which many do not. It would allow telling a member their preferred machine has arrived, and nudging equipment they have stopped using.
- **Sets, reps and loads.** Needs a connected strength circuit. Progression stalling is a stronger churn signal than attendance alone.
- **Free weights and racks.** Never instrumented anywhere. No realistic route today.
- **Wearables and heart rate.** Member-owned and rarely shared. Would give intensity rather than only attendance.
- **Live occupancy sensing.** Real technology, unlikely at this size. Would give measured utilisation rather than inferred pressure.
- **Machine hour counters.** The closest call on this list. Cardio machines count their own hours for service intervals and need no member login, so the data is reliable where the estate is networked. Would turn replacement planning from inferred to measured.
- **Payment events and failures.** Certain data, cut for scope. A failed payment appears days before a cancellation, and showing the system caught someone weeks earlier is the strongest commercial argument the retention feature has.
- **Class bookings and no-shows.** Certain data, cut for scope. A booked class nobody attends is a sharper statement of disengagement than simply not coming.
- **Equipment fault history and capex planning.** Cut with the catalogue split. Failure against age and site footfall gives a replacement schedule.

And of the system itself: no contact suppression or frequency cap behind the approve button, no holdout group so effectiveness cannot be claimed, no seasonality model, no authentication beyond a shared link token, members under four weeks unscored, no accuracy figure and the reason why, and data only as fresh as the seed.

## Running this on real data

**What it would connect to.** Access control and turnstile scans, which is the feed that replaces `entries`. Membership and billing, for plan, price, join and leave dates. The asset register, for equipment. Class booking and CRM, so an intervention is delivered, suppressed or attributed.

**The regulatory position.** Gym attendance combined with health questionnaires, body composition or injury notes is special category data under UK GDPR Article 9. Inferring that a member is disengaging, and acting on that inference, is profiling. A real deployment needs a Data Protection Impact Assessment, a lawful basis that holds for profiling, a documented retention period, and a route for a member to object. This shapes what the feature is allowed to do, and it is cheaper to design around than to retrofit.

## Still open

- Whether a cheaper or larger model holds the briefing constraint better, settled by the comparison slice rather than in advance.
- Whether a briefing is invalidated when decisions are recorded against its site, or simply overwritten the next time someone asks for one.
- **Whether the no-visits rule should apply to a joiner's four-week window.** "No visits in the baseline window bands High without further calculation" was written for a twelve-week window, where it plainly means somebody has stopped coming. A member between four and twelve weeks has their own first four weeks as that window, so somebody who joined, did nothing for a month, and has been attending since is banded High while they are actively coming in. 011 found it by putting the reason and a drafted message side by side, and the reason now says when the member last came, so the row states the tension rather than hiding it. Whether the rule itself should change is not decided.

- **Whether the gap reading needs a minimum-data guard of its own.** The minimum-baseline guard protects the decay ratio from thin history and nothing protects the typical gap. A member with two visits in the window, a day apart, has a median gap of one day, so a month of silence reads as thirty times their usual gap. 006 found this by running the rule rather than reading it, and settled it in the generator: members attend on a small set of spaced days rather than by an independent draw each morning, which is a better model of how people train and leaves almost nothing resting on two or three gaps. That removes the symptom from this dataset. On real data the case would recur, and the options are a minimum number of gaps before the reading governs, or a floor under the typical gap. Neither is decided, and the thresholds in the band table were left where they are.
