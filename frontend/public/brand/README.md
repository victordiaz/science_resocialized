# Science Resocialized brand assets

The mark: a paper (center) linked to four reviewers (blue, teal, clay, purple).

## Folders
- `logo/` the mark alone: `mark.svg` (on light), `mark-on-dark.svg`, `mark-black.svg`, `mark-white.svg`, plus 512 px PNGs.
- `lockup/` mark plus name: horizontal (light, dark, black, white) and stacked (light, dark). Text is outlined, so no font is needed.
- `app-icon/` `app-icon.svg` / `-dark` / `-cream`, 1024 px PNGs, `icon-192.png`, `icon-512.png`, `maskable-512.png` (PWA), `apple-touch-icon.png` (180 px).
- `favicon/` `favicon.svg` (switches to dark colors in dark mode), `favicon.ico` (16/32/48), PNGs.
- `animated/` one self-contained animated SVG per state, plus `sr-animations.css` if you want to animate inline SVG yourself.
- `social/` `og-image` (1200 × 630 link preview) and 800 × 800 avatars.
- `colors.css` brand colors as CSS variables.

## Animations
| File | Use it for |
|---|---|
| `gather.svg` | Splash, first launch, empty pages |
| `thinking.svg` | General loading |
| `signals.svg` | A review is running |
| `orbit.svg` | Long waits, such as a replication |
| `reply.svg` | A persona just replied |
| `verified.svg` | Replication verified, task done |
| `waiting.svg` | Paused, needs the user (leak check) |

Use them as `<img src="animated/thinking.svg" width="24" height="24" alt="Loading">`. They all stop when the system asks for reduced motion.

## In the HTML head
```html
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:image" content="/og-image.png">
```

## Rules
- Keep clear space of at least one dot's width around the mark.
- Minimum sizes: mark 16 px, horizontal logo 120 px wide. Below 32 px use the favicon version (thicker links, bigger dots).
- Don't recolor single dots, rotate the mark, or add effects.
- Wordmark typeface: Space Grotesk Bold (SIL Open Font License).
