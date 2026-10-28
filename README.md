# pocket-familiar

*Free tools from the Rocheverse.* Part of **Rocha Coded**.

![Lucky's week as a 2003 blog page in a window called lucky.exe, with Lucky the pixel leopard in the sidebar, her mood, a hit counter and a guestbook](docs/img/hero.png)

![The same week in three looks: an analog guest check, a cyberpunk handheld, and a y2k blog](docs/img/triptych.png)

*One week, three looks: analog, cyberpunk, y2k-blog. You choose hers.*

## What she gets you

A pixel familiar who lives at the bottom of your Claude Code window.
Lucky is a pink leopard with a diamond grill.
She eats what you ship: a post, an email, an invoice, a rest day, a closed item.
She gets worried when something you shipped breaks.
She gets sleepy when you have been at it too long.
Every week she prints you a guest check of everything you fed her.

![](docs/img/divider.svg)

## Start here

Five steps, about five minutes. You need a Mac or Linux computer and Claude Code.
The **terminal** is the window where you type instructions to your computer. On a Mac, press Command and Space together, type Terminal, and press Enter.

![step 1](docs/img/step-01.svg) **Copy Lucky onto your computer.** To **clone** is to copy a project from GitHub into a folder on your computer.
```sh
git clone https://github.com/RochaStone/pocket-familiar ~/.claude/skills/pocket-familiar
```
You will see "Cloning into" and then your prompt comes back. That means it worked.

![step 2](docs/img/step-02.svg) **Set her up.** This connects her to Claude Code and teaches your terminal the word `familiar`. It saves a backup of your Claude Code settings first.
```sh
bash ~/.claude/skills/pocket-familiar/install.sh
```
You will see a few green ticks and "Next: hatch her."

![step 3](docs/img/step-03.svg) **Open a new terminal window**, so it knows the new word. Then hatch her.
```sh
familiar hatch
```
You will see Lucky hatch. Press Enter to keep the name Lucky, or type a new name first. She tells you she is hungry already.

![step 4](docs/img/step-04.svg) **Feed her your first win.** Pick something you did today.
```sh
familiar feed shipped "the newsletter"
```
You will see her eat it in one bite.

![step 5](docs/img/step-05.svg) **Restart Claude Code.** You will see her at the bottom of the window, with her mood next to her name. That strip is the **status line**. From now on you can tell Claude "I sent the invoice" and Claude feeds her for you.

Using Claude Cowork instead? Go to [Claude Cowork](#claude-cowork) below. Three steps, no terminal.

![](docs/img/divider.svg)

## Why she eats actions, not tokens

When Claude Code shipped its own little buddy, a wave of terminal pets followed. Every one of them eats tokens or commits, so they grow fat on busywork and reward you for keeping the machine running. Lucky is a founder's familiar, not a developer's. She only eats the things that move a business: the newsletter that went out, the pitch you sent, the invoice, the item you finally closed, and the rest day you took on purpose. Rest counts as food. The tax line on her receipt always reads 0 tokens.

![](docs/img/divider.svg)

## Install

You need Python 3.10 or newer. Nothing else.

| Where you use her | Install | What you get |
|---|---|---|
| [Claude Code](#claude-code) (recommended) | clone into `~/.claude/skills`, run `install.sh` | status line, session hooks, the `familiar` command, the web card |
| [Any terminal](#any-terminal) | clone anywhere, run `install.sh --cli-only` | the `familiar` command and the web card |
| [Claude Cowork](#claude-cowork) | upload `pocket-familiar.zip` as a skill | Claude feeds her for you and prints her card |

The status line and the hooks are Claude Code only. **Hooks** are small scripts Claude Code runs on its own when a session starts and stops; hers note how long you have been working. Everything else works anywhere with a terminal.

### Claude Code
```sh
git clone https://github.com/RochaStone/pocket-familiar ~/.claude/skills/pocket-familiar
bash ~/.claude/skills/pocket-familiar/install.sh
familiar hatch
```
Restart Claude Code. She is at the bottom of the window.
The installer also adds one line to your shell profile (`~/.zshrc` on a Mac) so your terminal can find `familiar`. Open a new terminal window after installing.
The installer backs up your `~/.claude/settings.json` before it touches anything, keeps your other hooks, and saves your old status line so it can come back.
To undo: `bash ~/.claude/skills/pocket-familiar/uninstall.sh`.

### Any terminal
```sh
git clone https://github.com/RochaStone/pocket-familiar ~/pocket-familiar
bash ~/pocket-familiar/install.sh --cli-only
familiar hatch
```

### Claude Cowork
1. Download `pocket-familiar.zip` from the latest release. A **zip** is one file that holds a whole folder.
2. In the Claude desktop app: Customize > Skills, then + > Create skill > Upload a skill, and pick the zip.
3. Give your Cowork task a folder to keep her in, then say: "Hatch my pocket familiar."
4. From then on, tell Claude what you did. "I shipped the newsletter." Claude feeds her.

![](docs/img/divider.svg)

## The five feeds

```sh
familiar feed shipped "the newsletter"
familiar feed sent "podcast pitch"
familiar feed invoiced "brand day"
familiar feed rested "beach, phone off"
familiar feed closed "booking page"
```

Or tell Claude in your own words. "Invoice is out." Claude feeds her and tells you so.

![](docs/img/divider.svg)

## Her moods

Exactly one mood wins. She checks them in this order.

| Mood | Sprite | When |
|---|---|---|
| asleep | `∴(=_✧_=)zZ` | quiet hours (23:00 to 07:00 unless you change it) |
| worried | `∴(=ﾟ✧ﾟ;=)∴` | a probe in your ledger is failing |
| celebrating | `✧\(=^✧^=)/✧` | for an hour after you ship or invoice, or hit a 3, 7 or 21 day streak |
| sleepy | `∴(=-✧-=)ᶻ` | your Claude Code session has run past 3 hours |
| restless | `≋(=･✧･=)≋` | open items are past their default date |
| hungry | `∴(=°✧°=)っ` | nothing fed for 24 hours |
| fed | `∴(=^･✧･^=)∴` | all good |

The ✧ is her grill. The ∴ are her spots.

She comes in two renderings from the same mood: painted for the web card (analog and y2k-blog), pixel for the terminal, the status line and the cyberpunk handheld.

![Lucky in all seven moods, painted on top and pixel underneath](docs/img/lucky-moods.png)

## Make her yours

```sh
familiar config --name Diamond          # rename her
familiar config --watch invoiced        # the one number on her card
familiar config --quiet 22:30-06:30     # her bedtime, or off
familiar config --hunger-hours 36       # how long she can wait
familiar config --ledger ~/probes/ledger.json   # a ledger somewhere else (goal tests is found on its own)
familiar config --open-items ~/notes/OPEN_ITEMS.md # she gets restless when a default is due
```

If you use goal tests from Claude Code for Founders, she finds its ledger on her own (`$GOAL_TESTS_HOME/ledger.json`, then `~/.claude/goal-tests/ledger.json`). She is worried for as long as its `failing` list has a name in it.
No ledger means no worry. A ledger older than 26 hours means the daily sweep has not run, so she does not worry about it either. `familiar config --ledger off` turns this off.
Any other JSON with pass and fail statuses works too (see `examples/ledger.example.json`), and so does a plain log with `PASS name` and `FAIL name` lines.
An open item is a markdown table row or a `- [ ]` line with a date in it. Struck-through or ticked rows are skipped. See `examples/open-items.example.md`.

![](docs/img/divider.svg)

## Make it yours

Her colours, fonts and lines come from one `style.json`, and the same file styles every Rocha Coded tool.
Two come in the box: `examples/style.rocha-coded.json` (Rocha's current look: plum, blush, candy pink and gold, as above) and `style.example.json` (blank, for yours). `STYLE.md` explains every key.
Put yours in your working folder or in `~/.rocha-coded/style.json`, or ask Claude to make one with you from a few references.
Your colours and fonts re-tone every look, and `motif` picks the shape: `analog`, `cyberpunk` or `y2k-blog`. Both are yours to curate.

Pairs with [merwitch-mode](https://github.com/RochaStone/merwitch-mode): install pocket-familiar first, then merwitch-mode, so the two status lines do not fight.

## See her

- `familiar status` tells you how she is and why.
- `familiar card` prints this week as a guest check, right in the terminal.
- `familiar web` opens her web card. Tap a dish to copy the feed command. Feeding happens in your terminal.
- `familiar web --motif cyberpunk` (or `analog`, `y2k-blog`) shows her in another look for this one card.

![](docs/img/divider.svg)

## What's inside

| File | What it does |
|---|---|
| `familiar` | the command (one Python file, standard library only) |
| `mood.py` | the mood rules, documented at the top |
| `statusline.sh` | the Claude Code status line |
| `hooks/` | session start greeting, session length tracking |
| `painted.py` | the painted Lucky, a soft-shaded SVG in seven moods |
| `templates/` | the web card: one page, one script, three motif skins, inlined into a single file |
| `style.py`, `STYLE.md`, `style.example.json` | the shared style file: lookup, keys, a blank one to fill in |
| `install.sh`, `uninstall.sh` | safe setup and a clean undo |
| `SKILL.md` | tells Claude how to install, feed and read her |
| `examples/` | Rocha's style, a sample week, sample ledger and open items |
| `scripts/make-readme-images.py` | makes every image in this README from the tool itself (`docs/IMAGES.md`) |
| `tests/` | `python3 -m unittest discover -s tests` (all three motifs render in Chrome at phone width) and `bash tests/test_statusline.sh` |

Her memories live in `~/.familiar` on your computer. Nothing is sent anywhere.

Not affiliated with any other terminal pet or familiar project.

![](docs/img/divider.svg)

## If it goes wrong (everyone's first time) ![](docs/img/heart.svg)

This happens to everyone the first time. Each one has a quick fix.

- **"command not found: familiar".** Your terminal has not learned the new word yet. Open a new terminal window and try again. If it still says this, run `python3 ~/.claude/skills/pocket-familiar/familiar hatch` instead; it does the same thing.
- **"command not found: git" or a box asking to install developer tools.** Your Mac needs its free developer tools once. Click Install in the box, wait for it to finish, then run step 1 again.
- **You do not see her at the bottom of Claude Code.** Close Claude Code completely and open it again. If you see an egg, she has not hatched yet: run `familiar hatch`. To check her any time, run `familiar status`.

If you want her gone, `bash ~/.claude/skills/pocket-familiar/uninstall.sh` takes everything back out and puts your old settings back.

## Licence

MIT. See [LICENSE](LICENSE).

[Sign my guestbook](https://github.com/RochaStone/pocket-familiar/issues) ♡

## Made by Rocha

Rocha \
Brand Alchemist & AI Architect \
Author of *Brand Alchemy in the Thriving Era* \
Creator of [Conscious Founder OS](https://founders.thrivingera.com) \
Founder, [Thriving Era Studio](https://thrivingera.com)

I take female founders AI native in 7 days, and I build what they need next. \
Start with the audit: [thrivingera.com/audit](https://thrivingera.com/audit). \
Or book an exploratory call: [calendly.com/rochelle-thrivingera/exploratory-call](https://calendly.com/rochelle-thrivingera/exploratory-call). It is where we decide if we work together.

[Instagram @rocheverse](https://instagram.com/rocheverse) · [Substack](https://rochastone.substack.com) · [LinkedIn](https://www.linkedin.com/in/rochellelivingstonecosmic) · [More free tools](https://thrivingera.com/free) · [All tools on GitHub](https://github.com/RochaStone)
