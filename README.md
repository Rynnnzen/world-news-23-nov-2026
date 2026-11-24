# The World in One Day — Monday, 23 November 2026

A single 1024x1024 newspaper-style front page that sums up the world news of
**Monday 23 November 2026**: all **41 stories** from **7 regions**, with 13
illustrated pictured stories and 28 listed one-line briefs.

Entry for the make.fun bounty:
**<https://make.fun/bounty/news-image-20261123>**

[![make.fun news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123)
[![make.fun rank](https://make.fun/badge/news-image-20261123/Rynnnzen/world-news-23-nov-2026/rank.svg)](https://make.fun/bounty/news-image-20261123)
[![make.fun reward](https://make.fun/badge/news-image-20261123/Rynnnzen/world-news-23-nov-2026/reward.svg)](https://make.fun/bounty/news-image-20261123)

## What the image shows

- **Masthead** — "THE WORLD IN ONE DAY" and "Monday, 23 November 2026".
- **Stat strip** — 41 stories, 7 regions, 13 pictured, 28 listed, and the date.
- **Lead cards** — COP31's failure, the sinking of the *Merkury* off Libya, and
  Nvidia reinstating Jensen Huang, each with a drawn illustration.
- **Ten more pictured cards** — Europe, the Middle East, Asia, the Americas,
  Africa, Oceania and the World, each with a drawn icon, region tag, headline
  and one-line summary.
- **Dotted world map** — dots form the continents, and numbered pins mark the
  locations of the pictured stories.
- **Regional briefs** — the remaining 28 stories grouped under EUROPE, MIDDLE
  EAST, ASIA, AMERICAS, AFRICA, OCEANIA and WORLD.
- **Date check and footer** — confirming every story is dated 23 November 2026
  and that this is a news summary image, not a live news service.

All artwork is original, drawn with Pillow primitives. No photographs, no
external images and no network access are used.

## Files

| File | Purpose |
| --- | --- |
| `compose.py` | Draws the infographic and writes `assets/entry.png` (Python + Pillow). |
| `assets/entry.png` | The finished 1024x1024 PNG, 179,396 bytes. |
| `main.py` | Standard-library entry point: copies the shipped image to the output directory and verifies its SHA-256. |
| `README.md` | This file. |
| `LICENSE` | MIT license. |

## Build the image

The image is already committed at `assets/entry.png`. To redraw it (requires
Pillow):

```sh
python3 compose.py
```

The drawing is deterministic, so a rerun produces byte-identical output.

## Run the entry

`main.py` uses only the Python standard library. It resolves the output
directory in this order:

1. `--output-dir PATH`
2. `$MAKEFUN_OUTPUT_DIR`
3. `/output`

```sh
python3 main.py --output-dir out
# or
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It writes `out/entry.png` through a temporary file and an atomic rename, then
checks that the copy's SHA-256 matches the shipped image. If the checksums
differ, or the shipped image is not a PNG within 1024x1024 and 1 MiB, the
program fails loudly.

SHA-256 of `assets/entry.png`:
`2feeb3ee6e1d742692badf32997f33110fc5304a80c1d42614500b4d3c55664c`

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Rynnnzen.
