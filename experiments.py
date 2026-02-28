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
  return set(vocab.upto(lesson)
             + vocab.most_common(morphology.proper_nouns(all_words), 50))


def find_verses(books, vocab):
  good_verses = []
  for book in books.values():
    for chapter in book:
      for verse in chapter:
        hit = [w.lemma_core in vocab for w in verse]
        ratio = sum(hit) / len(verse)
        if ratio > 0.5:
          pn = sum([morphology.is_proper_noun(w) for w in verse])
          pn_ratio = pn / len(verse)
          good_verses.append((ratio, pn_ratio, verse))
  good_verses.sort(key=lambda x: (x[1]-x[0], -x[0]))

  for r, pnr, v in good_verses:
    print(v.ref())
    print(f'{r:.4f} vocab, {pnr:.4f} proper nouns')
    print(v.text())
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

  vocab = get_vocab(all_words, 6)
  find_verses(books, vocab)
