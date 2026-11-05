"""
Database seeder for Smart Placement Preparation Assistant.
Seeds:
- Default Student profile
- 32 Python programming questions across all 6 mandatory categories and 3 difficulty levels
- 4 Quizzes and 34 MCQ questions covering Python fundamentals, data structures, functions, and algorithms
- Initial realistic attempt & quiz history records (only when tables are initially empty)
Safe to run on every application startup without duplicating records.
"""

import json
from typing import Any, Dict, List, Tuple
from backend.database import db_session, init_db

QUESTIONS_SEED: List[Tuple[str, str, str, str, str, str, str, str]] = [
    # 1-6: Strings (6 questions)
    (
        "Reverse Words in a Sentence",
        "Given a string s containing words separated by spaces, reverse the order of words while removing leading, trailing, and multiple intermediate spaces.",
        "Strings",
        "Beginner",
        's = "  smart   placement  assistant "',
        '"assistant placement smart"',
        "Use s.split() without arguments to split by any whitespace and strip extra spaces automatically, then reverse with [::-1] and join with a single space.",
        "def reverse_words(s: str) -> str:\n    # Write your solution here\n    return ' '.join(s.split()[::-1])\n",
    ),
    (
        "Valid Anagram Check",
        "Given two strings s and t, return True if t is an anagram of s, and False otherwise. Ignore case sensitivity.",
        "Strings",
        "Beginner",
        's = "Listen", t = "Silent"',
        "True",
        "Normalize both strings to lowercase and compare character frequency counts using collections.Counter or a dictionary in O(n) time.",
        "from collections import Counter\n\ndef is_anagram(s: str, t: str) -> bool:\n    return Counter(s.lower()) == Counter(t.lower())\n",
    ),
    (
        "First Non-Repeating Character",
        "Given a string s, find the first character that does not repeat anywhere in the string and return its 0-based index. If it does not exist, return -1.",
        "Strings",
        "Beginner",
        's = "placementprep"',
        "2",
        "Build a frequency map of characters in the first pass. In the second pass, iterate with enumerate(s) and return the first index whose count is 1.",
        "def first_unique_char(s: str) -> int:\n    freq = {}\n    for ch in s:\n        freq[ch] = freq.get(ch, 0) + 1\n    for idx, ch in enumerate(s):\n        if freq[ch] == 1:\n            return idx\n    return -1\n",
    ),
    (
        "Longest Substring Without Repeating Characters",
        "Given a string s, find the length of the longest contiguous substring without any duplicate characters.",
        "Strings",
        "Intermediate",
        's = "abcabcbb"',
        "3",
        "Use a sliding window with two pointers (left, right) and a dictionary storing the last seen index of each character to achieve O(n) time complexity.",
        "def length_of_longest_substring(s: str) -> int:\n    seen = {}\n    left = max_len = 0\n    for right, ch in enumerate(s):\n        if ch in seen and seen[ch] >= left:\n            left = seen[ch] + 1\n        seen[ch] = right\n        max_len = max(max_len, right - left + 1)\n    return max_len\n",
    ),
    (
        "Run-Length String Compression",
        "Compress a string by replacing consecutive identical characters with the character followed by its repetition count. Return the original string if the compressed version is not shorter.",
        "Strings",
        "Intermediate",
        's = "aabcccccaaa"',
        '"a2b1c5a3"',
        "Track the current character and its streak count while iterating. Append parts to a list and join at the end to avoid O(n^2) string concatenation.",
        "def compress_string(s: str) -> str:\n    if not s:\n        return s\n    parts = []\n    count = 1\n    for i in range(1, len(s)):\n        if s[i] == s[i - 1]:\n            count += 1\n        else:\n            parts.append(f'{s[i - 1]}{count}')\n            count = 1\n    parts.append(f'{s[-1]}{count}')\n    compressed = ''.join(parts)\n    return compressed if len(compressed) < len(s) else s\n",
    ),
    (
        "Minimum Window Substring",
        "Given two strings s and t, return the minimum window substring of s such that every character in t (including duplicates) is included in the window. Return '' if no such window exists.",
        "Strings",
        "Advanced",
        's = "ADOBECODEBANC", t = "ABC"',
        '"BANC"',
        "Maintain frequency counts of required characters from t. Expand the right pointer until all characters are satisfied, then shrink the left pointer to minimize window size.",
        "from collections import Counter\n\ndef min_window(s: str, t: str) -> str:\n    if not s or not t:\n        return ''\n    need = Counter(t)\n    missing = len(t)\n    left = start = end = 0\n    for right, char in enumerate(s, 1):\n        if need[char] > 0:\n            missing -= 1\n        need[char] -= 1\n        if missing == 0:\n            while left < right and need[s[left]] < 0:\n                need[s[left]] += 1\n                left += 1\n            if end == 0 or right - left < end - start:\n                start, end = left, right\n            need[s[left]] += 1\n            missing += 1\n            left += 1\n    return s[start:end]\n",
    ),

    # 7-12: Lists (6 questions)
    (
        "Remove Duplicates Preserving Order",
        "Given a list of integers, remove all duplicate elements while strictly preserving the original order of first appearance.",
        "Lists",
        "Beginner",
        "nums = [4, 2, 4, 1, 2, 5, 1]",
        "[4, 2, 1, 5]",
        "In Python 3.7+, dict.fromkeys(nums) preserves insertion order in O(n) time, or you can maintain a seen set while iterating.",
        "def remove_duplicates(nums: list[int]) -> list[int]:\n    return list(dict.fromkeys(nums))\n",
    ),
    (
        "Move Zeroes In-Place",
        "Given an integer list nums, move all 0s to the end of it while maintaining the relative order of the non-zero elements.",
        "Lists",
        "Beginner",
        "nums = [0, 1, 0, 3, 12]",
        "[1, 3, 12, 0, 0]",
        "Use a slow pointer 'insert_pos' for the next non-zero element and swap whenever a non-zero value is encountered by the fast pointer.",
        "def move_zeroes(nums: list[int]) -> list[int]:\n    insert_pos = 0\n    for i in range(len(nums)):\n        if nums[i] != 0:\n            nums[insert_pos], nums[i] = nums[i], nums[insert_pos]\n            insert_pos += 1\n    return nums\n",
    ),
    (
        "Rotate List Right by K Steps",
        "Given a list nums, rotate the list to the right by k steps, where k is non-negative.",
        "Lists",
        "Intermediate",
        "nums = [1, 2, 3, 4, 5, 6, 7], k = 3",
        "[5, 6, 7, 1, 2, 3, 4]",
        "Compute k = k % len(nums) to handle k larger than list length. Slice with nums[-k:] + nums[:-k] or reverse three segments in-place.",
        "def rotate_list(nums: list[int], k: int) -> list[int]:\n    if not nums:\n        return nums\n    k %= len(nums)\n    return nums[-k:] + nums[:-k] if k else nums\n",
    ),
    (
        "Product of List Except Self",
        "Given an integer list nums, return a list answer such that answer[i] is equal to the product of all the elements of nums except nums[i], without using division.",
        "Lists",
        "Intermediate",
        "nums = [1, 2, 3, 4]",
        "[24, 12, 8, 6]",
        "Compute prefix products in a forward pass and multiply by suffix products in a backward pass in O(n) time and O(1) extra space.",
        "def product_except_self(nums: list[int]) -> list[int]:\n    n = len(nums)\n    res = [1] * n\n    prefix = 1\n    for i in range(n):\n        res[i] = prefix\n        prefix *= nums[i]\n    suffix = 1\n    for i in range(n - 1, -1, -1):\n        res[i] *= suffix\n        suffix *= nums[i]\n    return res\n",
    ),
    (
        "Merge Overlapping Intervals",
        "Given a collection of intervals where intervals[i] = [start_i, end_i], merge all overlapping intervals and return the non-overlapping intervals covering the input.",
        "Lists",
        "Intermediate",
        "intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]",
        "[[1, 6], [8, 10], [15, 18]]",
        "Sort intervals by start time. Compare each interval's start with the previous merged interval's end and update the end to max(end1, end2) when overlapping.",
        "def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:\n    if not intervals:\n        return []\n    intervals.sort(key=lambda x: x[0])\n    merged = [intervals[0]]\n    for current in intervals[1:]:\n        if current[0] <= merged[-1][1]:\n            merged[-1][1] = max(merged[-1][1], current[1])\n        else:\n            merged.append(current)\n    return merged\n",
    ),
    (
        "Maximum Subarray Sum (Kadane's Algorithm)",
        "Given an integer list nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.",
        "Lists",
        "Advanced",
        "nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]",
        "6",
        "Maintain current_sum = max(num, current_sum + num) and global_max = max(global_max, current_sum) at each element in a single O(n) scan.",
        "def max_subarray(nums: list[int]) -> int:\n    curr = best = nums[0]\n    for num in nums[1:]:\n        curr = max(num, curr + num)\n        best = max(best, curr)\n    return best\n",
    ),

    # 13-17: Dictionaries (5 questions)
    (
        "Two Sum Using Hash Map",
        "Given a list of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "Dictionaries",
        "Beginner",
        "nums = [2, 7, 11, 15], target = 9",
        "[0, 1]",
        "Store each visited number and its index in a dictionary. For each element x, check if (target - x) already exists in the dictionary in O(1) time.",
        "def two_sum(nums: list[int], target: int) -> list[int]:\n    seen = {}\n    for idx, val in enumerate(nums):\n        diff = target - val\n        if diff in seen:\n            return [seen[diff], idx]\n        seen[val] = idx\n    return []\n",
    ),
    (
        "Word Frequency Counter",
        "Given a paragraph of text, return a dictionary mapping each lowercase word (stripped of punctuation) to its frequency count, sorted by frequency descending.",
        "Dictionaries",
        "Beginner",
        'text = "Python is fast, and Python is readable!"',
        "{'python': 2, 'is': 2, 'fast': 1, 'and': 1, 'readable': 1}",
        "Extract alphanumeric words using re.findall(r'[a-z0-9]+', text.lower()) and count occurrences with a dictionary or Counter.",
        "import re\n\ndef word_frequencies(text: str) -> dict[str, int]:\n    words = re.findall(r'[a-z0-9]+', text.lower())\n    counts = {}\n    for w in words:\n        counts[w] = counts.get(w, 0) + 1\n    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))\n",
    ),
    (
        "Group Anagrams Together",
        "Given a list of strings strs, group the anagrams together into sublists. You can return the answer in any order.",
        "Dictionaries",
        "Intermediate",
        'strs = ["eat", "tea", "tan", "ate", "nat", "bat"]',
        '[["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]',
        "Use tuple(sorted(word)) as the dictionary key and append each word to its corresponding bucket in collections.defaultdict(list).",
        "from collections import defaultdict\n\ndef group_anagrams(strs: list[str]) -> list[list[str]]:\n    groups = defaultdict(list)\n    for word in strs:\n        groups[tuple(sorted(word))].append(word)\n    return list(groups.values())\n",
    ),
    (
        "Invert Dictionary with Duplicate Values",
        "Given a dictionary mapping student names to their department, invert it so each department maps to a sorted list of students belonging to it.",
        "Dictionaries",
        "Intermediate",
        "mapping = {'Aarav': 'CSE', 'Diya': 'ECE', 'Rohan': 'CSE'}",
        "{'CSE': ['Aarav', 'Rohan'], 'ECE': ['Diya']}",
        "Iterate over mapping.items(), append keys to a list for each value, and sort each resulting list.",
        "def invert_department_map(mapping: dict[str, str]) -> dict[str, list[str]]:\n    inverted: dict[str, list[str]] = {}\n    for student, dept in mapping.items():\n        inverted.setdefault(dept, []).append(student)\n    for dept in inverted:\n        inverted[dept].sort()\n    return inverted\n",
    ),
    (
        "Subarray Sum Equals K",
        "Given a list of integers nums and an integer k, return the total number of contiguous subarrays whose sum equals to k.",
        "Dictionaries",
        "Advanced",
        "nums = [1, 2, 3], k = 3",
        "2",
        "Track running prefix_sum and store the frequency of each prefix_sum in a dictionary initialized with {0: 1}. Add freq.get(prefix_sum - k, 0) at each step.",
        "def subarray_sum(nums: list[int], k: int) -> int:\n    prefix_counts = {0: 1}\n    curr_sum = count = 0\n    for num in nums:\n        curr_sum += num\n        count += prefix_counts.get(curr_sum - k, 0)\n        prefix_counts[curr_sum] = prefix_counts.get(curr_sum, 0) + 1\n    return count\n",
    ),

    # 18-22: Functions (5 questions)
    (
        "Flexible Argument Aggregator (*args & **kwargs)",
        "Write a function summarize_scores(*scores, bonus=0, **metadata) that returns a dictionary with the count, average (with bonus added to each score), and metadata.",
        "Functions",
        "Beginner",
        "summarize_scores(80, 90, 100, bonus=5, exam='Placement Mock')",
        "{'count': 3, 'average': 95.0, 'exam': 'Placement Mock'}",
        "*scores collects positional arguments as a tuple, bonus is a keyword-only default argument, and **metadata collects arbitrary keyword arguments as a dict.",
        "def summarize_scores(*scores: float, bonus: float = 0, **metadata) -> dict:\n    if not scores:\n        return {'count': 0, 'average': 0.0, **metadata}\n    adjusted = [s + bonus for s in scores]\n    avg = round(sum(adjusted) / len(adjusted), 2)\n    return {'count': len(scores), 'average': avg, **metadata}\n",
    ),
    (
        "Recursive Factorial and Power Function",
        "Implement a recursive function power_mod(base, exp, mod) that computes (base^exp) % mod in O(log exp) time using binary exponentiation.",
        "Functions",
        "Beginner",
        "base = 3, exp = 5, mod = 100",
        "43",
        "Use divide-and-conquer recursion: if exp is even, square power_mod(base, exp // 2, mod); if odd, multiply by base one extra time.",
        "def power_mod(base: int, exp: int, mod: int) -> int:\n    if exp == 0:\n        return 1 % mod\n    half = power_mod(base, exp // 2, mod)\n    res = (half * half) % mod\n    return (res * base) % mod if exp % 2 == 1 else res\n",
    ),
    (
        "Memoization Decorator From Scratch",
        "Implement a custom @memoize decorator that caches the return values of a pure function based on its positional arguments.",
        "Functions",
        "Intermediate",
        "fib(10) decorated with @memoize",
        "55",
        "Use a closure dictionary cache = {} inside the decorator and functools.wraps(fn) to preserve function metadata.",
        "from functools import wraps\n\ndef memoize(fn):\n    cache = {}\n    @wraps(fn)\n    def wrapper(*args):\n        if args not in cache:\n            cache[args] = fn(*args)\n        return cache[args]\n    return wrapper\n",
    ),
    (
        "Flatten Arbitrarily Nested List Using Generators",
        "Write a recursive generator function flatten(nested) that yields elements from an arbitrarily nested list of integers.",
        "Functions",
        "Intermediate",
        "nested = [1, [2, [3, 4], 5], [6]]",
        "[1, 2, 3, 4, 5, 6]",
        "Check isinstance(item, list). If true, use 'yield from flatten(item)'; otherwise 'yield item'.",
        "def flatten(nested: list):\n    for item in nested:\n        if isinstance(item, list):\n            yield from flatten(item)\n        else:\n            yield item\n",
    ),
    (
        "Function Composition Pipeline",
        "Write a higher-order function compose(*functions) that accepts multiple single-argument functions and returns a single function applying them from right to left.",
        "Functions",
        "Advanced",
        "f = compose(lambda x: x * 2, lambda x: x + 3); f(4)",
        "14",
        "Apply functions in reversed(functions) order using functools.reduce or a clean loop inside the inner closure.",
        "from functools import reduce\n\ndef compose(*functions):\n    def inner(arg):\n        return reduce(lambda acc, fn: fn(acc), reversed(functions), arg)\n    return inner\n",
    ),

    # 23-27: Number problems (5 questions)
    (
        "Palindrome Integer Check Without String Conversion",
        "Determine whether an integer x is a palindrome without converting the integer to a string. Negative numbers are not palindromes.",
        "Number problems",
        "Beginner",
        "x = 12321",
        "True",
        "Reverse the digits mathematically using modulo (% 10) and integer division (// 10), then compare the reversed integer with the original.",
        "def is_palindrome_number(x: int) -> bool:\n    if x < 0:\n        return False\n    original, rev = x, 0\n    while x > 0:\n        rev = rev * 10 + (x % 10)\n        x //= 10\n    return original == rev\n",
    ),
    (
        "Armstrong (Narcissistic) Number Validator",
        "Check if a positive integer n of d digits equals the sum of its digits each raised to the power d.",
        "Number problems",
        "Beginner",
        "n = 153",
        "True",
        "153 has 3 digits and 1^3 + 5^3 + 3^3 = 1 + 125 + 27 = 153. Extract digits and compute sum(digit ** d).",
        "def is_armstrong(n: int) -> bool:\n    if n < 0:\n        return False\n    digits = [int(d) for d in str(n)]\n    power = len(digits)\n    return sum(d ** power for d in digits) == n\n",
    ),
    (
        "Greatest Common Divisor & Least Common Multiple",
        "Given two positive integers a and b, return a tuple (gcd, lcm) computed using Euclid's algorithm.",
        "Number problems",
        "Intermediate",
        "a = 24, b = 36",
        "(12, 72)",
        "Euclid's algorithm repeatedly sets a, b = b, a % b until b == 0. Then LCM(a, b) = (a * b) // GCD(a, b).",
        "def gcd_and_lcm(a: int, b: int) -> tuple[int, int]:\n    x, y = a, b\n    while y:\n        x, y = y, x % y\n    lcm = (a * b) // x if x else 0\n    return (x, lcm)\n",
    ),
    (
        "Count Primes Up to N (Sieve of Eratosthenes)",
        "Given an integer n, return all prime numbers less than or equal to n using the Sieve of Eratosthenes.",
        "Number problems",
        "Intermediate",
        "n = 20",
        "[2, 3, 5, 7, 11, 13, 17, 19]",
        "Create a boolean array is_prime of size n + 1. For each p from 2 to int(n**0.5), mark multiples starting from p*p as False.",
        "def sieve_primes(n: int) -> list[int]:\n    if n < 2:\n        return []\n    is_prime = [True] * (n + 1)\n    is_prime[0] = is_prime[1] = False\n    for p in range(2, int(n ** 0.5) + 1):\n        if is_prime[p]:\n            for multiple in range(p * p, n + 1, p):\n                is_prime[multiple] = False\n    return [i for i, prime in enumerate(is_prime) if prime]\n",
    ),
    (
        "Count Trailing Zeroes in N Factorial",
        "Given an integer n, return the number of trailing zeroes in n! (n factorial) in O(log_5 n) time without computing the factorial itself.",
        "Number problems",
        "Advanced",
        "n = 25",
        "6",
        "Trailing zeroes are produced by factors of 10 (2 * 5). Count how many multiples of 5, 25, 125, ... are <= n by repeatedly dividing n by 5.",
        "def trailing_zeroes(n: int) -> int:\n    count = 0\n    while n >= 5:\n        n //= 5\n        count += n\n    return count\n",
    ),

    # 28-32: Basic algorithms (5 questions)
    (
        "Iterative Binary Search on Sorted List",
        "Given a sorted list of integers nums and a target value, return the 0-based index if the target is found, or -1 otherwise, in O(log n) time.",
        "Basic algorithms",
        "Beginner",
        "nums = [-4, -1, 0, 3, 9, 12], target = 9",
        "4",
        "Maintain low = 0 and high = len(nums) - 1. Compare nums[mid] with target and narrow the search half each iteration.",
        "def binary_search(nums: list[int], target: int) -> int:\n    low, high = 0, len(nums) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if nums[mid] == target:\n            return mid\n        elif nums[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1\n",
    ),
    (
        "Valid Balanced Parentheses (Stack)",
        "Given a string s containing only '(', ')', '{', '}', '[' and ']', determine if the input string has valid, properly nested brackets.",
        "Basic algorithms",
        "Beginner",
        's = "{[()()]}"',
        "True",
        "Push opening brackets onto a stack. When encountering a closing bracket, check that the stack is non-empty and its top matches the corresponding opening bracket.",
        "def is_valid_parentheses(s: str) -> bool:\n    stack = []\n    pairs = {')': '(', '}': '{', ']': '['}\n    for ch in s:\n        if ch in pairs:\n            if not stack or stack.pop() != pairs[ch]:\n                return False\n        else:\n            stack.append(ch)\n    return len(stack) == 0\n",
    ),
    (
        "Merge Sort Implementation",
        "Implement the divide-and-conquer Merge Sort algorithm to sort a list of integers in ascending order in O(n log n) worst-case time.",
        "Basic algorithms",
        "Intermediate",
        "nums = [38, 27, 43, 3, 9, 82, 10]",
        "[3, 9, 10, 27, 38, 43, 82]",
        "Recursively split the list into halves until len <= 1, then merge two sorted halves using two pointers.",
        "def merge_sort(nums: list[int]) -> list[int]:\n    if len(nums) <= 1:\n        return nums\n    mid = len(nums) // 2\n    left = merge_sort(nums[:mid])\n    right = merge_sort(nums[mid:])\n    merged = []\n    i = j = 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            merged.append(left[i]); i += 1\n        else:\n            merged.append(right[j]); j += 1\n    merged.extend(left[i:])\n    merged.extend(right[j:])\n    return merged\n",
    ),
    (
        "Climbing Stairs (Dynamic Programming)",
        "You are climbing a staircase with n steps. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
        "Basic algorithms",
        "Intermediate",
        "n = 5",
        "8",
        "The number of ways to reach step n is ways(n-1) + ways(n-2), which forms the Fibonacci sequence computable in O(n) time and O(1) space.",
        "def climb_stairs(n: int) -> int:\n    if n <= 2:\n        return n\n    prev2, prev1 = 1, 2\n    for _ in range(3, n + 1):\n        prev2, prev1 = prev1, prev2 + prev1\n    return prev1\n",
    ),
    (
        "Search in Rotated Sorted Array",
        "Given a sorted array of distinct integers nums that has been rotated at an unknown pivot, find the index of target in O(log n) time, or return -1.",
        "Basic algorithms",
        "Advanced",
        "nums = [4, 5, 6, 7, 0, 1, 2], target = 0",
        "4",
        "At any midpoint mid, at least one half (low..mid or mid..high) is strictly sorted. Check if target lies within the sorted half to decide which half to discard.",
        "def search_rotated(nums: list[int], target: int) -> int:\n    low, high = 0, len(nums) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if nums[mid] == target:\n            return mid\n        if nums[low] <= nums[mid]:\n            if nums[low] <= target < nums[mid]:\n                high = mid - 1\n            else:\n                low = mid + 1\n        else:\n            if nums[mid] < target <= nums[high]:\n                low = mid + 1\n            else:\n                high = mid - 1\n    return -1\n",
    ),
]


QUIZZES_SEED: List[Tuple[str, str, str, str, int, int]] = [
    (
        "Python Core & Strings Mastery",
        "Test your grasp of Python syntax, string manipulation, slicing, memory semantics, and core built-in types.",
        "Strings",
        "Beginner",
        10,
        10,
    ),
    (
        "Lists, Dictionaries & Data Structures",
        "Evaluate your knowledge of Python lists, tuples, sets, dictionaries, hashing, and time complexities.",
        "Lists",
        "Intermediate",
        12,
        10,
    ),
    (
        "Functions, Scope & Algorithmic Thinking",
        "Assess your understanding of closures, decorators, generators, recursion, sorting, and searching algorithms.",
        "Functions",
        "Intermediate",
        15,
        10,
    ),
    (
        "Comprehensive Placement Readiness Mock",
        "Full-spectrum placement mock drawing randomized questions across all Python & DSA topics.",
        "Comprehensive",
        "Mixed",
        15,
        12,
    ),
]


# 34 MCQs mapped to quiz_id (1, 2, or 3; Quiz 4 pulls from the entire 34-question pool!)
QUIZ_QUESTIONS_SEED: List[Tuple[int, str, str, str, str, str, str, str, str, str]] = [
    # Quiz 1: Python Core & Strings (11 MCQs)
    (
        1,
        "What is the output of `'placement'[::-2]` in Python?",
        "Strings",
        "Beginner",
        "'tnmclp'",
        "'tneca'",
        "'plcmn'",
        "'tnmcl'",
        "B",
        "Slicing with `[::-2]` starts from the end ('t') and steps backward by 2 indices: 't', 'n', 'e', 'c', 'p' -> wait: indices 8('t'), 6('e'), 4('e'), 2('a'), 0('p') -> wait let's trace 'p'(0)'l'(1)'a'(2)'c'(3)'e'(4)'m'(5)'e'(6)'n'(7)'t'(8): 8='t', 6='e', 4='e', 2='a', 0='p'. Let's make the string `'python'[::-1]` so it is crystal clear!",
    ),
    (
        1,
        "Which of the following is true about Python strings (`str`)?",
        "Strings",
        "Beginner",
        "Strings are mutable sequences of characters",
        "Strings are immutable sequences of Unicode code points",
        "Strings can be modified in-place using index assignment",
        "Strings cannot be used as dictionary keys",
        "B",
        "In Python 3, `str` objects are immutable sequences of Unicode characters and are hashable, making them valid dictionary keys.",
    ),
    (
        1,
        "What does `'  hello   world  '.split()` return when called without arguments?",
        "Strings",
        "Beginner",
        "['', '', 'hello', '', '', 'world', '', '']",
        "['hello', 'world']",
        "['hello   world']",
        "('hello', 'world')",
        "B",
        "Calling `str.split()` with `sep=None` splits on runs of consecutive whitespace and automatically strips leading and trailing whitespace.",
    ),
    (
        1,
        "What is the time complexity of concatenating `n` strings of length 1 using `s += ch` vs `''.join(chars)`?",
        "Strings",
        "Intermediate",
        "Both are guaranteed O(1)",
        "join() guarantees O(n) memory allocation while repeated concatenation can degrade to O(n^2)",
        "join() is O(n^2) and += is O(log n)",
        "join() only works on tuples",
        "B",
        "`''.join(iterable)` pre-calculates total length and allocates memory once in O(n) time, which is the recommended Pythonic idiom.",
    ),
    (
        1,
        "What is the result of `'abc'.find('z')` compared to `'abc'.index('z')`?",
        "Strings",
        "Beginner",
        "Both return -1",
        "find() returns -1 whereas index() raises ValueError",
        "find() raises KeyError whereas index() returns None",
        "Both raise IndexError",
        "B",
        "`str.find(sub)` returns `-1` when the substring is not found, whereas `str.index(sub)` raises a `ValueError`.",
    ),
    (
        1,
        "What is the output of `bool('False')` in Python?",
        "Strings",
        "Beginner",
        "False",
        "True",
        "None",
        "Raises TypeError",
        "B",
        "Any non-empty string in Python is truthy (`bool('False') == True`). Only the empty string `''` evaluates to `False`.",
    ),
    (
        1,
        "Which string method checks if all characters in a non-empty string are alphanumeric?",
        "Strings",
        "Beginner",
        "str.isalpha()",
        "str.isdigit()",
        "str.isalnum()",
        "str.isidentifier()",
        "C",
        "`str.isalnum()` returns `True` if all characters are either alphabetic letters or numeric digits and the string is non-empty.",
    ),
    (
        1,
        "What does `f'{3.14159:.2f}'` evaluate to?",
        "Strings",
        "Beginner",
        "'3.14'",
        "'3.15'",
        "'3.141'",
        "3.14",
        "A",
        "The format specifier `:.2f` formats a floating-point number to 2 decimal places as a string (`'3.14'`).",
    ),
    (
        1,
        "What is the output of `'banana'.replace('a', 'o', 2)`?",
        "Strings",
        "Intermediate",
        "'bonono'",
        "'bonona'",
        "'banono'",
        "'banana'",
        "B",
        "The third argument `count=2` limits replacement to the first 2 occurrences of `'a'`, producing `'bonona'`.",
    ),
    (
        1,
        "What does `ord('A')` return in Python?",
        "Number problems",
        "Beginner",
        "65",
        "97",
        "48",
        "64",
        "A",
        "`ord('A')` returns the Unicode code point (ASCII value) for uppercase `'A'`, which is 65 (`ord('a')` is 97).",
    ),
    (
        1,
        "What is the output of `-7 // 2` and `-7 % 2` in Python?",
        "Number problems",
        "Intermediate",
        "-3 and -1",
        "-4 and 1",
        "-3 and 1",
        "-4 and -1",
        "B",
        "Python floor division `//` rounds toward negative infinity (`-7 // 2 == -4`), and `-7 == (-4 * 2) + 1`, so `-7 % 2 == 1`.",
    ),

    # Quiz 2: Lists, Dictionaries & Data Structures (12 MCQs)
    (
        2,
        "What is the average time complexity of checking `x in my_collection` when `my_collection` is a `set` or `dict` versus a `list`?",
        "Dictionaries",
        "Beginner",
        "O(1) for set/dict and O(n) for list",
        "O(log n) for set/dict and O(1) for list",
        "O(n) for both",
        "O(1) for both",
        "A",
        "Sets and dictionaries use hash tables providing O(1) average lookup, whereas lists require a linear O(n) scan.",
    ),
    (
        2,
        "Which of the following objects CANNOT be used as a key in a Python `dict`?",
        "Dictionaries",
        "Beginner",
        "(1, 2, 3)",
        "frozenset([1, 2])",
        "(1, [2, 3])",
        "'interview'",
        "C",
        "A tuple containing a mutable `list` `(1, [2, 3])` is unhashable and raises `TypeError: unhashable type: 'list'`.",
    ),
    (
        2,
        "What is the difference between `list.sort()` and `sorted(list)`?",
        "Lists",
        "Beginner",
        "list.sort() sorts in-place and returns None; sorted() returns a new sorted list",
        "sorted() sorts in-place and returns None; list.sort() returns a new list",
        "list.sort() works on any iterable including tuples and dictionaries",
        "There is no difference",
        "A",
        "`list.sort()` mutates the list in-place and returns `None`. `sorted(iterable)` accepts any iterable and returns a new sorted list.",
    ),
    (
        2,
        "What happens when you execute `matrix = [[0] * 3] * 3` and then set `matrix[0][0] = 9`?",
        "Lists",
        "Intermediate",
        "Only matrix[0][0] becomes 9",
        "matrix[0][0], matrix[1][0], and matrix[2][0] all become 9",
        "All 9 elements become 9",
        "IndexError is raised",
        "B",
        "Multiplying a outer list `[...] * 3` creates 3 references to the exact same inner list object. Use `[[0]*3 for _ in range(3)]` instead.",
    ),
    (
        2,
        "What does `my_dict.get('score', 0)` return if `'score'` is not present in `my_dict`?",
        "Dictionaries",
        "Beginner",
        "Raises KeyError",
        "None",
        "0",
        "False",
        "C",
        "`dict.get(key, default)` safely returns `default` (`0`) without raising a `KeyError` or modifying the dictionary.",
    ),
    (
        2,
        "Which module and class in the Python standard library provides $O(1)$ time complexity for both `append()` and `popleft()`?",
        "Lists",
        "Intermediate",
        "collections.deque",
        "queue.LifoQueue",
        "heapq",
        "array.array",
        "A",
        "`collections.deque` (double-ended queue) supports $O(1)$ appends and pops from both ends, unlike `list.pop(0)` which takes $O(n)$.",
    ),
    (
        2,
        "What is the output of `[x*x for x in range(6) if x % 2 == 1]`?",
        "Lists",
        "Beginner",
        "[1, 9, 25]",
        "[0, 4, 16]",
        "[1, 3, 5]",
        "[0, 1, 4, 9, 16, 25]",
        "A",
        "Odd numbers in `range(6)` are `1, 3, 5`. Squaring them yields `[1, 9, 25]`.",
    ),
    (
        2,
        "Starting from Python 3.7+, what guarantee does the built-in `dict` type provide regarding key order?",
        "Dictionaries",
        "Intermediate",
        "Keys are automatically sorted alphabetically",
        "Keys are stored in random hash order",
        "Keys preserve their insertion order",
        "Keys are ordered by their value size",
        "C",
        "Preserving insertion order became a language specification guarantee for `dict` in Python 3.7.",
    ),
    (
        2,
        "What does `{x: x**2 for x in (2, 4, 6)}` create?",
        "Dictionaries",
        "Beginner",
        "A set containing {4, 16, 36}",
        "A dictionary {2: 4, 4: 16, 6: 36}",
        "A generator object",
        "A list of tuples",
        "B",
        "The `{key: value for ...}` syntax is a dictionary comprehension producing `{2: 4, 4: 16, 6: 36}`.",
    ),
    (
        2,
        "What is the output of `a = [1, 2, 3]; b = a; b.append(4); print(len(a))`?",
        "Lists",
        "Beginner",
        "3",
        "4",
        "Raises AttributeError",
        "0",
        "B",
        "`b = a` binds `b` to the same list object referenced by `a`. Mutating `b` mutates the shared list, so `len(a)` is 4.",
    ),
    (
        2,
        "Which expression merges two dictionaries `d1` and `d2` into a new dictionary in Python 3.9+?",
        "Dictionaries",
        "Intermediate",
        "d1 + d2",
        "d1 | d2",
        "d1 & d2",
        "d1.append(d2)",
        "B",
        "PEP 584 (Python 3.9) introduced the union operator `d1 | d2` (and `|=`) for merging dictionaries.",
    ),

    # Quiz 3: Functions, Scope & Algorithmic Thinking (11 MCQs)
    (
        3,
        "Why is `def add_item(item, bucket=[]): bucket.append(item); return bucket` considered a classic Python pitfall?",
        "Functions",
        "Intermediate",
        "Default mutable arguments are evaluated only once at function definition time and shared across calls",
        "Lists cannot be passed as default arguments in Python",
        "It causes a SyntaxError at runtime",
        "It creates a new list on every call and wastes memory",
        "A",
        "Default argument values are created once when `def` executes. Mutating `bucket` persists across subsequent function calls that omit `bucket`.",
    ),
    (
        3,
        "What does a Python function return if it contains the `yield` keyword?",
        "Functions",
        "Beginner",
        "A tuple of all yielded values",
        "A generator iterator object",
        "A list comprehension",
        "None",
        "B",
        "Any function containing `yield` becomes a generator function; calling it returns a lazy generator object.",
    ),
    (
        3,
        "What does the LEGB rule in Python stand for?",
        "Functions",
        "Beginner",
        "Local, Enclosing, Global, Built-in scope resolution order",
        "Linear, Exponential, Graph, Binary search",
        "Loop, Exception, Generator, Branch",
        "Lambda, Expression, Global, Block",
        "A",
        "Python resolves variable names by searching Local -> Enclosing (closure) -> Global -> Built-in namespaces.",
    ),
    (
        3,
        "What is the worst-case and best-case time complexity of Python's built-in `Timsort` (`list.sort()`)?",
        "Basic algorithms",
        "Intermediate",
        "Worst: O(n^2), Best: O(n log n)",
        "Worst: O(n log n), Best: O(n)",
        "Worst: O(n), Best: O(1)",
        "Worst: O(n log n), Best: O(n log n)",
        "B",
        "Timsort is a hybrid stable sort (merge sort + insertion sort) that detects natural runs, achieving O(n) best case on nearly sorted data and O(n log n) worst case.",
    ),
    (
        3,
        "What is the time complexity of Binary Search on a sorted array of `n` elements?",
        "Basic algorithms",
        "Beginner",
        "O(n)",
        "O(n log n)",
        "O(log n)",
        "O(1)",
        "C",
        "Binary search halves the search interval on every comparison, requiring at most $\\lfloor \\log_2(n) \\rfloor + 1$ steps.",
    ),
    (
        3,
        "Which decorator from `functools` preserves the wrapped function's `__name__` and `__doc__` metadata?",
        "Functions",
        "Intermediate",
        "@functools.wraps",
        "@functools.lru_cache",
        "@functools.partial",
        "@functools.reduce",
        "A",
        "`@functools.wraps(fn)` copies `__name__`, `__doc__`, `__annotations__`, and `__wrapped__` to the wrapper function.",
    ),
    (
        3,
        "What is the auxiliary space complexity of a naive recursive Fibonacci function `fib(n)` without memoization, and its time complexity?",
        "Basic algorithms",
        "Intermediate",
        "Time: O(n), Space: O(1)",
        "Time: O(2^n), Space: O(n) call stack depth",
        "Time: O(log n), Space: O(log n)",
        "Time: O(n^2), Space: O(2^n)",
        "B",
        "Naive recursive `fib(n)` branches twice per call ($O(2^n)$ time), while the maximum recursion tree depth at any moment is $O(n)$.",
    ),
    (
        3,
        "In a function signature `def configure(host, /, port=8000, *, debug=False):`, what do `/` and `*` enforce?",
        "Functions",
        "Advanced",
        "host is positional-only and debug is keyword-only",
        "host is keyword-only and debug is positional-only",
        "Both host and debug are optional",
        "They unpack tuples and dictionaries",
        "A",
        "Parameters before `/` are positional-only, and parameters after `*` are keyword-only.",
    ),
    (
        3,
        "Which data structure is used internally to manage function calls and recursion?",
        "Basic algorithms",
        "Beginner",
        "Queue (FIFO)",
        "Call Stack (LIFO)",
        "Min-Heap",
        "Hash Table",
        "B",
        "Active subroutine activation records (stack frames) are pushed and popped in Last-In, First-Out (LIFO) order on the call stack.",
    ),
    (
        3,
        "Using Euclid's algorithm, how many recursive steps are needed to compute `gcd(48, 18)`?",
        "Number problems",
        "Intermediate",
        "1 step",
        "3 steps: (48, 18) -> (18, 12) -> (12, 6) -> (6, 0)",
        "6 steps",
        "18 steps",
        "B",
        "`48 % 18 = 12`, `18 % 12 = 6`, `12 % 6 = 0`, returning `6` in 3 modulo operations.",
    ),
    (
        3,
        "What does `all([])` and `any([])` return in Python for an empty list?",
        "Functions",
        "Advanced",
        "all([]) is True, any([]) is False",
        "all([]) is False, any([]) is True",
        "Both return False",
        "Both return True",
        "A",
        "`all([])` is vacuously `True` (no falsy element exists), while `any([])` is `False` (no truthy element exists).",
    ),
]

# Fix the first MCQ in QUIZ_QUESTIONS_SEED so the explanation and answer are 100% clean
QUIZ_QUESTIONS_SEED[0] = (
    1,
    "What is the output of `'python'[::-1]` in Python?",
    "Strings",
    "Beginner",
    "'nohtyp'",
    "'python'",
    "'pnh'",
    "'nyto'",
    "A",
    "Slicing with step `-1` (`[::-1]`) traverses the string from right to left, producing the reversed string `'nohtyp'`.",
)


def seed_database() -> None:
    """Initialize tables and idempotently seed student, questions, quizzes, and sample attempts."""
    init_db()

    with db_session() as conn:
        # 1. Seed default student profile (editable by user via UI)
        conn.execute(
            """
            INSERT OR IGNORE INTO students (id, name, email, branch, graduation_year, target_role)
            VALUES (1, 'Student', 'student@university.edu', 'Computer Science', 2026, 'Software Development Engineer')
            """
        )

        # 2. Seed coding questions (idempotent via UNIQUE title)
        for q in QUESTIONS_SEED:
            conn.execute(
                """
                INSERT OR IGNORE INTO questions
                (title, description, category, difficulty, sample_input, expected_output, explanation, starter_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                q,
            )

        # 3. Seed quizzes (idempotent via UNIQUE title)
        for qz in QUIZZES_SEED:
            conn.execute(
                """
                INSERT OR IGNORE INTO quizzes
                (title, description, category, difficulty, duration_minutes, total_questions)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                qz,
            )

        # 4. Seed quiz MCQ questions (idempotent via UNIQUE question_text)
        for qq in QUIZ_QUESTIONS_SEED:
            conn.execute(
                """
                INSERT OR IGNORE INTO quiz_questions
                (quiz_id, question_text, category, difficulty, option_a, option_b, option_c, option_d, correct_option, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                qq,
            )

        # 5. Seed initial sample attempts ONLY if attempts table is completely empty
        existing_attempts = conn.execute("SELECT COUNT(*) AS cnt FROM attempts").fetchone()["cnt"]
        if existing_attempts == 0:
            initial_attempts = [
                (
                    1,
                    1,
                    "def reverse_words(s: str) -> str:\n    return ' '.join(s.split()[::-1])",
                    "Completed",
                    "Used split() without args to handle multiple spaces cleanly.",
                    8,
                ),
                (
                    1,
                    7,
                    "def remove_duplicates(nums: list[int]) -> list[int]:\n    return list(dict.fromkeys(nums))",
                    "Completed",
                    "Preserved insertion order in O(n) using dict.fromkeys.",
                    6,
                ),
                (
                    1,
                    13,
                    "def two_sum(nums: list[int], target: int) -> list[int]:\n    seen = {}\n    for i, x in enumerate(nums):\n        if target - x in seen:\n            return [seen[target - x], i]\n        seen[x] = i\n    return []",
                    "Completed",
                    "Single-pass hash map lookup in O(n) time.",
                    10,
                ),
                (
                    1,
                    18,
                    "def summarize_scores(*scores, bonus=0, **metadata):\n    adjusted = [s + bonus for s in scores]\n    return {'count': len(scores), 'average': sum(adjusted)/len(adjusted), **metadata}",
                    "Completed",
                    "Practiced *args and **kwargs unpacking.",
                    12,
                ),
                (
                    1,
                    28,
                    "def binary_search(nums: list[int], target: int) -> int:\n    low, high = 0, len(nums) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if nums[mid] == target:\n            return mid\n        elif nums[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1",
                    "Completed",
                    "Iterative binary search verified with edge cases.",
                    9,
                ),
                (
                    1,
                    4,
                    "def length_of_longest_substring(s: str) -> int:\n    # Working on sliding window boundary condition\n    pass",
                    "Attempted",
                    "Reviewing sliding window left pointer jump condition.",
                    15,
                ),
            ]
            conn.executemany(
                """
                INSERT INTO attempts (student_id, question_id, submitted_code, status, notes, time_taken_minutes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                initial_attempts,
            )

        # 6. Seed initial sample quiz attempts ONLY if quiz_attempts table is completely empty
        existing_quiz_attempts = conn.execute("SELECT COUNT(*) AS cnt FROM quiz_attempts").fetchone()["cnt"]
        if existing_quiz_attempts == 0:
            q1_rows = conn.execute(
                "SELECT id, correct_option FROM quiz_questions WHERE quiz_id = 1 ORDER BY id LIMIT 8"
            ).fetchall()
            if q1_rows:
                ans1 = {}
                score1 = 0
                for idx, r in enumerate(q1_rows):
                    if idx < 7:
                        ans1[str(r["id"])] = r["correct_option"]
                        score1 += 1
                    else:
                        ans1[str(r["id"])] = "D" if r["correct_option"] != "D" else "A"
                pct1 = round((score1 / len(q1_rows)) * 100.0, 2)
                conn.execute(
                    """
                    INSERT INTO quiz_attempts (student_id, quiz_id, score, total_questions, percentage, time_taken_seconds, answers_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (1, 1, score1, len(q1_rows), pct1, 265, json.dumps(ans1)),
                )

            q2_rows = conn.execute(
                "SELECT id, correct_option FROM quiz_questions WHERE quiz_id = 2 ORDER BY id LIMIT 8"
            ).fetchall()
            if q2_rows:
                ans2 = {}
                score2 = 0
                for idx, r in enumerate(q2_rows):
                    if idx < 6:
                        ans2[str(r["id"])] = r["correct_option"]
                        score2 += 1
                    else:
                        ans2[str(r["id"])] = "C" if r["correct_option"] != "C" else "A"
                pct2 = round((score2 / len(q2_rows)) * 100.0, 2)
                conn.execute(
                    """
                    INSERT INTO quiz_attempts (student_id, quiz_id, score, total_questions, percentage, time_taken_seconds, answers_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (1, 2, score2, len(q2_rows), pct2, 310, json.dumps(ans2)),
                )

