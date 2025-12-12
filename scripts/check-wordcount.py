#!/usr/bin/env python3
"""
Word count validation script for Physical AI & Humanoid Robotics Textbook
Checks that content meets the 15,000-20,000 word target
"""
import os
import re
import sys
from pathlib import Path

def count_words_in_file(file_path):
    """Count words in a markdown file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Remove markdown syntax and count words
        clean_content = re.sub(r'[#*\[\]`~\-_=+|{}]', ' ', content)
        words = clean_content.split()
        return len(words)

def count_words_in_directory(directory):
    """Count words in all markdown files in a directory"""
    total_words = 0
    md_files = Path(directory).rglob('*.md')
    
    for md_file in md_files:
        words = count_words_in_file(md_file)
        total_words += words
        print(f"{md_file}: {words} words")
    
    return total_words

def main():
    if len(sys.argv) != 2:
        print("Usage: python check-wordcount.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Directory {directory} does not exist")
        sys.exit(1)
    
    total_words = count_words_in_directory(directory)
    print(f"\nTotal words: {total_words}")
    
    if 15000 <= total_words <= 20000:
        print("✓ Word count is within the target range (15,000-20,000)")
        return 0
    else:
        print(f"✗ Word count is outside the target range (15,000-20,000)")
        if total_words < 15000:
            print(f"Need {15000 - total_words} more words")
        else:
            print(f"Has {total_words - 20000} words over the limit")
        return 1

if __name__ == "__main__":
    sys.exit(main())
