"""
HIT137 Group Assessment-2 - Question 2
evaluator.py

Reads mathematical expressions from a text file (one per line), evaluates
each using a recursive-descent parser built from plain functions, and
writes the results to output.txt in the same directory as the input file.

Grammar (highest precedence at the bottom):

    expr    -> term  (('+' | '-') term)*
    term    -> unary (('*' | '/' | '%') unary  |  implicit_mul unary)*
    unary   -> '-' unary  |  power
    power   -> primary ('^' unary)?             # right-associative
    primary -> NUMBER  |  '(' expr ')'

Notes:
    * Implicit multiplication is allowed between adjacent factors when at
      least one side is a parenthesis (e.g. 2(3+4), (3+4)2, (1)(2)).
      Two adjacent numbers such as "2 3" are treated as an error.
    * Unary + is not supported and produces an error.
    * Errors are reported per expression - tokenisation, parsing and
      runtime failures each set the relevant output field(s) to "ERROR".
"""

import os


# ---------------------------------------------------------------------------
# Custom exceptions used to keep error handling clean
# ---------------------------------------------------------------------------

class TokenError(Exception):
    """Raised when the input contains an illegal character."""


class ParseError(Exception):
    """Raised when the token stream cannot be parsed by the grammar."""


class EvalError(Exception):
    """Raised when a valid parse tree cannot be evaluated (e.g. div by 0)."""


# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------
#
# A token is a tuple (type, value).
# Types: 'NUM', 'OP', 'LPAREN', 'RPAREN', 'END'.

def tokenize(expr):
    """Turn a raw expression string into a list of tokens ending with END."""
    tokens = []
    i, n = 0, len(expr)
    while i < n:
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit():
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            # Optional single '.' followed by one or more digits
            if j < n and expr[j] == '.':
                if j + 1 < n and expr[j + 1].isdigit():
                    j += 1
                    while j < n and expr[j].isdigit():
                        j += 1
                else:
                    raise TokenError(f"Malformed number at position {i}")
            tokens.append(('NUM', expr[i:j]))
            i = j
            continue

        if ch in '+-*/%^':
            tokens.append(('OP', ch))
            i += 1
            continue

        if ch == '(':
            tokens.append(('LPAREN', '('))
            i += 1
            continue

        if ch == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
            continue

        # Anything else is an illegal character (e.g. '@').
        raise TokenError(f"Unexpected character {ch!r} at position {i}")

    tokens.append(('END', ''))
    return tokens


# ---------------------------------------------------------------------------
# Recursive-descent parser
# ---------------------------------------------------------------------------
#
# The parser walks a shared list of tokens with an integer position. Each
# non-terminal in the grammar is implemented as its own function, and
# parenthesised sub-expressions recurse back to parse_expr().
#
# Tree node shapes:
#     ('num',   value_string)
#     ('neg',   child_node)
#     ('binop', op_char, left_node, right_node)

def _peek(tokens, pos, offset=0):
    return tokens[pos + offset]


def _previous(tokens, pos):
    if pos == 0:
        return None
    return tokens[pos - 1]


def parse_expr(tokens, pos):
    """Level 1: addition and subtraction (left-associative)."""
    left, pos = parse_term(tokens, pos)
    while True:
        t = _peek(tokens, pos)
        if t[0] == 'OP' and t[1] in ('+', '-'):
            op = t[1]
            pos += 1
            right, pos = parse_term(tokens, pos)
            left = ('binop', op, left, right)
        else:
            break
    return left, pos


def parse_term(tokens, pos):
    """Level 2: multiplication, division, modulo and implicit multiplication."""
    left, pos = parse_unary(tokens, pos)
    while True:
        t = _peek(tokens, pos)
        prev = _previous(tokens, pos)

        # Explicit multiplicative operator
        if t[0] == 'OP' and t[1] in ('*', '/', '%'):
            op = t[1]
            pos += 1
            right, pos = parse_unary(tokens, pos)
            left = ('binop', op, left, right)
            continue

        # Implicit multiplication: ) followed by ( , NUM before ( , ) before NUM
        implicit = False
        if t[0] == 'LPAREN' and prev is not None and prev[0] in ('NUM', 'RPAREN'):
            implicit = True
        elif t[0] == 'NUM' and prev is not None and prev[0] == 'RPAREN':
            implicit = True

        if implicit:
            right, pos = parse_unary(tokens, pos)
            left = ('binop', '*', left, right)
            continue

        break
    return left, pos


def parse_unary(tokens, pos):
    """Level 3: prefix unary minus. Unary + is rejected here."""
    t = _peek(tokens, pos)
    if t[0] == 'OP' and t[1] == '-':
        pos += 1
        operand, pos = parse_unary(tokens, pos)
        return ('neg', operand), pos
    if t[0] == 'OP' and t[1] == '+':
        raise ParseError("Unary '+' is not supported")
    return parse_power(tokens, pos)


def parse_power(tokens, pos):
    """Level 4: exponentiation, right-associative (recurse into unary on RHS)."""
    left, pos = parse_primary(tokens, pos)
    t = _peek(tokens, pos)
    if t[0] == 'OP' and t[1] == '^':
        pos += 1
        right, pos = parse_unary(tokens, pos)
        left = ('binop', '^', left, right)
    return left, pos


def parse_primary(tokens, pos):
    """Number literal or parenthesised sub-expression."""
    t = _peek(tokens, pos)
    if t[0] == 'NUM':
        pos += 1
        return ('num', t[1]), pos
    if t[0] == 'LPAREN':
        pos += 1
        inner, pos = parse_expr(tokens, pos)
        closing = _peek(tokens, pos)
        if closing[0] != 'RPAREN':
            raise ParseError("Expected closing ')'")
        pos += 1
        return inner, pos
    raise ParseError(f"Unexpected token {t}")


def parse(tokens):
    """Parse the full token list and confirm we consumed everything."""
    tree, pos = parse_expr(tokens, 0)
    if _peek(tokens, pos)[0] != 'END':
        raise ParseError(f"Unexpected trailing token {_peek(tokens, pos)}")
    return tree


# ---------------------------------------------------------------------------
# Evaluator - walks the parse tree and produces a numeric value
# ---------------------------------------------------------------------------

def evaluate_tree(node):
    kind = node[0]
    if kind == 'num':
        return float(node[1])
    if kind == 'neg':
        return -evaluate_tree(node[1])
    if kind == 'binop':
        _, op, left_node, right_node = node
        left = evaluate_tree(left_node)
        right = evaluate_tree(right_node)
        if op == '+':
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            if right == 0:
                raise EvalError("Division by zero")
            return left / right
        if op == '%':
            if right == 0:
                raise EvalError("Modulo by zero")
            return left % right
        if op == '^':
            try:
                return left ** right
            except (OverflowError, ValueError) as exc:
                raise EvalError(str(exc))
    raise EvalError(f"Unknown node kind {kind!r}")


# ---------------------------------------------------------------------------
# Formatters used for the output.txt file
# ---------------------------------------------------------------------------

def _format_num_literal(value_str):
    """Format a number literal for display.

    If the literal is a whole number (like '3' or '10') we show it as an
    integer; if it has a decimal part we keep the value as-is.
    """
    try:
        v = float(value_str)
    except ValueError:
        return value_str
    if v.is_integer() and '.' not in value_str:
        return str(int(v))
    return value_str


def format_tree(node):
    """Produce the parenthesised prefix form used on the Tree line."""
    kind = node[0]
    if kind == 'num':
        return _format_num_literal(node[1])
    if kind == 'neg':
        return f"(neg {format_tree(node[1])})"
    if kind == 'binop':
        _, op, left, right = node
        return f"({op} {format_tree(left)} {format_tree(right)})"
    return "ERROR"


def format_tokens(tokens):
    """Produce the [TYPE:value] line used on the Tokens line."""
    parts = []
    for t in tokens:
        ttype, tval = t
        if ttype == 'END':
            parts.append('[END]')
        elif ttype == 'NUM':
            parts.append(f'[NUM:{_format_num_literal(tval)}]')
        elif ttype == 'OP':
            parts.append(f'[OP:{tval}]')
        elif ttype == 'LPAREN':
            parts.append('[LPAREN:(]')
        elif ttype == 'RPAREN':
            parts.append('[RPAREN:)]')
    return ' '.join(parts)


def format_result(value):
    """Whole numbers -> no decimal point; otherwise round to 4 decimals."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(round(value, 4))


# ---------------------------------------------------------------------------
# Public entry point required by the brief
# ---------------------------------------------------------------------------

def evaluate_file(input_path: str) -> list[dict]:
    """Evaluate every expression in input_path, write output.txt beside it,
    and return a list of per-expression dictionaries.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    results = []
    output_blocks = []

    for raw_line in lines:
        expr = raw_line.rstrip('\r\n')
        if expr.strip() == '':
            # Skip blank lines in the input, but keep going.
            continue

        block = {'input': expr}

        # --- Stage 1: tokenise ---
        try:
            tokens = tokenize(expr)
            tokens_str = format_tokens(tokens)
        except TokenError:
            block['tree'] = 'ERROR'
            block['tokens'] = 'ERROR'
            block['result'] = 'ERROR'
            results.append(block)
            output_blocks.append(_render_block(block))
            continue

        # --- Stage 2: parse ---
        try:
            tree = parse(tokens)
            tree_str = format_tree(tree)
        except ParseError:
            block['tree'] = 'ERROR'
            block['tokens'] = tokens_str
            block['result'] = 'ERROR'
            results.append(block)
            output_blocks.append(_render_block(block))
            continue

        # --- Stage 3: evaluate ---
        try:
            value = evaluate_tree(tree)
        except (EvalError, ZeroDivisionError, ArithmeticError):
            block['tree'] = tree_str
            block['tokens'] = tokens_str
            block['result'] = 'ERROR'
            results.append(block)
            output_blocks.append(_render_block(block))
            continue

        block['tree'] = tree_str
        block['tokens'] = tokens_str
        block['result'] = float(value)   # spec: float on success
        # For the output file we use the string-formatted version.
        results.append(block)
        output_blocks.append(_render_block({
            'input': expr,
            'tree': tree_str,
            'tokens': tokens_str,
            'result': format_result(value),
        }))

    # Write output.txt into the same directory as the input file.
    out_dir = os.path.dirname(os.path.abspath(input_path))
    out_path = os.path.join(out_dir, 'output.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(output_blocks))
        # Trailing newline for POSIX-friendliness
        if output_blocks:
            f.write('\n')

    return results


def _render_block(block):
    """Render one four-line block for output.txt."""
    return (
        f"Input: {block['input']}\n"
        f"Tree: {block['tree']}\n"
        f"Tokens: {block['tokens']}\n"
        f"Result: {block['result']}"
    )


# ---------------------------------------------------------------------------
# Run this as a script
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    default_path = "input.txt"
    path = sys.argv[1] if len(sys.argv) > 1 else default_path
    print(f"Evaluating expressions from {path} ...")
    outcomes = evaluate_file(path)
    print(f"Wrote output.txt with {len(outcomes)} expression block(s).")
