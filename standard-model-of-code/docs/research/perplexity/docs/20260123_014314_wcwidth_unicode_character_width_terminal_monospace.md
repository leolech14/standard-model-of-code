# Research: wcwidth unicode character width terminal monospace emoji double-width alignment Python

> **Date:** 2026-01-23 01:43:14
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:3880c9526e423e8b0b6dc0d11079372fadb2a84e80f337fe34ed7cf12c6a1457`
> **Raw JSON:** `raw/20260123_014314_wcwidth_unicode_character_width_terminal_monospace.json`

---

## Query

wcwidth unicode character width terminal monospace emoji double-width alignment Python

---

## Response

**wcwidth** is a Python library that measures how many cells a unicode character or string occupies when displayed in a terminal with monospace fonts.[1][2] This is essential because while most characters occupy 1 cell, some occupy 2 cells (like full-width characters and emoji), and others occupy 0 cells (like combining characters).

## The Problem

Python's standard `len()` function counts characters by codepoints, not by their display width. For example, the Japanese text `'コンニチハ'` has 5 codepoints but occupies 10 cells on screen.[2] This causes alignment issues when using standard string functions like `rjust()`.

## The Solution

wcwidth provides two main functions:[1][2]

**`wcwidth()`** — determines the width of a *single character*, returning:
- `-1` for indeterminate/non-printable characters
- `0` for zero-width characters (null, combining marks)
- `1` for most characters
- `2` for East Asian Wide (W) or East Asian Full-width (F) characters, including emoji

**`wcswidth()`** — determines the width of a *string*, returning the sum of all character widths or `-1` if any character is unprintable

## Usage Example

To right-align a string correctly on an 80-column terminal:[1]

```python
from wcwidth import wcswidth
text = u'コンニチハ'
padding = ' ' * (80 - wcswidth(text))
print(padding + text)
```

With emoji, `wcswidth('🦆')` returns `2` since emoji are double-width characters.[3]

## Installation and Availability

Install via pip: `pip install wcwidth`[1] The library is also available through package managers on various Linux distributions and in conda.[4][5]

wcwidth is widely used in terminal applications including **blessed** (terminal wrapper), **python-prompt-toolkit** (interactive CLI builder), **pgcli**, and **curtsies**.[2]

---

## Citations

1. https://pypi.org/project/wcwidth/0.1.5/
2. https://github.com/jquast/wcwidth
3. https://ocaml.org/p/wcwidth/1.0.1
4. https://doc.sagemath.org/html/en/reference/spkg/wcwidth.html
5. https://packagehub.suse.com/packages/python-wcwidth/
6. https://wcwidth.readthedocs.io/en/latest/specs.html
7. https://software.opensuse.org/package/python-wcwidth
8. https://www.jeffquast.com/post/terminal_wcwidth_solution/

---

## Usage Stats

- Prompt tokens: 13
- Completion tokens: 428
- Total tokens: 441
