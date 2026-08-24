import csv
from collections import defaultdict
import os


def load_vocab(filename='vocab.csv'):
    """
    Reads from a CSV file (default 'vocab.csv') and constructs a dictionary
    mapping each lesson to a list of Strong's numbers.
    
    Args:
        filename (str): Path to the vocab CSV file.
        
    Returns:
        dict: Dictionary where keys are lesson names (str) and values are lists of Strong's numbers (list of str).
    """
    if not os.path.isabs(filename) and not os.path.exists(filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)
        if os.path.exists(file_path):
            filename = file_path

    vocab = defaultdict(list)
    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lesson = row.get('Lesson', '').strip()
            strong_num = row.get("Strong's Number", '').strip()
            if lesson and strong_num:
                vocab[lesson].append(strong_num)

    return dict(vocab)


# Alias for load_vocab
read_vocab = load_vocab


def upto(lesson_num, reading_num=0, filename='vocab.csv'):
    """
    Returns a set of Strong's numbers for all lessons <= lesson_num
    and all readings <= reading_num.
    
    Args:
        lesson_num (int): Maximum lesson number (inclusive).
        reading_num (int): Maximum reading number (inclusive).
        filename (str): Path to vocab CSV file.
        
    Returns:
        set: Set of Strong's numbers (str).
    """
    if not os.path.isabs(filename) and not os.path.exists(filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)
        if os.path.exists(file_path):
            filename = file_path

    res = set()
    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry_type = row.get('Lesson', '').strip()
            strong_num = row.get("Strong's Number", '').strip()
            if not strong_num or not entry_type:
                continue

            if entry_type.startswith('Lesson #'):
                # Extract numbers from lesson entry string like "Lesson #03", "Lesson #24/25", "Lesson #41-44"
                nums = [int(n) for n in entry_type.replace('Lesson #', '').replace('/', ' ').replace('-', ' ').split()]
                if nums and any(n <= lesson_num for n in nums):
                    res.add(strong_num)
            elif entry_type.startswith('Reading #'):
                r_num = int(entry_type.replace('Reading #', '').strip())
                if r_num <= reading_num:
                    res.add(strong_num)

    return res


if __name__ == '__main__':
    vocab_dict = load_vocab()
    print(f"Loaded {len(vocab_dict)} lessons/readings from vocab.csv.")
    for lesson, numbers in list(vocab_dict.items())[:5]:
        print(f"{lesson}: {numbers}")

    vocab_upto_7_1 = upto(7, 1)
    print(f"\nVocab upto lesson 7 and reading 1: {len(vocab_upto_7_1)} items")
