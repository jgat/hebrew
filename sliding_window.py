from itertools import islice

def sliding_window(iterable, n):
  """
  Returns an iterable of tuples of size n sliding through the input.
  """
  it = iter(iterable)
  window = tuple(islice(it, n))
  if len(window) == n:
    yield window
  for elem in it:
    window = window[1:] + (elem,)
    yield window

if __name__ == '__main__':
  for window in sliding_window('abcdefghi', 3):
    print(window)