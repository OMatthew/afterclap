# Topic research: demand, competition, niche (2026-10-14)

Question from Matthew: should we pick topics from data on what people ask, check what already exists, and should we commit to a niche or keep the rabbit-hole thread?

**Short answer:** Yes to data, used as a filter rather than the source of ideas. Don't narrow to the big-topic niches he floated. Narrow a little, to a beat: the hidden history of ordinary American things (money, food, the street, the calendar), run as short mini-series. Keep the tease line, but stop letting it choose the next topic.

---

## 1. Demand: what YouTube autocomplete shows

`suggestqueries.google.com ... ds=yt` worked (not blocked). It returns the top ~10 YouTube suggestions for a prefix. **No volumes.** Results are ranked, may be shaped by location, and move with the news. Tool: `research/tools/topic_scan.py suggest "<prefix>"`.

**Generic stems are useless.** "why is / why do / why are / why does / why did / how did" return songs, memes and news ("why is the government shutdown", "why do birds suddenly appear", "how did michael jackson die"). "history of" returns big umbrellas (halloween, the world, japan, concrete, islam).

**Stems anchored to a noun are useful.** They show which questions about a thing people actually type:

| Seed | Top suggestions (in order) |
|---|---|
| why are coins | painted red · **round** · does coins have **ridges** · made of |
| why are there | ... · no new cemeteries · **ridges on coins** |
| why is the dollar | crashing · strong · store so cheap · ... · not backed by gold · **sign an s** |
| why is money | so important · **green** · important · dirty |
| why are pencils | **yellow** · made of · ... · carpenters pencils flat |
| why is ketchup | **so hard to pour** (several variants) · bad for you · red · called ketchup |
| why is new york | so expensive · **called the big apple** · ... · called the empire state |
| why is it called | ... · **black friday** · amber alert · **pound cake** |
| why do we say | pledge · like · amen · ok · **trick or treat** |
| why do we eat | **turkey on thanksgiving** · slop · cake on birthdays · popcorn at the movies |
| why do we have | seasons · school · belly button · ... · **daylight savings time** |
| why do keyboards | have the **qwerty** arrangement · not alphabetical · qwerty |
| why do watches | have **jewels** · cost so much · rotating bezel |
| why are barns | red · painted red |

Niche probes (seed → top suggestions):
- **War/geopolitics:** "why did the roman" → empire fall / kill jesus / collapse / split / republic fall. "why did ww1" → start / happen / end so suddenly / really start / turn into trench warfare. "why does the us" → current-events questions (Venezuela, Israel, Greenland, 800 bases).
- **Economics:** "why did the 2008" → crash happen / economy crash / housing market crash. "why is the dollar" → mostly news (crashing, weak, strong).
- **Language:** "why is english" → so hard (mostly memes) · spelling so weird. "why do languages" → die / have gender / change. "why do we say" → amen, ok, trick or treat.
- **Programming:** "why is python" → popular / slow / used for ML. Demand comes from learners asking practical questions, not history.

Takeaway: there is demand in every candidate niche, but in war and economics it's dominated by a few huge evergreen questions plus news. Everyday-object stems turn up exactly our format, including two we already made (coin ridges).

## 2. What already exists (saturated vs. open)

Method: scraped the YouTube search results page for the exact question (`topic_scan.py search`). Counts are as displayed on 2026-10-14. It's one search with no login, so treat it as a snapshot, not a census.

**The pattern, on nearly every famous "why" question:** one to three winners with 0.1–66M views, then a long tail of near-identical AI-style Shorts at under 1K views (titles like "The Real Reason ... Will Surprise You 🤯"). The low end of this format is crowded with exactly what we're trying not to be.

**Direct competitor to watch:** *History of Simple Things* makes 8–9 min videos plus some Shorts on our kind of question (school buses 318K, Big Apple 21K, dollar sign 9.8K, Coca-Cola 14K, pencils 4.6K). Older long-form players on the same questions: Today I Found Out, BrainStuff, Colossal Cranium, TED-Ed, Vox. *Simple Things – Surprising* has 1.7M on ship hulls.

Our own questions, for calibration:

| Question | Biggest existing Short / video | Ours |
|---|---|---|
| Dime smaller than a nickel | nothing over ~1.6K | 1.1K |
| Old glass purple | **1.2M Short** ("Why Are Old Bottles Purple?") + 30K | 16 (stalled) |
| Maraschino red | 65K Short, 18K Short | 1.3K |

Weak hint, three data points: our stalled glass Short went up against a 1.2M Short on the same hook. That fits "the feed has already served this hook", but n=3 can't separate it from luck, title or the first frame.

**Candidate niches, as a 60–90 s hand-drawn sourced format:**

| Niche | Evidence | Verdict |
|---|---|---|
| War / geopolitics | WW1-start Shorts at **66M**, 12M, 4.1M (countryballs and edits); OverSimplified WW1 57M; Rome-fall Short 97K, Infographics Show 4.9M | **Crowded.** Huge winners, plus a current-events pull we can't fact-check at Short speed. |
| Specific periods / regions | Not probed by region; same big channels cover it | Probably crowded at the top; a narrow region shrinks the audience |
| Tech / inventions | QWERTY Short **3M** + 176K + 146K; Vox 3.4M; Atomic Frontier 727K disputing the "jam" story | Popular, crowded on the famous ones; open on obscure objects |
| Languages / etymology | Grammatical gender Shorts 1M and 1.1M; English spelling 357K; Etymology Nerd (Adam Aleksic) is a big dedicated short-form creator; RobWords 1.5M on "$" | **Crowded, with strong specialist personalities** |
| Programming languages | "Why is Python called Python" Shorts top out at 5.8K | Open but **small ceiling**; audience wants tutorials |
| Economics / crashes | 2008 Shorts 597K, 257K, 179K; Fed-creation Short 1M | Crowded; and conspiracy content clusters here (Fed) |
| **Everyday objects / customs** (current) | Mixed: some 1–14M winners (barns, popcorn, cake, ship hulls, school buses), but many good questions top out under 10K on Shorts | **Best fit**, as long as we screen out the already-won hooks |

## 3. Niche vs. rabbit hole: what the evidence says

- **YouTube's official line is about audience, not topic.** Todd Sherman (Shorts product lead, Aug 2023): "The audience is the algorithm." Each Short is tested on "a set of people that may enjoy your video", then expanded or not. Rene Ritchie (Creator Liaison, 2024): "The algorithm follows the audience, so please the audience ... see which videos are growing your audience ... make more videos like those."
- **There is no official YouTube statement that a consistent niche is rewarded on Shorts.** "Niche down" advice (Paddy Galloway's 3.3B-view study as summarized by VideoGen, OutlierKit and others) is creator opinion without published comparison data. Both sources say this outright.
- **Series:** YouTube launched Shorts series (seasons, episodes, custom thumbnails, sequential playback) on 2026-09-23, aimed mostly at microdramas. YouTube says nothing about whether series change feed distribution.
- **Our own data:** 94% of views come from the feed, and each Short gets one burst and then goes quiet. So almost nobody arrives having seen the previous Short. The tease line costs little, but it doesn't bring in viewers, and choosing topics for the bridge narrows the pool for no measurable gain.
- **Practical reading:** a consistent *audience promise* matters (same kind of payoff, same look, so the people who liked one get the next). A narrow *subject* niche isn't required, and would cut us off from the open everyday questions.

## 4. Recommendation

### Narrow a little, not a lot
- **Beat:** "the surprising history behind ordinary (mostly American) things": money, food and labels, things on the street, holidays and the calendar. This is what 01, 02 and 04 already are (the three that got feed reach).
- **Mini-series of 3–5** inside the beat (e.g. "Money", "Food color", "Holidays"), grouped with the new Shorts series feature. It's free to try, though its effect on reach is unknown.
- **The thread:** keep the last-line tease as flavor, but choose the topic first and write the bridge after. When no honest bridge exists, end on a question inside the mini-series.
- **Don't** pivot to war, geopolitics, economics crashes or programming languages. The first three are owned by huge channels and drift into news. Programming has a small ceiling.

### Weekly topic method (about 1 hour)
1. **Harvest (20 min).** Run `topic_scan.py suggest` on 30–50 noun-anchored stems ("why are [object]", "why is [object]", "why is it called", "why do we say", "why do we eat"). Add the seasonal calendar for the next 3 weeks. Keep anything that's a true "why" about a thing everyone knows.
2. **Check coverage (15 min).** Run `topic_scan.py search "<exact question>"`. Log the top Short's views, the top long video's views, and whether either tells the same causal chain we would.
3. **Score (0–3 each; this rubric is our own judgment, not a validated model):**
   - **Demand:** 3 = shows up after a 2–3-word stem; 2 = shows up only with most of the phrase; 1 = not in autocomplete, but older videos on it have 100K+ views; 0 = none.
   - **Gap:** 3 = top Short under 10K; 2 = 10–100K; 1 = 100K–1M, and only with a clearly different chain; 0 = a 1M+ Short already tells our chain.
   - **Surprise chain:** at least 3 verified links, with a final cause the viewer wouldn't guess.
   - **Hook object:** something everyone has handled or seen, which can be drawn in one image.
   - **Paint fit:** the color is the story, or the red-lead paint has a clear path.
   - **Sources:** primary or scholarly sources exist, and no known myth sits at the core.
   - **Groove check:** if our angle is the one the top AI Shorts use, score 0 here and find another.
   Make anything scoring 14 or more out of 21. Anything with Gap 0 needs a different question.
4. **Close the loop each Sunday.** In WEEKLY-*.md, record each Short's score next to its "shown in feed", "chose to view" and views. After about 15 Shorts, check whether Demand and Gap actually predict reach, and drop whatever doesn't.

### 10 candidate questions
Demand = autocomplete evidence above. Competition = the 2026-10-14 search snapshot. **The chains are leads to verify, not checked facts.**

| # | Question | Demand | Biggest existing (Short / long) | Lead chain (to verify) | Flag |
|---|---|---|---|---|---|
| 1 | Why are pencils yellow? | top suggestion for "why are pencils" | 3.4K / 4.6K | 1890s premium "Chinese" graphite (really Siberian) → Koh-i-Noor paints pencils imperial yellow → everyone copies the color of quality | **Open.** Myth risk on the China story |
| 2 | Why is New York called the Big Apple? | 2nd for "why is new york" | 9.4K / 152K (TIFO) | 1920s racing columnist hears stable hands in New Orleans → jazz musicians → revived by a 1970s tourism campaign during the city's crisis | **Open** |
| 3 | Why is it called Black Friday? (post by ~Nov 25) | "why is it called" → black friday | 11K / 224K | Philadelphia police name for traffic chaos (1950s–60s) → retailers retrofit the "in the black" story | **Open.** Seasonal |
| 4 | Why do we say "trick or treat"? (post by ~Oct 28) | "why do we say" → trick or treat | 2.2K / 28K | 1920s–30s Halloween vandalism → towns organize treats to buy off pranksters → paused by WWII sugar rationing → postwar candy boom | **Open.** Seasonal, tight deadline |
| 5 | Why do we eat turkey on Thanksgiving? (post by ~Nov 24) | "why do we eat" → top suggestion | 1.1K / 637K (Mystery Science) | Sarah Josepha Hale's decades-long campaign and menus → Lincoln 1863 → turkey: big, cheap, and not needed for eggs or milk | **Open for Shorts.** Seasonal |
| 6 | Why do we change the clocks? (DST ends Nov 1) | "why do we have" → daylight savings time | 137K / 1M (Colossal Cranium) | 1916 Germany saves coal for the war → US copies → **farmers fought it** and got it repealed in 1919 | Medium. The farmer-myth angle exists only at ~200 views |
| 7 | Why is the dollar sign an S? | "why is the dollar" → sign an s | 88K / **1.5M (RobWords, 5 months old)** | Spanish silver peso, "ps" abbreviation → merchants' shorthand → $ (Pillars-of-Hercules story is a myth) | Medium. Recently well covered long-form. Fits the Money series |
| 8 | Why are coins round? | 2nd for "why are coins" | 1.2K / 19K | Unknown. Needs a real surprising link (round blanks and dies, machine minting?). **Skip if no chain** | Open but unproven |
| 9 | Why is ketchup so hard to pour? | about half of the "why is ketchup" suggestions | **56M (AumSum, physics)** / 3.5M TED-Ed | History angle instead: Heinz drops preservatives (1906 food-law fight) → needs ripe, thick tomatoes → the slow pour became the brand | **Flag: hook saturated** on physics. Only with the history chain. Fits the food-label thread (Wiley) |
| 10 | Why is money green? | 2nd for "why is money" | **2.2M Short** / 23K | 1861 Civil War "greenbacks" → green ink resisted photo counterfeiting → 1929 small-note standardization kept it | **Flag: one big viral Short.** Others are under 1K. Only with a sharper chain |

**Checked and set aside (already won by big Shorts):** barns red (2.7M, 918K), QWERTY (3M; the "jam" story is also disputed), popcorn at movies (3.6M, 2.6M), cake on birthdays (14M), ships' red bottoms (3.4M), Coke/cocaine (7.3M), school buses yellow (2.8M, 1.1M), clocks clockwise (1.9M), no new cemeteries (604K), watch jewels (606K). Also checked: 60 minutes in an hour (Shorts ≤5.9K, but the Babylon answer is well known, so a groove risk) and driving on the right (112K).

### What this research doesn't show
- No search volumes. Autocomplete is a rank, not a count. Google Trends wasn't pulled.
- Feed reach (94% of our views) isn't search demand. A question people search for isn't proof the feed will push it. Demand is a tiebreaker; the hook and the first second still decide whether a Short gets swiped.
- The competition snapshot comes from one unauthenticated search per question, and view counts include old videos.
- Nothing official says a niche helps or hurts on Shorts.

## Sources (opened)
- YouTube autocomplete endpoint (queried ~70 seeds): https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q=why+is+
- YouTube search results pages, e.g. https://www.youtube.com/results?search_query=why+are+school+buses+yellow (about 40 exact-question searches, 2026-10-14)
- Search Engine Journal, "YouTube explains how Shorts algorithm works" (Todd Sherman, 2023-08-28): https://searchenginejournal.com/youtube-explains-how-shorts-algorithm-works/494953
- OutlierKit, "How the YouTube Shorts algorithm works in 2026, in YouTube's words": https://outlierkit.com/resources/youtube-shorts-algorithm/
- Tubefilter, Rene Ritchie Shorts FAQs (2024-08-26): https://www.tubefilter.com/2024/08/26/rene-ritchie-shorts-creator-faqs/
- TV Technology, YouTube episodic Shorts / Shorts series (2026-09-25): https://www.tvtechnology.com/platform/streaming/youtube-embraces-microdramas-with-features-for-episodic-shorts
- VideoGen, summary of Paddy Galloway's 3.3B-view Shorts study (2023-08-17): https://videogen.io/blog/decoding-the-youtube-shorts-algorithm-a-deep-dive-into-3-3-billion-views

Tool for repeating this weekly: `research/tools/topic_scan.py` (suggest / search modes; light manual use only, and it breaks if YouTube changes its page; fallback is YouTube Data API search.list).

## Addendum (lead, 2026-10-14): YouTube numbers with 06 and 07, and our own calibration

Studio, Shorts, last 28 days to Oct 13: 6,377 views, 65.0% stayed to watch, +17 subscribers.

| Short | Views | Stayed | Avg viewed | Likes | Subs |
|---|---|---|---|---|---|
| 07 Swiss cheese (1 day) | 1,550 | 66.4% | 54% (0:47) | 44 | +2 |
| 04 maraschino | 1,374 | 65.5% | 48% | 40 | +1 |
| 06 margarine | 1,273 | 64.5% | **73% (1:02)** | 47 | **+5** |
| 01 dime | 1,142 | 62.3% | 43% | 28 | +4 |
| 02 ridges | 850 | 66.8% | 61% | 36 | +4 |
| 05 oranges | 164 | 62.6% | 65% | 11 | +1 |
| 03 glass | 24 | 57.1% | 82% | 5 | 0 |

- 5 of 7 got a first-day burst of ~850–1,550 views. Openings hold (62–67%) across the board, so the stalls (03, 05) aren't explained by the hook metric.
- 06 is 85 s and held 73%: length alone doesn't explain the drop-off in 01 and 04. What 06 and 02 share: a clear, slightly absurd conflict told as a story (a law forcing pink margarine; clippers and a window tax), not a mechanism.
- Competition calibration: Swiss cheese already had 66K and 53K Shorts on the same question and ours still got 1.5K on day one; oranges is dominated by meme Shorts on "why are oranges called orange" (516K) and ours stalled; margarine had nothing above 5K and did well. "Already covered" is a soft signal, not a veto.
- "Why does American cheese melt" already has several Shorts (41K, 3.7K, 1K) telling the chemistry answer. The chemistry is the groove; the Swiss export origin and the 1921 laxative patent are what nobody else tells.
