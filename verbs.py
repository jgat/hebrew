from collections import defaultdict

import load

if __name__ == '__main__':
  books = load.load()

  verbs = defaultdict(list)
  for book in books.values():
    for word in book.words():
      verb = word.morph2.verb()
      if word.morph2.is_hebrew() and verb:
        verbs[verb].append(word)

  result = sorted(verbs.items(), key=lambda x: len(x[1]), reverse=True)
  for k, v in result:
    if k.stem in ('qal', 'niphal', 'piel', 'hiphil', 'hithpael'):
      print(k, len(v))
