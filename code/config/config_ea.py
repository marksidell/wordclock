'''
Configuration for the Elle & Ale clock
'''

import datetime
from wordclock.configdefs import Word, BirthDate, SpecialBirthday

VERSION_2 = True

CLOCK_NAME = "Elle &amp; Ale"

LAT = 28.610940839823634
LON = -81.33362929069895

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
TO1 = Word('to', 3, 11, False)

ORB = Word('orb', 4, 0, False)
BIRTH = Word('birth', 4, 2, False)
BIRTHDAY = Word('birthday', 4, 2, False)
DAY = Word('day', 4, 7, False)
TO = Word('to', 4, 10, False)

H_FOUR = Word('four', 5, 5, False)
OUR = Word('ou4', 5, 2, False)
H_FIVE = Word('five', 5, 1, False)
H_SIX = Word('six', 5, 9, False)

AUGGIE = Word('auggie', 6, 1, False)
ELLE = Word('elle', 6, 6, False)
EON = Word('eon', 6, 9, False)
LEO = Word('leo', 6, 8, False)
ALE = Word('ale', 6, 1, True)

H_EIGHT = Word('eight', 7, 7, False)
ELIAH = Word('eliah', 7, 1, False)
HEIGHT = Word('height', 7, 6, False)
TEE = Word('tee', 7, 11, True)

H_ONE = Word('one', 8, 4, False)
VET = Word('net', 8, 0, False)
H_TWO = Word('two', 8, 2, False)
H_THREE = Word('three', 8, 7, False)
H_TEN = Word('ten', 8, 2, True)

H_SEVEN = Word('seven', 9, 1, False)
H_TWELVE = Word('twelve', 9, 6, False)

H_ELEVEN = Word('eleven', 5, 0, True)

H_NINE = Word('nine', 10, 2, False)
NO = Word('no', 10, 0, False)
NON = Word('non', 10, 0, False)
NEO = Word('neo', 10, 4, False)
OCLOCK = Word('oclock', 10, 6, False)
CLOCK = Word('clock', 10, 7, False)
LOCK = Word('lock', 10, 8, False)

EVE2 = Word('eve', 7, 0, True)
VEN = Word('ven', 8, 0, True)
TOM = Word('tom', 9, 1, True)
SEA = Word('sea', 1, 2, True)
NOG = Word('nog', 5, 2, True)
SAT = Word('sat', 0, 4, True)
YET2 = Word('yet', 2, 5, True)
EEL = Word('eel', 8, 8, True)
TEA = Word('tea', 1, 9, True)
EAST = Word('east', 1, 10, True)
TOE = Word('toe', 3, 11, True)
HEN = Word('hen', 7, 11, True)

A0 = Word('a', 0, 7, False)
A1 = Word('a', 1, 1, False)
A2 = Word('a', 1, 4, False)
A3 = Word('a', 2, 10, False)
A4 = Word('a', 3, 2, False)
A5 = Word('a', 3, 9, False)
A6 = Word('a', 4, 8, False)
A7 = Word('a', 6, 1, False)
A8 = Word('a', 7, 5, False)


BIRTHDAYS = {
    BirthDate(8, 25): ELLE,
    BirthDate(5, 13): ALE,
    BirthDate(6, 5): ELIAH,
    BirthDate(8, 3): AUGGIE,
}

SPECIAL_BIRTHDAY = SpecialBirthday(
    ELLE,
    datetime.date(2021, 8, 28),
    datetime.date(2021, 9, 5))


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
    TO1,
    ORB,
    BIRTH,
    BIRTHDAY,
    DAY,
    TO,
    H_ONE,
    VET,
    H_TWO,
    H_THREE,
    H_SIX,
    H_FIVE,
    H_FOUR,
    ELIAH,
    HEIGHT,
    TEE,
    AUGGIE,
    ELLE,
    EON,
    LEO,
    ALE,
    H_TEN,
    H_SEVEN,
    H_TWELVE,
    H_ELEVEN,
    H_EIGHT,
    H_NINE,
    NO,
    NON,
    NEO,
    OCLOCK,
    CLOCK,
    LOCK,
    EVE2,
    VEN,
    TOM,
    SEA,
    NOG,
    SAT,
    YET2,
    EEL,
    TEA,
    EAST,
    TOE,
    HEN,

    A0,
    A1,
    A2,
    A3,
    A4,
    A5,
    A6,
    A7,
    A8,
]
