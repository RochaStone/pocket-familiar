# style.json

One small file holds your look: your colours, your fonts and your lines.
Every Rocha Coded tool reads the same file, so you make it once.
`style.example.json` is the blank version. `examples/style.rocha-coded.json` is Rocha's look, shared as an example.

## Where it is read from (first one found wins)
1. The file you set with `familiar config --style path/to/style.json`
2. `style.json` in the folder you are working in
3. `~/.rocha-coded/style.json`
4. `examples/style.rocha-coded.json` in this tool

Leave a colour or a font blank and that one key falls back to the bundled example.
Your words never fall back to Rocha's. A blank line, owner or handle stays blank, and the card leaves it out.
Her lines only show when you have no style.json at all and her example is the style in use.

## The keys
| Key | What to put | Used by the familiar |
|---|---|---|
| `name` | your brand or collection name | no |
| `owner` | your name | card footer |
| `handle` | your social handle, like @you | card footer |
| `site` | your website | no |
| `palette.hero` | your GROUND colour, the dark one things sit on | the page behind the card, the status line and receipt |
| `palette.accent` | your one accent | her fur, the feed pills, the mood chip |
| `palette.paper` | a light paper | her screen, text on the ground |
| `palette.paper_pink` | the card paper | the guest check, her belly |
| `palette.ink` | text and outlines | text, her outline |
| `palette.marker` | a pen colour for scrawl | the stamp, the top line, THANK YOU |
| `palette.plum` | a deep colour for objects | the egg |
| `palette.wine` | a second deep colour | her rosettes, small labels (plum is used if you leave it out) |
| `palette.gold` | a thin-rule and sparkle colour | rules, egg buttons, her grill |
| `palette.cool` | an alternate pill fill | not used by the familiar |
| `fonts.masthead` | a big headline font | her name |
| `fonts.label` | a narrow font for tags | labels, buttons |
| `fonts.body` | a readable font | sentences |
| `fonts.scrawl` | a handwriting or marker font | stamp, top line, THANK YOU |
| `fonts.mono` | a typewriter font | receipt lines |
| `fonts.script` | a signature script | not used by the familiar |
| `motif` | one of guest-check, front-page, magazine-scrawl, pink-paper, sticker-collage, rotary, leopard, retro-tv, neutral | no (she is always a guest check) |
| `lines.todo` | your to-do line | top of the card and the receipt |
| `lines.celebrate` | what you say when it goes right | the sticker when she celebrates |
| `lines.affirm` | the line you live by | printed when you hit a streak |
| `lines.masthead`, `headline`, `scrawl`, `stamp` | your other house lines | no, other tools use them |
| `references` | images or links that show your taste | read by Claude when it makes this file with you |
| `notes` | your look in one or two sentences | same |

Colours must be hex, like `#50163C`. Fonts are Google Fonts names. If a font is not on Google Fonts, the card falls back to a system font of the same kind.
The familiar's own name is not in this file. It lives with her: `familiar config --name Diamond`.
