
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
