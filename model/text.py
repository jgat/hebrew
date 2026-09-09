"""Model for biblical texts: words, passages, books.
"""
from dataclasses import dataclass
import re

from . import reference

_LEMMA = re.compile(r'^((?:[a-z]/)*[a-z]?)?(\d+)?( [a-z]|\+)?$')

@dataclass() #frozen=True)
class Word:
  text: str
  lemma: str
  morph: str
  book: str
  ref: reference.WordRef

  def __post_init__(self):
    match = _LEMMA.match(self.lemma)
    if not match:
      raise ValueError(f'bad lemma: {self}')
    self.lemma_prefix, self.lemma_core, self.lemma_suffix = match.groups()

  def detail(self):
    return f'<{self.book} {self.ref}: {self.text}\u200e {self.lemma} {self.morph}>'

  def __hash__(self):
    return hash((self.book, self.ref))

  def __str__(self):
    return f"<{self.book} {self.ref} - {self.text} {self.lemma} {self.morph}>"


@dataclass(frozen=True)
class Passage:
  words: list[Word]
  book: str
  ref: reference.RangeRef

  def __getitem__(self, item):
    return self.words[item]

  def __iter__(self):
    return iter(self.words)

  def __str__(self):
    return ' '.join(w.text for w in self.words)

  def detail(self, vocab=None):
    text = []
    missing_lemmas = set()
    for w in self.words:
      line = f'{w.book} {w.ref:8}: {w.text:10}\u200e\t{w.lemma:10} {w.morph}'
      if vocab is not None and w.lemma_core not in vocab:
        line += f'\t\t********'
        missing_lemmas.add(w.lemma_core)
      text.append(line)
    return '\n'.join(text) + '\n\nMissing lemmas: ' + ', '.join(sorted(missing_lemmas))

  def text(self, vocab):
    words = []
    for w in self.words:
      text = w.text.replace('/', '')
      if w.lemma_core in vocab:
        words.append(text)
      else:
        words.append(f'_({text})_')
    return ' '.join(words)


@dataclass(frozen=True)
class Verse:
  words: list[Word]

  def __getitem__(self, item):
    if isinstance(item, int):
      if item <= 0:
        raise ValueError(f"can't subscript verse with <= 0: {item}")
      return self.words[item-1]
    else:
      raise TypeError(f"can't subscript verse with {type(item)}")

  def __len__(self): return len(self.words)

  def __iter__(self): return iter(self.words)

  def __lt__(self, other):
    return self.ref() < other.ref()

  def slice(self, a, z):
    """Returns a subset of the words in this verse, bounded by a-z."""
    # check bounds & resolve END
    if z == reference.END:
      z = len(self)
    if a > len(self) or z > len(self):
      raise IndexError(f'words {a}-{z} out of bounds for verse of length {len(self)}')
    return self.words[a-1:z]

  def as_passage(self):
    return Passage(self.words, self.words[0].book,
                   reference.RangeRef(self.words[0].ref, self.words[-1].ref))

  def ref(self):
    if len(self.words) < 1: return '[empty verse]'
    w = self.words[0]
    return f'{w.book} {w.ref.chapter}:{w.ref.verse}'

  def text(self):
    return ' '.join(w.text for w in self.words)


@dataclass(frozen=True)
class Chapter:
  verses: list[Verse]

  def __getitem__(self, item):
    if isinstance(item, int):
      if item <= 0:
        raise ValueError(f"can't subscript chapter with <= 0: {item}")
      return self.verses[item-1]
    else:
      raise TypeError(f"can't subscript chapter with {type(item)}")

  def __len__(self): return len(self.verses)

  def __iter__(self): return iter(self.verses)

  def words(self):
    return [w for verse in self for w in verse]

  def ref(self):
    if len(self) < 1 or len(self.verses[0]) < 1: return '[empty chapter]'
    w = self.verses[0].words[0]
    return f'{w.book} {w.ref.chapter}'

  def slice(self, a_verse, a_word, z_verse, z_word):
    """Returns a subset of the words in this chapter, bounded by a-z."""
    # check bounds & resolve END
    if z_verse == reference.END:
      z_verse = len(self)
    if a_verse > len(self) or z_verse > len(self):
      raise IndexError(f'verses {a_verse}-{z_verse} out of bounds for chapter of length {len(self)}')

    if a_verse == z_verse:
      return self[a_verse].slice(a_word, z_word)

    words = self[a_verse].slice(a_word, reference.END)
    for v in self.verses[a_verse:z_verse-1]:
      words.extend(v.words)
    words.extend(self[z_verse].slice(1, z_word))
    return words


@dataclass(frozen=True)
class Book:
  name: str
  chapters: list[Chapter]

  def __getitem__(self, item):
    """Gets a chapter or passage.

    book[1] returns the first Chapter (1-indexed). Slices aren't supported.
    book['1'] returns a Passage containing all the words in chapter 1.
    book['1:2-3:4'] returns the passage of 1:2 through 3:4.
    """
    if isinstance(item, int):
      if item <= 0:
        raise ValueError(f"can't subscript book with <= 0: {item}")
      return self.chapters[item-1]
    elif isinstance(item, str):
      ref = reference.parse(item)
      return self.lookup(ref)
    elif isinstance(item, reference.RangeRef):
      return self.lookup(item)
    else:
      raise TypeError(f"can't subscript book with {type(item)}")

  def __len__(self): return len(self.chapters)

  def __iter__(self): return iter(self.chapters)

  def __repr__(self):
    return f"Book({self.name!r}, {len(self.chapters)} chapters)"
  
  def __str__(self):
    return f"{self.name} ({len(self.chapters)} chapters)"

  def verses(self):
    for c in self.chapters:
      for v in c.verses:
        yield v
  
  def words(self):
    for c in self.chapters:
      for v in c.verses:
        for w in v:
          yield w
  
  def lookup(self, ref):
    """Look up a passage by reference.RangeRef"""
    # check bounds & resolve END
    a, z = ref.start.chapter, ref.end.chapter
    if z == reference.END:
      z = len(self)
    if a > len(self) or z > len(self):
      raise IndexError(f'chapters {a}-{z} out of bounds for book {self.name} of length {len(self)}')

    if a == z:
      words = self[a].slice(ref.start.verse, ref.start.word, ref.end.verse, ref.end.word)
    else:
      words = self[a].slice(ref.start.verse, ref.start.word, reference.END, reference.END)
      for c in self.chapters[a:z-1]:
        for v in c.verses:
          words.extend(v.words)
      words.extend(self[z].slice(1, 1, ref.end.verse, ref.end.word))

    return Passage(words, self.name, ref)
