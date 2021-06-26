'''
Namedtuples used in the config files
'''

from collections import namedtuple

# Defines a word on the clock face
#
Word = namedtuple(
    'Word',
    [
        'text',     # The word text, used to calculate its length
        'y',        # The starting row
        'x',        # The startin column
        'vertical'  # True if the word is vertical
    ])

# Defines a birthday
#
BirthDate = namedtuple(
    'BirthDate',
    [
        'month',    # The month (1..12)
        'day',      # The month day (1..)
    ])

# Used to cause the clock to display the birthday message on a
# special range of days. I used this when I ended up delivering the
# clock late, and wanted my not to wait a year to see the greeting.
#
SpecialBirthday = namedtuple(
    'SpecialBirthday',
    [
        'name',     # The config variable for the name to display
        'begin',    # A datetime.Date() specifying the start day
        'end',      #  A datetime.Date() specifying the day after the end day
    ])
