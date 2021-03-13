'''
Configuration for the Doug & Marguerite clock
'''

import datetime
from wordclock.configdefs import Word, BirthDate, SpecialBirthday

VERSION_2 = False

CLOCK_NAME = 'Holmgren-Rogers'
LAT = 45.45918
LON = -122.72911

IT = Word('it', 0, 0, False)
TWIST = Word('twist', 0, 1, False)
IS = Word('is', 0, 3, False)
T_HALF = Word('half', 0, 6, False)
FOR = Word('for', 0, 9, False)

MASH = Word('mash', 1, 0, False)
AS0 = Word('as', 1, 1, False)
ASH = Word('ash', 1, 1, False)
HAPPY = Word('happy', 1, 3, False)
YET = Word('yet', 1, 7, False)
T_TEN = Word('ten', 1, 9, False)

T_TWENTY = Word('twenty', 2, 0, False)
T_FIVE = Word('five', 2, 6, False)
T_TWENTYFIVE = Word('twentyfive', 2, 0, False)
EAR = Word('ear', 2, 9, False)

T_QUARTER = Word('quarter', 3, 0, False)
REPAST = Word('repast', 3, 6, False)
PAST = Word('past', 3, 8, False)
AS1 = Word('as', 3, 9, False)

ORB = Word('orb', 4, 0, False)
BIRTH = Word('birth', 4, 2, False)
BIRTHDAY = Word('birthday', 4, 2, False)
DAY = Word('day', 4, 7, False)
TO = Word('to', 4, 10, False)

H_ONE = Word('one', 5, 1, False)
NET = Word('net', 5, 2, False)
H_TWO = Word('two', 5, 4, False)
H_THREE = Word('three', 5, 7, False)

H_FOUR = Word('four', 6, 1, False)
OUR = Word('ou4', 6, 2, False)
H_FIVE = Word('five', 6, 5, False)
H_SIX = Word('six', 6, 9, False)

H_EIGHT = Word('eight', 7, 0, False)
DOUG = Word('doug', 7, 5, False)
GO = Word('go', 7, 8, False)
GOAL = Word('goal', 7, 8, False)

MARGUERITE = Word('marguerite', 8, 1, False)
IT2 = Word('it', 8, 8, False)
H_TEN = Word('ten', 8, 9, False)

H_SEVEN = Word('seven', 9, 1, False)
H_TWELVE = Word('twelve', 9, 6, False)

H_ELEVEN = Word('eleven', 5, 0, True)

H_NINE = Word('nine', 10, 0, False)
NEO = Word('neo', 10, 2, False)
OK = Word('ok', 10, 4, False)
OCLOCK = Word('oclock', 10, 6, False)
CLOCK = Word('clock', 10, 7, False)
LOCK = Word('lock', 10, 8, False)

BIRTHDAYS = {
    BirthDate(2, 20): DOUG,
    BirthDate(9, 17): MARGUERITE,
}

SPECIAL_BIRTHDAY = SpecialBirthday(
    DOUG,
    datetime.date(2021, 3, 11),
    datetime.date(2021, 3, 17))

ALL_WORDS = [
    IT,
    TWIST,
    IS,
    T_HALF,
    FOR,
    MASH,
    AS0,
    ASH,
    HAPPY,
    YET,
    T_TEN,
    T_TWENTY,
    T_FIVE,
    T_TWENTYFIVE,
    EAR,
    T_QUARTER,
    REPAST,
    PAST,
    AS1,
    ORB,
    BIRTH,
    BIRTHDAY,
    DAY,
    TO,
    H_ONE,
    NET,
    H_TWO,
    H_THREE,
    H_SIX,
    H_FIVE,
    H_FOUR,
    OUR,
    DOUG,
    MARGUERITE,
    IT2,
    GO,
    GOAL,
    H_TEN,
    H_SEVEN,
    H_TWELVE,
    H_ELEVEN,
    H_EIGHT,
    H_NINE,
    NEO,
    OK,
    OCLOCK,
    CLOCK,
    LOCK,
]
