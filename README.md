# HIT137 Group Assesstment-2

Group submission for HIT137 Assignment 2 (20% mark).
#Group Members
Name | Student ID | GitHub | Question 1 (cipher.py) | Question 2 (evaluator.py) |
|------|-----------|--------|:---:|:---:|
| Pawan Koirala | S408952 | Purshottam285 | ✅ | ✅ |
| Parivesh Khadka Chhetri | S398438 | prabeshkhadka001-gif| ✅ | ✅ |
| Noel Maksymilian Karunathilake| S389821 | noelmaskym | | ✅ |  |

**Question 1 (cipher.py):** Pawan Koirala and Parivesh Khadka Chhetri
**Question 2 (evaluator.py):** Pawan Koirala,Parivesh Khadka Chhetri and Noel Karunathilake

GitHub repository: https://github.com/Purshottam285/HIT137-Assignment2
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

**Note about verification.** The encryption method changes each letter based
on whether it originally came from the first or second half of the alphabet.
After encryption, that original information is no longer available. To deal
with this, the decryption process checks both possible reverse shifts  and 
keeps the result that fits the correct half of the alphabet. In most cases
this recreates the original text, but some shift contributors can produce two
valid results, making cipher naturally ambiguous. The `verify_files` clearly
indicates whether the recovered text matches the original.


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
