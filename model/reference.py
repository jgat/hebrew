"""Model for chapter/verse references.
"""
from dataclasses import dataclass
import re

class _End(int):
  """_End is a sentinel value for the final verse of a chapter or the final word
  of a verse."""

  def __str__(self):
    return 'END'

  def __repr__(self):
    return f'{self.__class__.__name__}({int(self)})'


END = _End(-1)


@dataclass(frozen=True)
class WordRef:
  """A WordRef is a single chapter-verse-word index.

  We use the notation "chapter:verse.word" to index a single word of text.
  Example: Genesis 1:2.9 = ninth word of Genesis 1:2 ('elohim').

  verse or word may be the sentinel value END.
  """
  chapter: int
  verse: int
  word: int

  def __post_init__(self):
    if 1 > self.chapter != END:
      raise ValueError(f'chapter < 1: {self.chapter}')
    if 1 > self.verse != END:
      raise ValueError(f'verse < 1: {self.verse}')
    if 1 > self.word != END:
      raise ValueError(f'word < 1: {self.word}')

  def __str__(self):
    return f'{self.chapter}:{self.verse}.{self.word}'

  def __format__(self, spec):
    return format(str(self), spec)

  def __hash__(self):
    return hash((self.chapter, self.verse, self.word))

  def has_end(self):
    return self.chapter == END or self.verse == END or self.word == END


@dataclass(frozen=True)
class RangeRef:
  """A RangeRef indexes a range of one or more words.

  Example:
    Genesis 1:2-3 => RangeRef(WordRef(1, 2, 1), WordRef(1, 3, 5))
      (noting that Genesis 1:3 contains 5 words).
  """
  start: WordRef
  end: WordRef
  name: str = None

  def __post_init__(self):
    if self.start.has_end():
      raise ValueError(f'starts with END: {self.start}')
    if self.start.chapter > self.end.chapter != END:
      raise ValueError(f'{self.start} > {self.end} (chapter)')
    if self.start.chapter == self.end.chapter:
      if self.start.verse > self.end.verse != END:
        raise ValueError(f'{self.start} > {self.end} (verse)')
      if self.start.verse == self.end.verse and self.start.word > self.end.word != END:
        raise ValueError(f'{self.start} > {self.end} (word)')

  def __str__(self):
    return f'{self.start}-{self.end}'

  def __format__(self, spec):
    return format(str(self), spec)


def parse(ref_string):
  """Parses a verse reference.

  Example: Gen 1-2 = Gen 1:1-2:25, or Gen 1:1-2 = Gen 1:1-1:2
  Uses the token END for "last verse of a chapter" or "last word of a verse".

  Format: 1(:2(.3)?)?(-7(:8)?(.9)?)?

  Parsing:
    1:2.3-7:8.9 means "from chapter 1 verse 2 word 3, to chapter 7 verse 8
    word 9", abbreviated: ((start_chapter, start_verse, start_word),
                           (end_chapter, end_verse, end_word))

  Full parsing rules:
    1:2.3-7:8.9 = ((1, 2, 3), (7, 8, 9))
    1:2.3-7:8   = ((1, 2, 3), (7, 8, end))    # 7 is the chapter number
    1:2.3-7.9   = ((1, 2, 3), (1, 7, 9))      # 7 is the verse number
    1:2.3-7     = ((1, 2, 3), (1, 2, 7))      # 7 is the word number
    1:2.3       = ((1, 2, 3), (1, 2, 3))
    1:2-7:8.9   = ((1, 2, 1), (7, 8, 9))
    1:2-7:8     = ((1, 2, 1), (7, 8, end))    # 7 is the chapter number
    1:2-7.9     = ((1, 2, 1), (1, 7, 9))      # 7 is the verse number
    1:2-7       = ((1, 2, 1), (1, 7, end))    # 7 is the verse number
    1:2         = ((1, 2, 1), (1, 2, end))
    1-7:8.9     = ((1, 1, 1), (7, 8, 9))
    1-7:8       = ((1, 1, 1), (7, 8, end))    # 7 is the chapter number
    1-7.9       = invalid
    1-7         = ((1, 1, 1), (7, end, end))  # 7 is the chapter number
    1           = ((1, 1, 1), (1, end, end))
    <empty string> = ((1, 1, 1), (end, end, end))  # entire book
  """
  if ref_string == '':
    return RangeRef(WordRef(1, 1, 1), WordRef(END, END, END), ref_string)

  verse_format = re.compile(r'^(?P<a_chapter>\d+)(?::(?P<a_verse>\d+)(?:\.(?P<a_word>\d+))?)?(?:-(?P<z_part>\d+)(?::(?P<z_verse>\d+))?(?:\.(?P<z_word>\d+))?)?$')
  match = verse_format.match(ref_string)
  if not match:
    raise ValueError(f'invalid reference format for {ref_string!r}')

  a_chapter, a_verse, a_word, z_part, z_verse, z_word = match.groups()
  z_chapter = None
  if a_verse is None and z_verse is None and z_word is not None:
    # This is the "1-7.9" case above.
    raise ValueError(f'invalid reference format (1-7.9) for {ref_string!r}')

  # Figure out whether the z_part (e.g. "7") is a chapter, verse, or word.
  if z_verse is not None or (a_verse is None and z_verse is None):
    # Reference is "...-7:8" or "...-7:8.9" or "1-7" -> 7 is a chapter number.
    z_chapter = z_part
  elif z_word is None and a_word is not None:
    # Reference is "1:2.3-7" -> 7 is a word number.
    z_word = z_part
  else:
    # Reference is "1:2-7" or "1:2.3-7.9" or "1:2-7.9" -> 7 is a verse number.
    z_verse = z_part

  # End reference defaults to start reference (e.g. 1:2-7 = 1:2-1:7)
  if z_chapter is None:
    z_chapter = a_chapter
  if z_verse is None:
    z_verse = a_verse
  if z_part is None:
    # Reference is a single verse
    z_word = a_word

  # Start reference defaults to 1 (e.g. Gen 1-2 starts from Gen 1:1)
  if a_verse is None:
    a_verse = 1
  if a_word is None:
    a_word = 1

  a_chapter = int(a_chapter)
  a_verse = int(a_verse)
  a_word = int(a_word)
  z_chapter = int(z_chapter)

  # End reference defaults to "end" (e.g. Gen 1-2 ends at Gen 2:25).
  if z_verse is None:
    z_verse = END
  else:
    z_verse = int(z_verse)

  if z_word is None:
    z_word = END
  else:
    z_word = int(z_word)

  return RangeRef(WordRef(a_chapter, a_verse, a_word),
                  WordRef(z_chapter, z_verse, z_word),
                  ref_string)

