from collections import *

import load
import morphology
import vocab

def most_common_words(lemmas):
  """print the 50 most common words by lemma"""
  most_common = sorted(lemmas.items(), key=lambda x: -len(x[1]))
  for lemma, words in most_common[:50]:
    print(lemma, len(words), words[0].detail())


def print_all(words):
  for w in words:
    print(w.detail())


def get_vocab(all_words, lesson):
  """Return the vocab up to lesson #, and also the 50 most common proper nouns in the Bible"""
  return set(vocab.upto(lesson)), set(vocab.most_common(morphology.proper_nouns(all_words), 50))


def find_verses(books, vocab, proper_nouns):
  good_verses = []
  for book in books.values():
    for chapter in book:
      for verse in chapter:
        vocab_ratio = sum([w.lemma_core in vocab for w in verse]) / len(verse)
        pn_ratio = sum([w.lemma_core in proper_nouns and w.lemma_core not in vocab for w in verse]) / len(verse)
        if vocab_ratio > 0.7:
          good_verses.append((vocab_ratio, pn_ratio, verse))
  good_verses.sort(key=lambda x: (-x[0], -x[1]))

  for vr, pnr, v in good_verses:
    print(v.ref(), f'- {vr*100:.2f}% vocab & {pnr*100:.2f}% proper nouns')
    print(v.text())
    print()



def find_chapters(books, vocab, proper_nouns):
  good_chapters = []
  for book in books.values():
    for chapter in book:
      words = chapter.words()
      vocab_ratio = sum([w.lemma_core in vocab for w in words]) / len(words)
      pn_ratio = sum([w.lemma_core in proper_nouns and w.lemma_core not in vocab for w in words]) / len(words)
      if vocab_ratio + pn_ratio > 0.4:
        good_chapters.append((vocab_ratio, pn_ratio, chapter))
  good_chapters.sort(key=lambda x: (-x[0]-x[1], -x[0], -x[1]))

  for vr, pnr, c in good_chapters:
    print(c.ref(), f'- {vr*100:.2f}% vocab & {pnr*100:.2f}% proper nouns')
    print()
    print()



if __name__ == '__main__':
  books = load.load()
  genesis = books['Genesis']['']
  all_words = []
  for book in books.values():
    all_words.extend(book[''].words)

  # lemmas = by_lemma(all_words)

  #most_common_words(lemmas)

  #print_all(lemmas['3068'][:50]) # divine name

  #pn = morphology.by_lemma(morphology.proper_nouns(all_words))
  #most_common_words(pn)

  vocab, proper_nouns = get_vocab(all_words, 11)
  find_verses(books, vocab, proper_nouns)
