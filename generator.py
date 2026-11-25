"""
Core password generator logic with cryptographically secure randomization and strength assessment.
"""

import math
import secrets
import string
from typing import Dict, List, Tuple

UPPERCASE_CHARS = string.ascii_uppercase
LOWERCASE_CHARS = string.ascii_lowercase
DIGIT_CHARS = string.digits
SYMBOL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
AMBIGUOUS_CHARS = set("0Ool1I|`'\"~")


def get_available_pools(
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> Dict[str, str]:
    """Returns the dictionary of character pools based on user options."""
    pools = {}

    def filter_chars(chars: str) -> str:
        if exclude_ambiguous:
            return "".join(c for c in chars if c not in AMBIGUOUS_CHARS)
        return chars

    if use_upper:
        p = filter_chars(UPPERCASE_CHARS)
        if p:
            pools["upper"] = p
    if use_lower:
        p = filter_chars(LOWERCASE_CHARS)
        if p:
            pools["lower"] = p
    if use_digits:
        p = filter_chars(DIGIT_CHARS)
        if p:
            pools["digits"] = p
    if use_symbols:
        p = filter_chars(SYMBOL_CHARS)
        if p:
            pools["symbols"] = p

    return pools


def generate_password(
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> str:
    """
    Generates a cryptographically secure password based on selected character pools.
    Ensures at least one character from each selected category is present if length allows.
    """
    pools = get_available_pools(
        use_upper=use_upper,
        use_lower=use_lower,
        use_digits=use_digits,
        use_symbols=use_symbols,
        exclude_ambiguous=exclude_ambiguous,
    )

    if not pools:
        # Fallback if nothing was selected
        pools["lower"] = string.ascii_lowercase

    rng = secrets.SystemRandom()
    chosen_chars: List[str] = []

    # Ensure at least one character from each active pool if space permits
    pool_keys = list(pools.keys())
    if length >= len(pool_keys):
        for key in pool_keys:
            chosen_chars.append(rng.choice(pools[key]))

    # Fill the remainder of the length from combined pool
    all_allowed = "".join(pools.values())
    remaining_count = max(0, length - len(chosen_chars))
    for _ in range(remaining_count):
        chosen_chars.append(rng.choice(all_allowed))

    # Secure shuffle to prevent predictable placement
    rng.shuffle(chosen_chars)
    return "".join(chosen_chars[:length])


def evaluate_strength(password: str) -> Tuple[int, str, Tuple[int, int, int]]:
    """
    Calculates password score (0-100), descriptive label, and RGB color.
    Considers length, character variety, and entropy.
    """
    if not password:
        return 0, "None", (100, 100, 110)

    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in SYMBOL_CHARS for c in password)

    variety_count = sum([has_upper, has_lower, has_digit, has_symbol])

    # Pool size estimation
    pool_size = 0
    if has_upper:
        pool_size += 26
    if has_lower:
        pool_size += 26
    if has_digit:
        pool_size += 10
    if has_symbol:
        pool_size += len(SYMBOL_CHARS)
    pool_size = max(pool_size, 1)

    # Shannon / Information entropy in bits
    entropy = length * math.log2(pool_size)

    # Base score calculated from entropy & variety
    score = int(min(100, max(5, (entropy / 105.0) * 100)))

    # Bonus / penalty based on length & variety
    if length < 8:
        score = min(score, 30)
    elif length >= 16 and variety_count >= 3:
        score = max(score, 75)
    if length >= 20 and variety_count == 4:
        score = max(score, 95)

    if score < 25:
        return score, "Very Weak", (243, 139, 168)  # Catppuccin Red
    elif score < 50:
        return score, "Weak", (250, 179, 135)       # Catppuccin Peach
    elif score < 70:
        return score, "Fair", (249, 226, 175)       # Catppuccin Yellow
    elif score < 90:
        return score, "Strong", (166, 227, 161)     # Catppuccin Green
    else:
        return score, "Very Strong", (148, 226, 213) # Catppuccin Teal
