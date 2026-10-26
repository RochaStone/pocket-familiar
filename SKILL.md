---
name: pocket-familiar
description: A pixel leopard familiar who eats business actions, not tokens. Use when the user wants to install their familiar, says they shipped, sent, invoiced, rested or closed something ("I shipped the newsletter", "invoice is out", "took the afternoon off"), or asks how their familiar is doing.
---

# pocket-familiar

A pink pixel leopard with a diamond grill. She lives in the Claude Code status line and in a web card. She eats what the user ships: a post, an email, an invoice, a rest day, a closed item. Her default name is Lucky. The user may have renamed her, so read her name from `familiar status`.

## Install

In Claude Code (status line, hooks and the command):
```sh
bash ~/.claude/skills/pocket-familiar/install.sh
familiar hatch
```
Tell the user to restart Claude Code to see her in the status line. The installer backs up `~/.claude/settings.json` first and prints how to undo (`bash ~/.claude/skills/pocket-familiar/uninstall.sh`).

Anywhere else with a terminal, including Claude Cowork: the status line and hooks are Claude Code only. The command and the web card work anywhere with Python 3.10+.
```sh
python3 <this skill folder>/familiar hatch
```
In Cowork, set `FAMILIAR_HOME` to a folder the user gave you access to, so she remembers between tasks:
```sh
export FAMILIAR_HOME="<the user's folder>/.familiar"
```
If `familiar` is not on the PATH, run `python3 <this skill folder>/familiar` instead.

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
- `familiar config` shows or sets optional signals: `--ledger` (the goal-tests `ledger.json`, usually `~/.claude/goal-tests/ledger.json`, or any JSON or PASS/FAIL log; she is worried while a probe fails), `--open-items` (a markdown list, makes her restless when an item's default date has arrived), `--quiet 23:00-07:00`, `--hunger-hours 24`, `--watch invoiced`, `--style path/to/style.json`.

Her moods, first match wins: asleep, worried, celebrating, sleepy, restless, hungry, fed. The rules are documented at the top of `mood.py`.
