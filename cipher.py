"""
HIT137 Group Assessment-2 - Question 1
cipher.py

Reads raw_text.txt, encrypts using a two-input shift cipher, writes
encrypted_text.txt, decrypts the encrypted file to decrypted_text.txt,
and verifies the decryption matches the original.

Encryption rules (per assignment brief):
    Lowercase a-n : shift forward  by (shift1 * shift2)
    Lowercase o-z : shift backward by (shift1 + shift2)
    Uppercase A-M : shift backward by  shift1
    Uppercase N-Z : shift forward  by (shift2 ** 2)
    Digits 0-9    : shift forward  by (shift1 - shift2)
    Everything else (spaces, punctuation, symbols): unchanged.

Decryption note:
    The rule that applied to a letter depends on which half of the alphabet the
    ORIGINAL letter came from. After encryption we no longer know that half
    directly, so decryption tries both possible inverse shifts and keeps the
    one whose recovered letter falls back into the correct half. In rare
    combinations of shift1 and shift2, both inverses can land in valid halves,
    which produces an unavoidable ambiguity - verify_files() will detect and
    report any such mismatch.
"""


# ---------------------------------------------------------------------------
# Per-character transformations
# ---------------------------------------------------------------------------

def _encrypt_char(ch: str, shift1: int, shift2: int) -> str:
    """Encrypt a single character using the rules in the brief."""
    if ch.islower():
        base = ord('a')
        idx = ord(ch) - base           # 0..25
        if idx <= 13:                  # a-n (first half)
            new_idx = (idx + shift1 * shift2) % 26
        else:                          # o-z (second half)
            new_idx = (idx - (shift1 + shift2)) % 26
        return chr(base + new_idx)

    if ch.isupper():
        base = ord('A')
        idx = ord(ch) - base           # 0..25
        if idx <= 12:                  # A-M (first half)
            new_idx = (idx - shift1) % 26
        else:                          # N-Z (second half)
            new_idx = (idx + shift2 ** 2) % 26
        return chr(base + new_idx)

    if ch.isdigit():
        new_digit = (int(ch) + (shift1 - shift2)) % 10
        return str(new_digit)

    # Spaces, tabs, newlines, punctuation, symbols pass through untouched.
    return ch


def _decrypt_char(ch: str, shift1: int, shift2: int) -> str:
    """Invert the encryption for a single character.

    For letters we do not know which half the original was in, so we try both
    possible inverse shifts and choose the one whose recovered letter falls
    into the matching half.
    """
    if ch.islower():
        base = ord('a')
        e_idx = ord(ch) - base

        # If original was in first half (a-n), encrypted = orig + shift1*shift2
        cand_first  = (e_idx - shift1 * shift2) % 26
        # If original was in second half (o-z), encrypted = orig - (shift1+shift2)
        cand_second = (e_idx + (shift1 + shift2)) % 26

        first_valid  = cand_first  <= 13   # a-n
        second_valid = cand_second >= 14   # o-z

        if first_valid and not second_valid:
            return chr(base + cand_first)
        if second_valid and not first_valid:
            return chr(base + cand_second)
        # Ambiguous or neither valid - default to first-half interpretation.
        return chr(base + (cand_first if first_valid else cand_second))

    if ch.isupper():
        base = ord('A')
        e_idx = ord(ch) - base

        # First half (A-M) rule was: encrypted = orig - shift1
        cand_first  = (e_idx + shift1) % 26
        # Second half (N-Z) rule was: encrypted = orig + shift2**2
        cand_second = (e_idx - shift2 ** 2) % 26

        first_valid  = cand_first  <= 12   # A-M
        second_valid = cand_second >= 13   # N-Z

        if first_valid and not second_valid:
            return chr(base + cand_first)
        if second_valid and not first_valid:
            return chr(base + cand_second)
        return chr(base + (cand_first if first_valid else cand_second))

    if ch.isdigit():
        new_digit = (int(ch) - (shift1 - shift2)) % 10
        return str(new_digit)

    return ch


# ---------------------------------------------------------------------------
# File-level functions required by the brief
# ---------------------------------------------------------------------------

def encrypt_file(shift1: int, shift2: int,
                 input_path: str, output_path: str) -> None:
    """Read input_path, encrypt every character, write to output_path."""
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    encrypted = ''.join(_encrypt_char(c, shift1, shift2) for c in text)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(encrypted)


def decrypt_file(shift1: int, shift2: int,
                 input_path: str, output_path: str) -> None:
    """Read input_path, decrypt every character, write to output_path."""
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    decrypted = ''.join(_decrypt_char(c, shift1, shift2) for c in text)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decrypted)


def verify_files(original_path: str, decrypted_path: str) -> bool:
    """Compare the two files. Print outcome and return True on match."""
    with open(original_path, 'r', encoding='utf-8') as f:
        original = f.read()
    with open(decrypted_path, 'r', encoding='utf-8') as f:
        decrypted = f.read()

    if original == decrypted:
        print("Verification SUCCESSFUL: decrypted file matches the original.")
        return True

    print("Verification FAILED: decrypted file does not match the original.")
    # Point at the first divergence to help debugging.
    for i, (a, b) in enumerate(zip(original, decrypted)):
        if a != b:
            print(f"  First mismatch at position {i}: "
                  f"original={a!r}, decrypted={b!r}")
            break
    if len(original) != len(decrypted):
        print(f"  Length differs: original={len(original)}, "
              f"decrypted={len(decrypted)}")
    return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _prompt_non_negative_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if value < 0:
                print("  Value must be non-negative. Please try again.")
                continue
            return value
        except ValueError:
            print("  Not a valid integer. Please try again.")


def main() -> None:
    print("HIT137 Assignment 2 - Question 1: Shift cipher")
    print("-" * 48)

    shift1 = _prompt_non_negative_int("Enter shift1 (non-negative integer): ")
    shift2 = _prompt_non_negative_int("Enter shift2 (non-negative integer): ")

    encrypt_file(shift1, shift2, "raw_text.txt", "encrypted_text.txt")
    print("Encrypted -> encrypted_text.txt")

    decrypt_file(shift1, shift2, "encrypted_text.txt", "decrypted_text.txt")
    print("Decrypted -> decrypted_text.txt")

    verify_files("raw_text.txt", "decrypted_text.txt")


if __name__ == "__main__":
    main()
