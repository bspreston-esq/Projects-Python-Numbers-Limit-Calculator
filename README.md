# Limit Calculator

**Category:** Numbers

## Problem

Ask the user to enter f(x) and the limit value, then return the value of the limit statement. Optional: Make the calculator capable of supporting infinite limits.

## Solution

Parses f(x) with a strict AST whitelist, then probes the function at progressively closer points (h = 1e-2 ... 1e-8) on each requested side. Values are accepted when the last four samples agree to within 0.1%; growing magnitudes are reported as divergence, and mismatched one-sided limits as "does not exist". Infinite limit points use x = 10^1 ... 10^8.

## How to run

Requires Python 3.8+ and no third-party packages.

```bash
python3 main.py --function "(x**2-4)/(x-2)" --at 2
python3 main.py --function "sin(x)/x" --at 0
python3 main.py --function "(1+1/x)**x" --at inf
python3 main.py --demo
```

## Example

```text
lim x->2    (x**2 - 4)/(x - 2) = 4              [two-sided]
lim x->0    sin(x)/x           = 1              [two-sided]
lim x->inf  (1 + 1/x)**x       = 2.71828        [at infinity]
lim x->0    1/x                = does not exist [one-sided limit does not exist]
```

## Attribution

The problem statement is from [karan/Projects](https://github.com/karan/Projects), a list of practical projects that anyone can solve in any programming language (MIT License, Copyright (c) 2013 Karan Goel). The Python solution in this repository was implemented by [bspreston-esq](https://github.com/bspreston-esq).

This repository is part of the [Projects-Python-All](https://github.com/bspreston-esq/Projects-Python-All) collection.
