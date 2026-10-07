# Afterclap Short 02: "Why does a dime have ridges, but a nickel doesn't?"

**Status:** Rough cut rendered (out/ridges-rough.mp4), awaiting Matthew's look. Script v5 had four cold reads and a fact-and-logic review (Fable 5.1). Voice: Darren, eleven_v4, 74.4 s.
**Promise kept from Short 01:** the dime ends "And why does the dime have ridges, but not the nickel? That's another story."
**Groove check:** the ridges answer alone is heavily covered (a 28M-view short), and Newton at the Mint is groove. Our edge is the far end: the clipped-money deficiency paid for by the 1696 window tax, with bricked-up windows you can still see. Newton is left out on purpose.
**Next tease:** purple glass (story bank #3). It's committed by the last line, so 03 has to be purple glass. Research: research/03-purple-glass.md (the WWI/Germany link is a myth; the real cause is bottle machines).

## Beats and paint path (red lead accent, vertical paper strip)
Times come from words.json via shots.py; positions and targets from layout.py.
| # | Line (short) | Drawings | The paint lands on (word) |
|---|---|---|---|
| 1 | Hook: dime ridges vs smooth nickel | coins-edge | the dime's ridges ("ridges") |
| 2 | "...bricked-up windows in England, trace back to the same crime" | house-bricked | a bricked window ("bricked-up") |
| 3 | Worth their silver; hammered by hand, uneven edges | hammer-coin, lumpy-coin | the coin under the punch ("silver"), the lumpy edge ("uneven") |
| 4 | Snipped a little off, melted the clippings | shears-clip, ladle | the sliver ("off"), then it drops into the ladle ("clippings"): the paint is the silver |
| 5 | You could hang for clipping | rope (no noose, no figure) | the rope ("hang") |
| 6 | By the 1690s, nearly half their silver gone | balance | the clipped coin riding high ("half") |
| 7 | New coins by machine, ridged edges; anyone can tell | screw-press, milled-coin | the ridged edge ("ridged"), then the notch ("tell") |
| 8 | Taken back at full value; cost millions | chest | fills the chest ("full"), drains out on "cost ... pounds" |
| 9 | Taxed houses by their windows; easy to count from the street | house-open, tax-man | a window ("windows"), the next window along ("count") |
| 10 | Bricked windows up; a few still there | house-bricked (callback) | the bricked window ("bricked"), soaks in on "still" |
| 11 | America's silver coins got ridges; nickel mostly copper, stayed smooth | coins-edge (callback) | the dime's ridges ("dimes"), the nickel ("copper"); slides off it on "stayed smooth" |
| 12 | The silver left the dime in 1965; the ridges stayed | dime-large | fills the dime ("silver"), drains out, hops onto the ridges and soaks ("ridges") |
| 13 | Tease: purple glass | glass-panes + old-bottle: the bottle on a windowsill (the window ties back to the window tax; the bottle leads into 03) | the bottle ("purple"), then the film run-out and the brand mark |

**Art notes:** 16 drawings from the ChatGPT app (PROMPT_art.md); The tease is a bottle on a windowsill: the window ties back to this Short's windows, the bottle leads into 03 (Matthew's idea). The tracer drops coin ridges and window bricks as hatching, so tools/artfix.py redraws them (art/fixes.json).

## Fact table
| Claim | Source | Note |
|---|---|---|
| Clipping = shaving/snipping precious metal from coin edges; clippings melted into bullion | [Wikipedia: Coin clipping](https://en.wikipedia.org/wiki/Coin_clipping); [NGC: "Reed" All About It](https://www.ngccoin.com/news/article/513/) | |
| Hammered (hand-struck) coins had irregular edges that made clipping easy | [Wikipedia: Great Recoinage of 1696](https://en.wikipedia.org/wiki/Great_Recoinage_of_1696); [Newton and the Mint (Oxford)](https://newtonandthemint.history.ox.ac.uk/great-recoinage/the-great-recoinage) | |
| Clipping could be punished by death | [Wikipedia: Coin clipping](https://en.wikipedia.org/wiki/Coin_clipping) (Thomas and Anne Rogers, 1690); [Britannia Coin Co.](https://britanniacoincompany.com/blog/coin-clipping-the-great-recoinage-of-1696/); [Davcoin](https://davcoin.com/node/6184) | Script says "You could hang for clipping." True and not overstated. |
| By the 1690s (worst in 1695) clipped silver had lost close to half its weight | Hopton Haynes (Mint official, c.1700), "at least 45 per Cent", [Newton Project MINT01093](https://newtonandthemint.history.ox.ac.uk/transcriptions/normalised/MINT01093); [Davcoin](https://davcoin.com/node/6184): an Exchequer sample weighed "a bit over half the proper total" | "By the 1690s ... nearly half" (not "1695": it blurs with 1965 on one listen) |
| 1696 Great Recoinage: old hammered coin called in, re-minted by machine (screw press) with milled edges that show clipping | [Wikipedia: Great Recoinage](https://en.wikipedia.org/wiki/Great_Recoinage_of_1696) (milled edge since 1662, recoinage 1696–99); [Newton and the Mint](https://newtonandthemint.history.ox.ac.uk/great-recoinage/the-great-recoinage) | "ridged edges": smaller coins were grained (ridged), crowns were lettered. Fine for a Short. |
| Old coins accepted at face value for a period, with the loss borne at the public charge, not by holders; the swap cost the government about £2.7 million | [Davcoin](https://davcoin.com/node/6184) (face value until the deadline set by the Dec 1695 proclamation); [Britannia Coin Co.](https://britanniacoincompany.com/blog/coin-clipping-the-great-recoinage-of-1696/) (£2.7m); Haynes's loss estimate £2.25m; 7 & 8 Will. III c.1 (Jan 1696): clipped coin taken at face value in taxes to 4 May 1696 and in Exchequer loans to 24 June 1696, the deficiency made good "at the publick charge" | "For months", "so their owners didn't lose out", "millions of pounds" |
| **Central link:** the 1696 house/window duty was granted "for making good the Deficiency of the clipped Money" | **Primary:** Statutes of the Realm vol. 7, 7 & 8 Will. III c.18, ["For granting to His Majesty several rates or Duties upon Houses for making Good the deficiency of the clipt Money"](https://archive.british-history.ac.uk/node/39621); House of Commons Journal, 3 Nov 1696: ["The Duties upon Houses, for making good the Deficiency of the clipped Money"](https://www.british-history.ac.uk/node/32411). **Secondary:** [Wikipedia: Window tax](https://en.wikipedia.org/wiki/Window_tax); [UNC Tax Center](https://tax.unc.edu/?p=3832) | Two primary sources plus two secondary. Said as "To help pay for that": the house duty was the main measure, not the whole bill (Fable review). |
| The duty was a house tax graduated by number of windows | [Wikipedia: Window tax](https://en.wikipedia.org/wiki/Window_tax) (2s per house plus bands for 10–20 and 20+ windows); [UK National Archives](https://www.nationalarchives.gov.uk/education/resources/georgian-britain-age-modernity/window-tax/) | "taxed houses by their windows" |
| Windows could be counted from outside, without entering the home | [Oates & Schwab, Lincoln Institute *Land Lines* (2014)](https://www.lincolninst.edu/publications/articles/window-tax) | "Windows were easy to count from the street." |
| People bricked up windows to pay less | [UK National Archives](https://www.nationalarchives.gov.uk/education/resources/georgian-britain-age-modernity/window-tax/); [Oates & Schwab](https://www.lincolninst.edu/publications/articles/window-tax) | |
| Some bricked-up windows survive; not every blank window is a tax dodge | [Wikipedia: Window tax](https://en.wikipedia.org/wiki/Window_tax) | Script hedges: "A few of those blank windows are still there." |
| US Mint reeded its silver (and gold) coins against clipping; base-metal coins (cent, nickel) got no edge devices after 1795, "since these were not subject to clipping" | [NGC: "Reed" All About It](https://www.ngccoin.com/news/article/513/); [Wikipedia: Coin clipping](https://en.wikipedia.org/wiki/Coin_clipping) | The nickel (1866) was always base metal |
| A nickel is mostly copper | [US Mint: Nickel](https://www.usmint.gov/learn/coins-and-medals/circulating-coins/nickel) ("25% Ni, Balance Cu"); wartime 1942–45 nickels were 56% copper, 35% silver, 9% manganese, so still mostly copper | "A nickel is mostly copper, never worth clipping" |
| Silver left the dime in 1965; the reeding stayed ("for the sake of familiarity and tradition") | [Wikipedia: Coinage Act of 1965](https://en.wikipedia.org/wiki/Coinage_Act_of_1965); [NGC](https://www.ngccoin.com/news/article/513/) | Callback to Short 01 |

**Myths avoided:** "daylight robbery" from the window tax (no scholarly support, per Wikipedia); Newton "invented" reeding (milled edges predate him, and it's groove).

## Cold-read log
- v1: windows read as a tangent; "shears" not paid off; "full price" unclear; three "So" openers. Rewrote the hook to share a root cause ("trace back to one crime"), added "You can count windows from the street" as the bridge, fixed pronouns.
- v2: the swap's cost wasn't explained; "missing ridges" was odd; no bridge to America. Fixed.
- v3: dime not named among the silver coins; "millions" of what; "for a while" vague; clip payoff implicit. Fixed in v4.
- v4 (fresh cold read + Fable fact-and-logic review): "one crime" read as a single heist (now "the same crime"); why the old coins were taken at full value wasn't said (now "so their owners didn't lose out"); "nickel never worth clipping" assumed you know it isn't silver (now "mostly copper"); 1695 and 1965 blurred on one listen (now "By the 1690s"); "anyone can see it" pointed at the coin (now "anyone can tell"); "To raise the money" overstated the tax's share (now "To help pay for that"). No factual errors found.
- v5 (fresh cold read): passes; every pronoun landed and the answer got through in one listen. "You can count windows from the street" read as a stray fact, so it's now "Windows were easy to count from the street." "That's another story" stays: it's the channel's sign-off.
