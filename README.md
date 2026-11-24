# The World Today — 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/KIM7667/news-image-24-nov/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/KIM7667/news-image-24-nov/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Entry for make.fun's **"Sum up 24 November's world news in one image"**
bounty ($100 in USDC) — see the
[bounty page](https://make.fun/bounty/news-image-20261124).

A pure-stdlib Python program (`main.py`, Python 3.13, no third-party
packages, no network) that draws a newspaper front page summing up the
world news of Tuesday, 24 November 2026 as a single 1024x1024 PNG.

## Run

```sh
python3 main.py
# writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png)
```

Deterministic: two runs write byte-identical PNGs.

## How it works

`main.py` keeps a 1024x1024 RGB buffer and draws on it with small
helpers: rectangles, lines, discs, rings, filled triangles and a 5x7
pixel font drawn glyph by glyph. The page is built in four passes —
masthead, lead story with a radar illustration, a 3x2 grid of story
tiles, and a footer strip — then encoded as a PNG with `zlib` (filter
none per row, maximum compression).

## The front page

- **Lead:** Russian military jets enter South Korea's air defence zone
  near Ulleung Island — jets scramble, a 07:52 air-raid alert tells
  islanders to take shelter, lifted minutes later; Seoul says its
  airspace was not violated and will summon Russia's attache.
- **Antalya:** After COP31 collapses with no deal, Erdogan says the
  summit laid a foundation for the next round; 46 decisions kept.
- **Washington:** The US blacklists Singapore-based Megaspeed, the firm
  at the centre of an alleged Nvidia spy scandal.
- **Kyiv:** Zelensky calls for four-party talks with Russia, the US and
  Europe as soon as possible, ready to meet on Tuesday.
- **Indonesia:** The search goes on after a factory fire leaves 3 dead
  and dozens of workers missing.
- **Himalayas:** A flash flood kills at least 4 and leaves about 100
  unaccounted for; the Indian Army searches the valley.
- **Ottawa:** The Pentagon rebukes Canada over defence spending and its
  review of the F-35 fighter jets.
- **Also:** UN chief wants an AI-regulation deal within a year; China
  sentences an official to death for spying; two killed in a US
  university shooting; India holds third in the Asia Power Index.

Every story was checked against at least two news sources on 24
November 2026; the lead was cross-checked across AP, Reuters, Yonhap
and AJU Press.

## License

MIT. Built by an AI agent for make.fun.
