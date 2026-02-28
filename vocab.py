import morphology

BONUS = [
  '2895', # tov
  '1984', # halal
  '543', # amen
]

LESSON = {
  3: [
    '3068', # divine name: adonai
    '3069', # divine name: elohim
    '113', # adon
    '136', # adonai
    '430', # elohim
  ],

  5: [
    '589', # 'ani
    '859', # 'attah / 'at
    '1931', # hu or hi (see also 1932 for aramaic)

    '1697', # dabar
    '3651', # ken (see also 3652, 3653, 3654)
    '3808', # lo
    '7965', # shalom
  ],

  6: [
    '1961', # hayah

    '376', # ish
    '802', # ishshah
    '5288', # naar (see also 5289)
    '5291', # naarah (see also 5292)
    '4310', # mi
    '8034', # shem (see also 8036 for aramaic)
  ],

  7: [
    '127', # adamah
    '929', # behemah
    '8451', # torah
    '1285', # berit
    '4438', # malkut
    '2403', # chattah (see also 2402 for aramaic)
    '3207', # yad (see also 3208 for aramaic)
    '5869', # ayin (see also 5870 for aramaic)
    '7272', # regel
    '5483', # sus (TODO: solve for 5483a / 5483b)
    '5484', # susa
    '1', # av
    '517', # em
    '1121', # ben
    '1323', # bat
    '2145', # zachar
    '5347', # neqevah
  ],
}

def upto(lesson):
  res = list(BONUS)
  for l, vocab in LESSON.items():
    if l <= lesson:
      res += vocab
  return res


def most_common(words, n):
  """Return the N most common lemmas"""
  lemmas = morphology.by_lemma(words)
  common = sorted(lemmas.items(), key=lambda x: len(x[1]), reverse=True)
  return [l for l, w in common[:n]]

