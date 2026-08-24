from collections import *

import load
import morphology
import model.reference
import model.text
import vocab
import vocab2

def most_common_words(lemmas, n):
  """print the N most common words by lemma"""
  most_common = sorted(lemmas.items(), key=lambda x: -len(x[1]))
  for lemma, words in most_common[:n]:
    print(lemma, len(words), words[0].detail())


def print_all(words):
  for w in words:
    print(w.detail())


def get_vocab(all_words, lesson, reading):
  """Return the vocab up to lesson #"""
  return set(vocab2.upto(lesson, reading))


def get_proper_nouns(all_words, n):
  """Return the N most common proper nouns in the Bible."""
  return set(vocab.most_common(morphology.proper_nouns(all_words), n))


def find_verses(books, all_vocab, new_vocab, proper_nouns):
  good_verses = []
  for book in books.values():
    for chapter in book:
      for verse in chapter:
        word_count = len(verse)
        vocab_ratio = sum([w.lemma_core in all_vocab for w in verse]) / word_count
        new_ratio = sum([w.lemma_core in new_vocab for w in verse]) / word_count
        pn_ratio = sum([w.lemma_core in proper_nouns for w in verse]) / word_count

        if (vocab_ratio + pn_ratio) > 0.5 and new_ratio > 0:
          good_verses.append((new_ratio, vocab_ratio, pn_ratio, verse))
  good_verses.sort(reverse=True)

  for nr, vr, pnr, v in good_verses:
    print(v.ref(), f'- {len(v)} words; {nr*100:.2f}% new vocab; {vr*100:.2f}% vocab; {pnr*100:.2f}% proper nouns')
    print(v.text())
    print()


def find_verses_by_word(books, all_vocab, new_vocab, proper_nouns):
  good_verses = {v: [] for v in new_vocab}
  for book in books.values():
    for chapter in book:
      for verse in chapter:
        word_count = len(verse)
        vocab_ratio = sum([w.lemma_core in all_vocab or w.lemma_core in proper_nouns
                           for w in verse]) / word_count

        if vocab_ratio > 0.5:
          for v in new_vocab:
            if any(w.lemma_core == v for w in verse):
              good_verses[v].append((vocab_ratio, verse))
  for k in good_verses:
    good_verses[k].sort(reverse=True)
    print(f'\nVOCAB {k}\n')
    for vr, verse in good_verses[k]:
      print(verse.ref(), f'- {len(verse)} words; {vr*100:.2f}% vocab')
      print(verse.text())
      print()

def find_sliding_windows(books, vocab, proper_nouns, window_size=10):
  good_windows = []
  from sliding_window import sliding_window
  for book in books.values():
    for window in sliding_window(book.verses(), n=window_size):
      words = [w for v in window for w in v.words]
      passage = model.text.Passage(words, book.name, model.reference.RangeRef(words[0].ref, words[-1].ref))
      vocab_ratio = sum([w.lemma_core in vocab for w in words]) / len(words)
      pn_ratio = sum([w.lemma_core in proper_nouns for w in words]) / len(words)
      good_words = sum([w.lemma_core in proper_nouns or w.lemma_core in vocab for w in words]) / len(words)
      if good_words > 0.84 and pn_ratio < 0.33 and book.name != 'Genesis':
        good_windows.append((vocab_ratio, pn_ratio, book.name, passage))
  good_windows.sort(key=lambda x: (-x[0], -x[0]-x[1]))

  for vr, pnr, book_name, passage in good_windows:
    print(book_name, passage.ref, f'- {len(passage.words)} words, {vr*100:.2f}% vocab & {pnr*100:.2f}% proper nouns')
    print(passage.text(vocab.union(proper_nouns.keys())))
    print()
  print(len(good_windows))


def find_chapters(books, vocab, proper_nouns):
  good_chapters = []
  for book in books.values():
    for chapter in book:
      words = chapter.words()
      vocab_ratio = sum([w.lemma_core in vocab for w in words]) / len(words)
      pn_ratio = sum([w.lemma_core in proper_nouns for w in words]) / len(words)
      if vocab_ratio + pn_ratio > 0.7 and pn_ratio < 0.2:
        good_chapters.append((vocab_ratio, pn_ratio, chapter))
  good_chapters.sort(key=lambda x: (-x[0]-x[1], -x[0], -x[1]))

  for vr, pnr, c in good_chapters:
    print(c.ref(), f'- {len(c.words())} words, {vr*100:.2f}% vocab & {pnr*100:.2f}% proper nouns')
    print()
    print()



if __name__ == '__main__':
  books = load.load()
  genesis = books['Genesis']['']
  all_words = []
  for book in books.values():
    all_words.extend(book[''].words)


  all_vocab = get_vocab(None, 40, 9)
  pn = morphology.by_lemma(morphology.proper_nouns(all_words))
  
  #find_chapters(books, all_vocab, pn)
  find_sliding_windows(books, all_vocab, pn)

  # lemmas = by_lemma(all_words)

  #most_common_words(lemmas)

  #print_all(lemmas['3068'][:50]) # divine name

  #most_common_words(pn, 70)

  # all_vocab = get_vocab(all_words, 14)  # week 5
  # new_vocab = {
  #   '4100',
  #   '4069',
  #   '349',
  #   '4970',
  #   '335',
  #   '346',
  #   '375',
  #   '370',
  #   '575',
  # } # question words
  # proper_nouns = get_proper_nouns(all_words, 70) - all_vocab

  # find_verses_by_word(books, all_vocab, new_vocab, proper_nouns)
  # #find_chapters(books, all_vocab, proper_nouns)

