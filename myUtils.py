import sys

# ------------------------------------------------------------------------------
# Try if it is an int and return a default value
def tryInt(s, val=-1):
  try:
    return int(s)
  except ValueError:
    return val
