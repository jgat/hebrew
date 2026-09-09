
from dataclasses import dataclass
from collections import defaultdict
import re

_PROPER_NOUN = re.compile(r'^H(.*/)?Np.*$')

def is_proper_noun(word):
  return _PROPER_NOUN.match(word.morph) is not None


def proper_nouns(words):
  return {w for w in words if is_proper_noun(w)}


def by_lemma(words):
  lemmas = defaultdict(list)
  for w in words:
    lemmas[w.lemma_core].append(w)
  return lemmas

#####

_LANGUAGE = {
  'H': 'Hebrew',
  'A': 'Aramaic',
}

_PERSON = {'1': 'first', '2': 'second', '3': 'third', 'x': None}
_GENDER = {'b': 'both', 'c': 'common', 'f': 'feminine', 'm': 'masculine'}
_NUMBER = {'d': 'dual', 's': 'singular', 'p': 'plural'}
_STATE = {'a': 'absolute', 'c': 'construct', 'd': 'determined'}


_ADJECTIVE_TYPE = {'a': 'adjective', 'c': 'cardinal', 'o': 'ordinal'} # 'g': 'gentilic' is unused
def _parse_adjective(code_part):
  match = re.match(r'^A([acgo])([bcfm])([dsp])([acd])$', code_part)
  if not match:
    raise ValueError(f'Failed to parse adjective: {code_part}')
  t, g, n, s = match.groups()
  return _ADJECTIVE_TYPE[t], _GENDER[g], _NUMBER[n], _STATE[s]


def _parse_conjunction(code_part):
  return ()


def _parse_adverb(code_part):
  return ()


_NOUN_TYPE = {'c': 'common', 'g': 'gentilic'}
def _parse_noun(code_part):
  if code_part == 'Np':
    return ('proper', None, None, None)

  match = re.match(r'^N([cg])([bfm])([dsp])([acd])$', code_part)
  if not match:
    # Special handling for Daniel 5:25-28 (Mene Mene Tekel and Parsin)
    if code_part == 'Nxxxa':
      return ('common', 'masculine', 'singular', 'absolute')
    raise ValueError(f'Failed to parse noun: {code_part}')
  t, g, n, s = match.groups()
  return _NOUN_TYPE[t], _GENDER[g], _NUMBER[n], _STATE[s]


_PRONOUN_TYPE = {
  'd': 'demonstrative',
  'f': 'indefinite',
  'i': 'interrogative',
  'p': 'personal',
  'r': 'relative',
}
def _parse_pronoun(code_part):
  if code_part == 'Pf':
    return ('indefinite', None, None, None)
  elif code_part == 'Pi':
    return ('interrogative', None, None, None)

  match = re.match(r'^P([dprfi])([123x])([bcfm])([dsp])$', code_part)
  if not match:
    raise ValueError(f'Failed to parse pronoun: {code_part}')
  t, p, g, n = match.groups()
  return _PRONOUN_TYPE[t], _PERSON[p], _GENDER[g], _NUMBER[n]


def _parse_preposition(code_part):
  if code_part == 'R':
    return ()
  elif code_part == 'Rd':
    return ('definite article',)
  else:
    raise ValueError(f'Failed to parse preposition: {code_part}')


def _parse_suffix(code_part):
  # Suffixes without person/gender/number
  if code_part == 'Sd':
    return ('directional he', None, None, None)
  elif code_part == 'Sh':
    return ('paragogic he', None, None, None)
  elif code_part == 'Sn':
    return ('paragogic nun', None, None, None)
  
  # Suffixes with person/gender/number
  match = re.match(r'^Sp([123])([cfm])([dsp])$', code_part)
  if match:
    p, g, n = match.groups()
    return 'pronominal', _PERSON[p], _GENDER[g], _NUMBER[n]
  else:
    raise ValueError(f'Failed to parse suffix: {code_part}')


_PARTICLE_TYPE = {
  'a': 'affirmation',
  'd': 'definite article',
  'e': 'exhortation',
  'i': 'interrogative',
  'j': 'interjection',
  'm': 'demonstrative',
  'n': 'negative',
  'o': 'direct object marker',
  'r': 'relative',
  None: None,
}
def _parse_particle(code_part):
  match = re.match(r'^T([adeijmnor])?$', code_part)
  if not match:
    raise ValueError(f'Failed to parse particle: {code_part}')
  t = match.group(1)
  return (_PARTICLE_TYPE[t],)


_HEBREW_STEM = {
  'q': 'qal',
  'N': 'niphal',
  'p': 'piel',
  'P': 'pual',
  'h': 'hiphil',
  'H': 'hophal',
  't': 'hithpael',
  'o': 'polel',
  'O': 'polal',
  'r': 'hithpolel',
  'm': 'poel',
  'M': 'poal',
  'k': 'palel',
  'K': 'pulal',
  'Q': 'qal passive',
  'l': 'pilpel',
  'L': 'polpal',
  'f': 'hithpalpel',
  'D': 'nithpael',
  'j': 'pealal',
  'i': 'pilel',
  'u': 'hothpaal',
  'c': 'tiphil',
  'v': 'hishtaphel',
  'w': 'nithpalel',
  'y': 'nithpoel',
  'z': 'hithpoel'
}
_ARAMAIC_STEM = {
  'q': 'peal',
  'Q': 'peil',
  'u': 'hithpeel',
  'p': 'pael',
  'P': 'ithpaal',
  'M': 'hithpaal',
  'a': 'aphel',
  'h': 'haphel',
  's': 'saphel',
  'e': 'shaphel',
  'H': 'hophal',
  'i': 'ithpeel',
  't': 'hishtaphel',
  'v': 'ishtaphel',
  'w': 'hithaphel',
  'o': 'polel',
  'z': 'ithpoel',
  'r': 'hithpolel',
  'f': 'hithpalpel',
  'b': 'hephal',
  'c': 'tiphel',
  'm': 'poel',
  'l': 'palpel',
  'L': 'ithpalpel',
  'O': 'ithpolel',
  'G': 'ittaphal'
}
_CONJUGATION = {
  'p': 'qatal',
  'q': 'weqatal',
  'i': 'yiqtol',
  'w': 'wayyiqtol',
  'h': 'cohortative',
  'j': 'jussive',
  'v': 'imperative',
  'r': 'participle active',
  's': 'participle passive',
  'a': 'infinitive absolute',
  'c': 'infinitive construct'
}

def _parse_verb(stem, code_part):
  verbal_match = re.match(rf'^V([{"".join(stem.keys())}])([pqiwhjv])([123x])([bcfm])([dsp])$', code_part)
  if verbal_match:
    s, c, p, g, n = verbal_match.groups()
    return stem[s], _CONJUGATION[c], _PERSON[p], _GENDER[g], _NUMBER[n], None
  participle_match = re.match(rf'^V([{"".join(stem.keys())}])([rs])([bcfm])([dsp])([acd])$', code_part)
  if participle_match:
    s, c, g, n, t = participle_match.groups()
    return stem[s], _CONJUGATION[c], None, _GENDER[g], _NUMBER[n], _STATE[t]
  infinitive_match = re.match(rf'^V([{"".join(stem.keys())}])([ac])$', code_part)
  if infinitive_match:
    s, c = infinitive_match.groups()
    return stem[s], _CONJUGATION[c], None, None, None, None
  raise ValueError(f'Failed to parse verb: {code_part}')


_PARSE_VERB = {
  'Hebrew': lambda code_part: _parse_verb(_HEBREW_STEM, code_part),
  'Aramaic': lambda code_part: _parse_verb(_ARAMAIC_STEM, code_part),
}

def _parse(code):
  language = _LANGUAGE[code[0]]
  PART_OF_SPEECH = {
    'A': ('adjective', _parse_adjective),
    'C': ('conjunction', _parse_conjunction),
    'D': ('adverb', _parse_adverb),
    'N': ('noun', _parse_noun),
    'P': ('pronoun', _parse_pronoun),
    'R': ('preposition', _parse_preposition),
    'S': ('suffix', _parse_suffix),
    'T': ('particle', _parse_particle),
    'V': ('verb', _PARSE_VERB[language]),
  }
  parts = []
  for code_part in code[1:].split('/'):
    part_of_speech, parse_func = PART_OF_SPEECH[code_part[0]]
    parts.append((part_of_speech,) + parse_func(code_part))
  return language, parts


class Morphology:
  def __init__(self, code):
    self.code = code
    self.language, self.parts = _parse(code)

    self.core_index = None
    self.core = None
    if len(self.parts) == 1:
      self.core_index = 0
      self.core = self.parts[0]

    if self.core is None:
      # Any word will be at most one of: adjective, adverb, noun, pronoun, verb.
      for i, part in enumerate(self.parts):
        if part[0] in ('adjective', 'adverb', 'noun', 'pronoun', 'verb'):
          self.core_index = i
          self.core = part
          break

  def __repr__(self):
    return f"Morphology({self.code})"
  
  def is_hebrew(self):
    return self.language == 'Hebrew'
  
  def is_aramaic(self):
    return self.language == 'Aramaic'

  def is_adjective(self):
    return self.core is not None and self.core[0] == 'adjective'
  
  def is_adverb(self):
    return self.core is not None and self.core[0] == 'adverb'
  
  def is_noun(self):
    return self.core is not None and self.core[0] == 'noun'
  
  def is_pronoun(self):
    return self.core is not None and self.core[0] == 'pronoun'

  def verb(self):
    if self.core is None or self.core[0] != 'verb':
      return None
    return Verb(self.language, *self.core[1:])

  def is_proper_noun(self):
    return self.is_noun() and self.core[1] == 'proper'


@dataclass(frozen=True)
class Verb:
  language: str
  stem: str
  conjugation: str
  person: str
  gender: str
  number: str
  state: str

  def __str__(self):
    return str((self.stem, self.conjugation, self.person, self.gender, self.number, self.state))

if __name__ == '__main__':
  import collections
  import pprint

  import load

  books = load.load()
  all_morphologies = collections.Counter()
  for book in books.values():
    for verse in book.verses():
      for word in verse:
        all_morphologies[word.morph] += 1
  pprint.pprint(all_morphologies)

