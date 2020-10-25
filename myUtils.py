import sys

# Format 'V01.09 B01' or 'V01.10'
ProjectVersionNumber='V01.13 B03'

# ------------------------------------------------------------------------------
# Try if it is an int and return a default value
def tryInt(s, val=-1):
  try:
    return int(s)
  except ValueError:
    return val
