---
name: pocket-familiar
description: A pixel leopard familiar who eats business actions, not tokens. Use when the user wants to install their familiar, says they shipped, sent, invoiced, rested or closed something ("I shipped the newsletter", "invoice is out", "took the afternoon off"), or asks how their familiar is doing.
---

# pocket-familiar

A pink pixel leopard with a diamond grill. She lives in the Claude Code status line and in a web card. She eats what the user ships: a post, an email, an invoice, a rest day, a closed item. Her default name is Lucky. The user may have renamed her, so read her name from `familiar status`.

## How to talk to her

She may never have opened a terminal. Be warm, certain and kind. Ask one question at a time and wait for the answer. Reflect her answer back in one sentence. Say what you are about to do before you do it. End every step with what she will see and what she can do next. Never say "simply" or "just". If a step needs her to type in the terminal, tell her exactly what to type and what she will see.

## Install, as a guided flow

1. Ask: "Are you in Claude Code on your computer, or in Claude Cowork?" Wait.
2. **Claude Code.** Say: "I'm going to set Lucky up and connect her to the bottom of your Claude Code window. I'll back up your settings first." Then run:
   ```sh
   bash ~/.claude/skills/pocket-familiar/install.sh
   ```
   Tell her what it printed in plain words ("she's installed, and your old settings are saved").
3. Ask: "What would you like to call her? Lucky is her name unless you pick another." Wait. Reflect it back ("Lovely, she's Diamond."). Then run:
   ```sh
   familiar hatch --name "<her answer>"
   ```
   If `familiar` is not found, run `python3 ~/.claude/skills/pocket-familiar/familiar hatch --name "<her answer>"` instead. Show her the hatch line.
4. Say: "Close Claude Code and open it again. You'll see her at the bottom of the window, with her mood next to her name." Then: "Tell me something you did today and I'll feed her."
5. **Cowork.** The status line and hooks are Claude Code only. The command and the web card work in Cowork. Say what you are about to do, then set her home inside the folder she gave you so Lucky remembers her between tasks:
   ```sh
   export FAMILIAR_HOME="<the folder she gave you>/.familiar"
   python3 <this skill folder>/familiar hatch --name "<her answer>"
   ```
   Then run `python3 <this skill folder>/familiar web --no-open` and give her the card file. Tell her: "Open this in your browser to see her. From now on, tell me what you did and I'll feed her."

## Make it hers (style.json)

Her card and receipt take their colours, fonts and lines from one shared `style.json` (lookup order and keys in `STYLE.md`). With no file, Rocha's look in `examples/style.rocha-coded.json` is used as the example.

If the user has no style.json, offer to make one: ask for 3 to 5 references (screenshots, links, a Pinterest board), a palette if she has one, and the words she says a lot. Write style.json. Show her one rendered sample. Never assume her taste is Rocha's.

Write it to `style.json` in her working folder, or to `~/.rocha-coded/style.json` so every Rocha Coded tool finds it. Then render a sample with `familiar web` (add `--no-open` in a sandbox) and show it to her. Her familiar's name is not in style.json. Rename her with `familiar config --name`.

## Feed her on the user's behalf

When the user tells you they did a business action, feed her once and say so in a short line, for example "I'll feed Lucky." Then run:

| The user says something like | Run |
|---|---|
| shipped, posted, published, launched, went live | `familiar feed shipped "<what>"` |
| sent, emailed, pitched, replied, followed up | `familiar feed sent "<what>"` |
| invoiced, billed, got paid | `familiar feed invoiced "<what>"` |
| rested, took the day off, walked, slept in | `familiar feed rested "<what>"` |
| closed, finished, ticked off, resolved an open item | `familiar feed closed "<what>"` |

Rules:
- Feed only for actions the user tells you they did. Never feed for your own tool calls, tokens, or code you wrote.
- One action, one feed. Keep the note to a few plain words in the user's language.
- Show her reply line from the command. Do not add a speech about it.

## Read her

- `familiar status` gives her mood, the reason, the streak and the number the user watches.
- `familiar card` prints this week as a guest check receipt.
- `familiar web` writes `~/.familiar/familiar.html` and opens it. Use `--no-open` in a sandbox and give the user the file.
- Her card comes in three looks: `analog` (a guest check), `cyberpunk` (a handheld with a terminal) and `y2k-blog` (a 2003 blog window). The `motif` in style.json picks one; `familiar web --motif y2k-blog` shows another for one card. When she asks which look she likes, render all three and show her.
- `familiar config` shows or sets optional signals: `--ledger` (goal tests is found on its own at `$GOAL_TESTS_HOME/ledger.json` or `~/.claude/goal-tests/ledger.json`; she is worried while its `failing` list is not empty, and a ledger older than 26 hours counts as unknown, not failing; pass a path for another ledger or `off`), `--open-items` (a markdown list, makes her restless when an item's default date has arrived), `--quiet 23:00-07:00`, `--hunger-hours 24`, `--watch invoiced`, `--style path/to/style.json`.

Her moods, first match wins: asleep, worried, celebrating, sleepy, restless, hungry, fed. The rules are documented at the top of `mood.py`.
