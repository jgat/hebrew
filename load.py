from dataclasses import dataclass
import json

import model

# hebrew.json is the output of this script:
# https://github.com/openscriptures/morphhb/blob/master/morphhbXML-to-JSON.py
FILENAME = 'hebrew.json'

def load(filename=FILENAME):
  books = {}
  with open(filename) as f:
    data = json.load(f)
  for name, chapters in data.items():
    books[name] = model.Book(
        name,
        [model.Chapter(
            [model.Verse(
                [model.Word(*word, name, model.WordRef(c, v, w))
                 for w, word in enumerate(verse, 1)])
             for v, verse in enumerate(chapter, 1)])
         for c, chapter in enumerate(chapters, 1)]
    )

  return books
