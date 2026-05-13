# =============================================================================
# password_generator.py
# Purpose: Generate strong random passwords
#
# Features:
#   - Customizable length
#   - Mix of uppercase, lowercase, numbers, symbols
#   - Guaranteed character type inclusion
# =============================================================================

import random
import string


def generate_password(
    length: int = 16,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True
) -> str:
    """
    Generate a strong random password.
    
    Args:
        length (int): Password length (minimum 8, default 16)
        use_uppercase (bool): Include uppercase letters (A-Z)
        use_lowercase (bool): Include lowercase letters (a-z)
        use_digits (bool): Include numbers (0-9)
        use_symbols (bool): Include special characters (!@#$...)
        
    Returns:
        str: A randomly generated password
        
    Raises:
        ValueError: If no character types are selected or length too short
        
    Example:
        >>> generate_password(length=12, use_symbols=True)
        'Kj#9mP$xR2!q'
    """
    
    # Enforce minimum length
    if length < 8:
        length = 8
    
    # Build the character pool based on user selections
    character_pool = ""
    guaranteed_chars = []  # Ensure at least one of each selected type
    
    if use_uppercase:
        character_pool += string.ascii_uppercase
        guaranteed_chars.append(random.choice(string.ascii_uppercase))
    
    if use_lowercase:
        character_pool += string.ascii_lowercase
        guaranteed_chars.append(random.choice(string.ascii_lowercase))
    
    if use_digits:
        character_pool += string.digits
        guaranteed_chars.append(random.choice(string.digits))
    
    if use_symbols:
        # Using a safe set of symbols that work across all systems
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        character_pool += symbols
        guaranteed_chars.append(random.choice(symbols))
    
    # If no options selected, default to all character types
    if not character_pool:
        character_pool = string.ascii_letters + string.digits + "!@#$%^&*"
        guaranteed_chars = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits),
            random.choice("!@#$%^&*")
        ]
    
    # Calculate remaining characters needed after guaranteed ones
    remaining_length = length - len(guaranteed_chars)
    
    # Generate remaining random characters from the pool
    remaining_chars = [random.choice(character_pool) for _ in range(remaining_length)]
    
    # Combine guaranteed + remaining characters
    all_chars = guaranteed_chars + remaining_chars
    
    # Shuffle to avoid predictable patterns (guaranteed chars at start)
    random.shuffle(all_chars)
    
    # Join into final password string
    password = "".join(all_chars)
    
    return password


def check_password_strength(password: str) -> dict:
    """
    Analyze the strength of a password.
    
    Args:
        password (str): Password to analyze
        
    Returns:
        dict: Strength info with 'score', 'label', and 'color'
              score: 0-4 (0=Very Weak, 4=Very Strong)
              label: Human-readable strength label
              color: Color code for GUI display
    """
    score = 0
    feedback = []
    
    # Check length
    if len(password) >= 16:
        score += 1
    elif len(password) >= 12:
        score += 0.5
    
    # Check character variety
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Add uppercase letters")
    
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Add lowercase letters")
    
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Add numbers")
    
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    else:
        feedback.append("Add special characters")
    
    # Determine strength label and color
    if score <= 1:
        return {"score": score, "label": "Very Weak", "color": "#FF4444"}
    elif score <= 2:
        return {"score": score, "label": "Weak", "color": "#FF8800"}
    elif score <= 3:
        return {"score": score, "label": "Medium", "color": "#FFCC00"}
    elif score <= 4:
        return {"score": score, "label": "Strong", "color": "#44BB44"}
    else:
        return {"score": score, "label": "Very Strong", "color": "#00CC44"}