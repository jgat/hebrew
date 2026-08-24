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
    '1285', # berit
    '1', # av
    '517', # em
    '1121', # ben
    '1323', # bat
    '2145', # zachar
    '5347', # neqevah
    # '8451', # torah
    # '4438', # malkut
    # '2403', # chattah (see also 2402 for aramaic)
  ],

  8: [
    '1004', # bayith (see also 1005 for aramaic)
    '4100', # mah (see also 4101 for aramaic)
    # ha article + interrogative
  ],

  9: [
    'l', # l of possession
    '776', # erets
    '4428', # melek
  ],

  10: [
    '241', # ozer
    '251', # ach
    '269', # achoth
    '7218', # rosh
    '7272', # regel
    '3207', # yad (see also 3208 for aramaic)
    '5869', # ayin (see also 5870 for aramaic)

    # Reading R1
    '1817', # 
    '7979', # 
    '3678', # 
    '6086', # 
    '953', # 
    '4940', # 
    '929', # behemah
    '352', # 
    '7716', # 
    '5483', # sus (TODO: solve for 5483a / 5483b)
    '5484', # susa
    '6499', # 
    '6510', # 
    '1581', # 
    '2543', # 
    '5795', # 
    '120', # 
    '3206', # 
    '3207', # 
    '7776', # 
    '5175', # 
    # '2421b', # TODO: solve for chayyah = "life", not "animal"
  ],

  11: [
    '3605', # 
    '1992', # 
    '2004', # 
    '859', # 
    '587', # 
    '5892', # 
    '1961', # 
    '5650', # 
    '3426', # 
  ],

  12: [
    '3426',
    '369',
    '4725',
    '8033',
  ],

  13: [
    '4325',
    '3220',
    '5973',
    '8064',
    '5921',
    '3942',
  ],

  14: [
    '5930',
    '4100',
    '4069',
    '349',
    '4970',
    '335',
    '346',
    '375',
    '370',
    '575',

    # Reading R2
    '3978',
    '6529',
    '5929',
    '1588',
    '5903',
  ],
}

def upto(lesson):
  res = list(BONUS)
  for l, vocab in LESSON.items():
    if l <= lesson:
      res += vocab
  return set(res)


def most_common(words, n):
  """Return the N most common lemmas"""
  lemmas = morphology.by_lemma(words)
  common = sorted(lemmas.items(), key=lambda x: len(x[1]), reverse=True)
  return [l for l, w in common[:n]]

