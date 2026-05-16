def calculate_bills(amount: int):
    # This is the "Smart Look-Ahead" Matrix you provided
    # Format: { total_amount: (₱100s, ₱50s, ₱20s) }
    matrix = {
        20: (0, 0, 1),  40: (0, 0, 2),  50: (0, 1, 0),
        60: (0, 0, 3),  70: (0, 1, 1),  80: (0, 0, 4),
        90: (0, 1, 2),  100: (1, 0, 0), 110: (0, 1, 3), # Logic override
        120: (1, 0, 1), 130: (0, 1, 4), 140: (1, 0, 2), # Logic override
        150: (1, 1, 0), 160: (1, 0, 3), 170: (1, 1, 1),
        180: (1, 0, 4), 190: (1, 1, 2), 200: (2, 0, 0),
        210: (1, 1, 3), 220: (2, 0, 1), 230: (1, 1, 4), # Logic overrides
        240: (2, 0, 2), 250: (2, 1, 0), 260: (2, 0, 3),
        270: (2, 1, 1), 280: (2, 0, 4), 290: (2, 1, 2),
        300: (3, 0, 0)
    }
    
    return matrix.get(amount, (0, 0, 0))

# Usage Example:
# bills_100, bills_50, coins_20 = calculate_bills(110)
# Result: 0, 1, 3