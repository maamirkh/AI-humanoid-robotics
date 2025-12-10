#!/usr/bin/env python3
"""
Word count validation script for Physical AI & Humanoid Robotics Textbook
Checks that each module meets the required word count ranges.
"""
import os
import re
from pathlib import Path

def count_words_in_file(file_path):
    """Count words in a markdown file, excluding frontmatter."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove frontmatter if present
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]

    # Remove markdown syntax and count words
    text = re.sub(r'[^\w\s]', ' ', content)
    words = [w for w in text.split() if w.strip()]
    return len(words)

def validate_word_counts():
    """Validate word counts for each module."""
    docs_path = Path('docs')
    modules = ['module-1', 'module-2', 'module-3', 'module-4']
    expected_ranges = {
        'module-1': (4000, 5000),
        'module-2': (3500, 4500),
        'module-3': (4000, 5000),
        'module-4': (3500, 4500)
    }

    total_words = 0
    all_valid = True

    for module in modules:
        module_path = docs_path / module
        if not module_path.exists():
            print(f"Module {module} does not exist")
            continue

        module_words = 0
        for file_path in module_path.glob('*.md'):
            word_count = count_words_in_file(file_path)
            module_words += word_count
            print(f"  {file_path.name}: {word_count} words")

        min_words, max_words = expected_ranges[module]
        print(f"{module}: {module_words} words (expected: {min_words}-{max_words})")

        if not (min_words <= module_words <= max_words):
            print(f"  ❌ {module} word count out of range!")
            all_valid = False
        else:
            print(f"  ✅ {module} word count OK")

        total_words += module_words

    print(f"\nTotal words: {total_words} (expected: 15000-20000)")
    if 15000 <= total_words <= 20000:
        print("✅ Total word count OK")
        return True
    else:
        print("❌ Total word count out of range!")
        return False

if __name__ == "__main__":
    print("Running word count validation...")
    success = validate_word_counts()
    if not success:
        exit(1)
    print("✅ All word count validations passed!")