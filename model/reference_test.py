import unittest

from reference import *

class ParseTest(unittest.TestCase):
  def test_parse(self):
    cases = [
      ('1:2.3-7:8.9', (1, 2, 3), (7, 8, 9)),
      ('1:2.3-7:8',   (1, 2, 3), (7, 8, END)),    # 7 is the chapter number
      ('1:2.3-7.9',   (1, 2, 3), (1, 7, 9)),      # 7 is the verse number
      ('1:2.3-7',     (1, 2, 3), (1, 2, 7)),      # 7 is the word number
      ('1:2.3',       (1, 2, 3), (1, 2, 3)),
      ('1:2-7:8.9',   (1, 2, 1), (7, 8, 9)),
      ('1:2-7:8',     (1, 2, 1), (7, 8, END)),    # 7 is the chapter number
      ('1:2-7.9',     (1, 2, 1), (1, 7, 9)),      # 7 is the verse number
      ('1:2-7',       (1, 2, 1), (1, 7, END)),    # 7 is the verse number
      ('1:2',         (1, 2, 1), (1, 2, END)),
      ('1-7:8.9',     (1, 1, 1), (7, 8, 9)),
      ('1-7:8',       (1, 1, 1), (7, 8, END)),    # 7 is the chapter number
      ('1-7',         (1, 1, 1), (7, END, END)),  # 7 is the chapter number
      ('1',           (1, 1, 1), (1, END, END)),
      ('',            (1, 1, 1), (END, END, END)),  # entire book
    ]

    for ref, start, end in cases:
      self.assertEqual(parse(ref), RangeRef(WordRef(*start), WordRef(*end)), ref)

  def test_invalid(self):
    self.assertRaises(ValueError, parse, '1-7.9')

if __name__ == '__main__':
    unittest.main()
