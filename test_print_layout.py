"""
Automated checks for freebreathwork.org print layout and copy.

Verifies CSS height math so the 2-up flyer always fits on one letter page,
and checks that combative copy hasn't crept back in.

Run:  python3 test_print_layout.py
"""

import re
import sys

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"

failures = []

def check(label, condition, detail=""):
    if condition:
        print(f"  {PASS}  {label}")
    else:
        print(f"  {FAIL}  {label}" + (f" — {detail}" if detail else ""))
        failures.append(label)

with open("index.html") as f:
    html = f.read()

print("\n── Print layout dimensions ──────────────────────────────────────────")

# Extract @page margin
margin_match = re.search(r"@page\s*\{[^}]*margin:\s*([\d.]+)in", html)
page_margin_in = float(margin_match.group(1)) if margin_match else None
check("@page margin is defined in inches", page_margin_in is not None)

# Extract flyer height
flyer_h_match = re.search(r"\.flyer\s*\{[^}]*height:\s*([\d.]+)in", html, re.DOTALL)
flyer_h_in = float(flyer_h_match.group(1)) if flyer_h_match else None
check("Flyer height is defined in inches", flyer_h_in is not None)

# Extract cut line height
cut_h_match = re.search(r"\.flyer-cut\s*\{[^}]*height:\s*([\d.]+)in", html, re.DOTALL)
cut_h_in = float(cut_h_match.group(1)) if cut_h_match else None
check("Cut line height is defined in inches", cut_h_in is not None)

if page_margin_in and flyer_h_in and cut_h_in:
    letter_h = 11.0
    printable_h = letter_h - (page_margin_in * 2)
    total_content = (flyer_h_in * 2) + cut_h_in
    fits = total_content <= printable_h + 0.01  # 0.01in rounding tolerance
    check(
        f"Two flyers ({flyer_h_in}in × 2) + cut ({cut_h_in}in) = {total_content}in "
        f"fits in printable height {printable_h}in",
        fits,
        f"overflow by {total_content - printable_h:.3f}in" if not fits else ""
    )

print("\n── Copy: no combative language ─────────────────────────────────────")

combative = [
    "you don't need",
    "you do not need",
    "pay to breathe",
    "don't pay",
]
for phrase in combative:
    present = phrase.lower() in html.lower()
    check(f'No "{phrase}" in copy', not present, "found in HTML")

print("\n── Copy: positive phrases present ──────────────────────────────────")

positive = [
    "breathing has always been free",
    "explore",
    "free to breathe",
]
for phrase in positive:
    check(f'"{phrase}" present', phrase.lower() in html.lower())

print("\n── Schedule config ──────────────────────────────────────────────────")

check("SESSIONS array defined", "const SESSIONS" in html)
check("SESSION_TIME defined", "const SESSION_TIME" in html)
session_count = len(re.findall(r"\{\s*date:", html))
check(f"At least 1 session defined ({session_count} found)", session_count >= 1)

print()
if failures:
    print(f"  {len(failures)} check(s) failed: {', '.join(failures)}\n")
    sys.exit(1)
else:
    print(f"  All checks passed.\n")
