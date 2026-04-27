"""
Automated checks for freebreathwork.org print layout and copy.

Run:  python3 test_print_layout.py
"""

import re, sys

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
failures = []

def check(label, condition, detail=""):
    if condition:
        print(f"  {PASS}  {label}")
    else:
        print(f"  {FAIL}  {label}" + (f" — {detail}" if detail else ""))
        failures.append(label)

def extract_in(pattern, html, flags=0):
    m = re.search(pattern, html, flags)
    return float(m.group(1)) if m else None

with open("index.html") as f:
    html = f.read()

# Pull the @media print block only so we don't match screen-only CSS
print_block = re.search(r"@media print\s*\{(.+)", html, re.DOTALL)
print_css = print_block.group(1) if print_block else ""

LETTER_W, LETTER_H = 8.5, 11.0

print("\n── Page setup ───────────────────────────────────────────────────────")

margin = extract_in(r"@page\s*\{[^}]*margin:\s*([\d.]+)in", print_css)
check("@page margin defined in inches", margin is not None)
if margin:
    check(f"Margin ≤ 0.5in (got {margin}in)", margin <= 0.5,
          "too large — reduces printable area too much")

print("\n── Height: both flyers must fit on one page ─────────────────────────")

flyer_h = extract_in(r"\.flyer\s*\{[^}]*height:\s*([\d.]+)in", print_css, re.DOTALL)
cut_h   = extract_in(r"\.flyer-cut\s*\{[^}]*height:\s*([\d.]+)in", print_css, re.DOTALL)
check("Flyer height defined in inches", flyer_h is not None)
check("Cut line height defined in inches", cut_h is not None)

if margin and flyer_h and cut_h:
    printable_h = LETTER_H - margin * 2
    total_h = flyer_h * 2 + cut_h
    check(
        f"2 flyers ({flyer_h}in×2) + cut ({cut_h}in) = {total_h}in "
        f"≤ printable {printable_h}in",
        total_h <= printable_h + 0.01,
        f"overflows by {total_h - printable_h:.3f}in — will push to page 2"
    )

print("\n── Width: right column must not overflow printable area ─────────────")

flyer_w = extract_in(r"\.flyer\s*\{[^}]*width:\s*([\d.]+)in", print_css, re.DOTALL)
cols_match = re.search(r"grid-template-columns:\s*([\d.]+)in\s+([\d.]+)in", print_css)
padding_match = re.search(r"\.flyer-r\s*\{[^}]*padding:\s*[\d.]+in\s+[\d.]+in\s+[\d.]+in\s+([\d.]+)in", print_css, re.DOTALL)
rpad_match = re.search(r"\.flyer-r\s*\{[^}]*padding:\s*[\d.]+in\s+([\d.]+)in", print_css, re.DOTALL)

check("Flyer width defined", flyer_w is not None)
check("Grid columns defined", cols_match is not None)

if margin and flyer_w and cols_match and rpad_match:
    printable_w = LETTER_W - margin * 2
    left_col = float(cols_match.group(1))
    right_col = float(cols_match.group(2))
    right_pad = float(rpad_match.group(1))
    content_right_edge = left_col + right_col - right_pad
    check(
        f"Right column content edge ({content_right_edge:.2f}in) "
        f"≤ printable width ({printable_w}in)",
        content_right_edge <= printable_w + 0.01,
        f"overflows by {content_right_edge - printable_w:.3f}in — text will be clipped"
    )

print("\n── Copy: no combative language ──────────────────────────────────────")

for phrase in ["you don't need", "you do not need", "pay to breathe", "don't pay"]:
    check(f'No "{phrase}"', phrase.lower() not in html.lower(), "found in HTML")

print("\n── Copy: key phrases present ────────────────────────────────────────")

for phrase in ["breathing has always been free", "explore", "free to breathe"]:
    check(f'"{phrase}" present', phrase.lower() in html.lower())

print("\n── Schedule config ──────────────────────────────────────────────────")

check("SESSIONS array defined", "const SESSIONS" in html)
check("SESSION_TIME defined", "const SESSION_TIME" in html)
count = len(re.findall(r"\{\s*date:", html))
check(f"At least 1 session ({count} found)", count >= 1)

print()
if failures:
    print(f"  {len(failures)} check(s) failed: {', '.join(failures)}\n")
    sys.exit(1)
else:
    print(f"  All checks passed.\n")
