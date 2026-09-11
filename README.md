# HIT137 Group Assignment 2

Group submission for HIT137 Assignment 2 (20% mark).

## Contents

| File | Description |
|---|---|
| `cipher.py` | Question 1 - two-input shift cipher (encrypt / decrypt / verify). |
| `evaluator.py` | Question 2 - recursive-descent expression evaluator. |
| `raw_text.txt` | Sample input text for Question 1 (supplied by the unit). |
| `sample_input.txt` | Sample input expressions for Question 2 (supplied by the unit). |
| `sample_output.txt` | Expected output for Question 2 (supplied by the unit). |
| `input.txt` | Working input file used when running `evaluator.py`. |
| `output.txt` | Produced by `evaluator.py` when it runs. |
| `encrypted_text.txt` | Produced by `cipher.py` when it runs. |
| `decrypted_text.txt` | Produced by `cipher.py` when it runs. |
| `github_link.txt` | The public GitHub repository URL for this assignment. |

## Requirements

Python 3.9 or later. No third-party packages are used.

## How to run

### Question 1

```bash
python3 cipher.py
```

The program prompts for `shift1` and `shift2` (non-negative integers), then:

1. Reads `raw_text.txt`.
2. Encrypts it and writes `encrypted_text.txt`.
3. Decrypts that file and writes `decrypted_text.txt`.
4. Prints whether the decryption matches the original.

**Note on verification.** The encryption rule for a letter depends on
which half of the alphabet the *original* letter came from. Once encrypted,
that information is lost, so decryption tries both possible inverse shifts
and chooses the one whose recovered letter lands in the matching half.
For most shift pairs this recovers the original text; for some pairs the
two candidates are both valid and the cipher is inherently ambiguous. The
`verify_files` function reports success or failure clearly in every case.

### Question 2

```bash
python3 evaluator.py input.txt
```

If no path is given the program uses `input.txt` from the current directory.
It writes `output.txt` next to the input, and each expression produces a
four-line `Input / Tree / Tokens / Result` block separated by a blank line.

The public entry point is:

```python
from evaluator import evaluate_file
results = evaluate_file("input.txt")
```

`results` is a list of dictionaries with keys `input`, `tree`, `tokens`,
`result`. `result` is a `float` on success or the string `"ERROR"` on
failure. `tree` and `tokens` are strings (or `"ERROR"`).

## Grammar summary (Question 2)

From lowest to highest precedence:

| Level | Operators | Associativity |
|---|---|---|
| 1 | `+` `-` | left |
| 2 | `*` `/` `%` and implicit multiplication | left |
| 3 | unary `-` | prefix |
| 4 | `^` | right |

* Unary `+` is **not** supported and produces `ERROR`.
* Two adjacent numbers such as `2 3` are **not** implicit multiplication
  and produce `ERROR`. Implicit multiplication requires at least one
  parenthesis at the boundary (e.g. `2(3+4)`, `(1)(2)`, `(1+2)3`).
