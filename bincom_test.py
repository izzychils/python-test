import os
import re
import random
import math
from collections import Counter
from html.parser import HTMLParser

# 0.  PARSE THE HTML FILE AND EXTRACT COLOUR DATA

try:
    from bs4 import BeautifulSoup

    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(html_path, "r") as f:
        soup = BeautifulSoup(f, "html.parser")

    rows = soup.select("tbody tr")
    all_colours = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 2:
            colours_text = cells[1].text.strip()
            colours = [c.strip().upper() for c in colours_text.split(",") if c.strip()]
            all_colours.extend(colours)

except ImportError:
    
    print("[INFO] BeautifulSoup not found — falling back to regex parser.\n")
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(html_path, "r") as f:
        html_content = f.read()

    pattern = re.compile(r"<td>(?:MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY)</td>\s*<td>(.*?)</td>", re.DOTALL)
    matches = pattern.findall(html_content)
    all_colours = []
    for match in matches:
        colours = [c.strip().upper() for c in match.split(",") if c.strip()]
        all_colours.extend(colours)

colour_counts = Counter(all_colours)

print("=" * 65)
print("  BINCOM ICT — PYTHON BASIC DEVELOPER TEST")
print("=" * 65)

print(f"\nTotal colour entries parsed: {len(all_colours)}")
print(f"Unique colours found:       {len(colour_counts)}\n")
print("Colour Frequency Table:")
print("-" * 35)
for colour, count in colour_counts.most_common():
    print(f"  {colour:<12} : {count}")
print("-" * 35)

# 1.  MEAN COLOUR

print("\n" + "=" * 65)
print("  1. MEAN COLOUR")
print("=" * 65)

frequencies = list(colour_counts.values())
mean_freq = sum(frequencies) / len(frequencies)
print(f"\nMean frequency: {mean_freq:.2f}")

# Find the colour(s) closest to the mean frequency
min_diff = min(abs(f - mean_freq) for f in frequencies)
mean_colours = [c for c, f in colour_counts.items() if abs(f - mean_freq) == min_diff]
print(f"Colour(s) closest to mean frequency: {', '.join(mean_colours)}")

# ──────────────────────────────────────────────────────────────────────────────
# 2.  MOST WORN COLOUR (MODE)
# ──────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 65)
print("  2. MOST WORN COLOUR THROUGHOUT THE WEEK")
print("=" * 65)

most_common_colour, most_common_count = colour_counts.most_common(1)[0]
print(f"\nMost worn colour: {most_common_colour} (worn {most_common_count} times)")


# 3.  MEDIAN COLOUR

print("\n" + "=" * 65)
print("  3. MEDIAN COLOUR")
print("=" * 65)

sorted_colours = sorted(all_colours)
n = len(sorted_colours)
if n % 2 == 1:
    median_colour = sorted_colours[n // 2]
else:
    median_colour = sorted_colours[n // 2 - 1]

print(f"\nTotal entries (sorted): {n}")
print(f"Median colour: {median_colour}")

# 4.  BONUS — VARIANCE OF THE COLOURS

print("\n" + "=" * 65)
print("  4. VARIANCE OF THE COLOURS")
print("=" * 65)

variance = sum((f - mean_freq) ** 2 for f in frequencies) / len(frequencies)
std_dev = math.sqrt(variance)
print(f"\nPopulation Variance : {variance:.4f}")
print(f"Standard Deviation  : {std_dev:.4f}")


# 5.  BONUS — PROBABILITY OF RED

print("\n" + "=" * 65)
print("  5. PROBABILITY THAT A RANDOMLY CHOSEN COLOUR IS RED")
print("=" * 65)

red_count = colour_counts.get("RED", 0)
total = len(all_colours)
prob_red = red_count / total
print(f"\nRed count   : {red_count}")
print(f"Total count : {total}")
print(f"P(Red)      : {red_count}/{total} = {prob_red:.4f} ({prob_red * 100:.2f}%)")

# 6.  SAVE COLOURS AND FREQUENCIES TO POSTGRESQL

print("\n" + "=" * 65)
print("  6. SAVE TO POSTGRESQL DATABASE")
print("=" * 65)


def save_to_postgresql(colour_freq: dict):
    """
    Creates a table `colour_frequency` and inserts colour data.
    Adjust the connection parameters below to match your PostgreSQL setup.
    """
    try:
        import psycopg2

        conn = psycopg2.connect(
            host="localhost",
            database="bincom_test",     
            user="postgres",            
            password="your_password"    
        )
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS colour_frequency (
                id SERIAL PRIMARY KEY,
                colour VARCHAR(50) NOT NULL UNIQUE,
                frequency INTEGER NOT NULL
            );
        """)

        for colour, freq in colour_freq.items():
            cur.execute("""
                INSERT INTO colour_frequency (colour, frequency)
                VALUES (%s, %s)
                ON CONFLICT (colour) DO UPDATE SET frequency = EXCLUDED.frequency;
            """, (colour, freq))

        conn.commit()
        cur.close()
        conn.close()
        print("\n[SUCCESS] Colour frequencies saved to PostgreSQL (table: colour_frequency).")

    except ImportError:
        print("\n[SKIP] psycopg2 not installed.  Install with:  pip install psycopg2-binary")
    except Exception as e:
        print(f"\n[ERROR] Could not connect to PostgreSQL: {e}")
        print("        Make sure PostgreSQL is running and the connection parameters are correct.")


save_to_postgresql(dict(colour_counts))

# 7.  BONUS — RECURSIVE SEARCH ALGORITHM

print("\n" + "=" * 65)
print("  7. RECURSIVE SEARCHING ALGORITHM (Binary Search)")
print("=" * 65)


def recursive_binary_search(arr, target, low, high):
    """
    Recursively searches for `target` in a sorted list `arr`.
    Returns the index if found, otherwise -1.
    """
    if low > high:
        return -1

    mid = (low + high) // 2

    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return recursive_binary_search(arr, target, mid + 1, high)
    else:
        return recursive_binary_search(arr, target, low, mid - 1)

sample_list = sorted(random.sample(range(1, 100), 15))
print(f"\nSorted list: {sample_list}")

demo_target = random.choice(sample_list)
result = recursive_binary_search(sample_list, demo_target, 0, len(sample_list) - 1)
print(f"Searching for {demo_target} → Found at index {result}")

miss_target = 0  
result_miss = recursive_binary_search(sample_list, miss_target, 0, len(sample_list) - 1)
print(f"Searching for {miss_target} → {'Found at index ' + str(result_miss) if result_miss != -1 else 'Not found'}")


# 8.  RANDOM 4-DIGIT BINARY NUMBER → BASE 10

print("\n" + "=" * 65)
print("  8. RANDOM 4-DIGIT BINARY NUMBER → BASE 10 CONVERSION")
print("=" * 65)


def generate_and_convert_binary(digits=4):
    """Generates a random binary number of `digits` digits and converts to base 10."""
    binary_digits = [random.choice([0, 1]) for _ in range(digits)]
    binary_str = "".join(str(d) for d in binary_digits)
    decimal_value = int(binary_str, 2)
    return binary_str, decimal_value


binary_num, decimal_num = generate_and_convert_binary()
print(f"\nGenerated binary : {binary_num}")
print(f"Base 10 value    : {decimal_num}")

# Run a few more examples
print("\nAdditional examples:")
for _ in range(4):
    b, d = generate_and_convert_binary()
    print(f"  {b}  →  {d}")

# 9.  SUM OF FIRST 50 FIBONACCI NUMBERS

print("\n" + "=" * 65)
print("  9. SUM OF THE FIRST 50 FIBONACCI NUMBERS")
print("=" * 65)


def fibonacci_sum(n):
    """Returns the sum of the first `n` Fibonacci numbers (F(1)=0, F(2)=1, ...)."""
    if n <= 0:
        return 0
    a, b = 0, 1
    total = 0
    for i in range(n):
        total += a
        a, b = b, a + b
    return total


fib_total = fibonacci_sum(50)
print(f"\nSum of first 50 Fibonacci numbers: {fib_total:,}")

print("\nFirst 50 Fibonacci numbers:")
a, b = 0, 1
fib_sequence = []
for _ in range(50):
    fib_sequence.append(a)
    a, b = b, a + b

for i in range(0, 50, 5):
    row = fib_sequence[i:i+5]
    print("  " + ", ".join(f"{x:>15,}" for x in row))

print(f"\nVerification — sum: {sum(fib_sequence):,}")

print("\n" + "=" * 65)
print("  END OF TEST")
print("=" * 65)

# I have really tried my best on this test,I hope you accept my work. I look forward to 
#  an interview with you.