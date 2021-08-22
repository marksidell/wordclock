'''
Configuration for the Mark & Beth clock
'''

import datetime
from wordclock.configdefs import Word, BirthDate

VERSION_2 = True

CLOCK_NAME = "Buzz &amp; Cap'n"
LAT = 35.90823
LON = -79.04082

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

WON = Word('won', 5, 0, False)
H_ONE = Word('one', 5, 1, False)
NET = Word('net', 5, 2, False)
H_TWO = Word('two', 5, 4, False)
H_THREE = Word('three', 5, 7, False)

H_SIX = Word('six', 6, 0, False)
IF = Word('if', 6, 3, False)
H_FIVE = Word('five', 6, 4, False)
H_FOUR = Word('four', 6, 8, False)
OUR = Word('our', 6, 9, False)

ABUZZ = Word('abuzz', 7, 0, False)
BUZZ = Word('buzz', 7, 1, False)
CAP = Word('cap', 7, 5, False)
CAPN = Word('capn', 7, 5, False)
H_TEN = Word('ten', 7, 9, False)

H_SEVEN = Word('seven', 8, 0, False)
NOT = Word('not', 8, 4, False)
H_TWELVE = Word('twelve', 8, 6, False)

H_ELEVEN = Word('eleven', 9, 0, False)
END = Word('end', 9, 4, False)
H_EIGHT = Word('eight', 9, 7, False)

H_NINE = Word('nine', 10, 0, False)
NEO = Word('neo', 10, 2, False)
OK = Word('ok', 10, 4, False)
OCLOCK = Word('oclock', 10, 6, False)
CLOCK = Word('clock', 10, 7, False)
LOCK = Word('lock', 10, 8, False)

SEA = Word('sea', 1, 2, True)
VEN = Word('ven', 8, 2, True)
EVE = Word('eve', 8, 3, True)
SAT = Word('sat', 0, 4, True)
NEO2 = Word('neo', 8, 4, True)
YET2 = Word('yet', 2, 5, True)
CONK = Word('conk', 7, 5, True)
VAT = Word('vat', 6, 6, True)
DO = Word('do', 9, 6, True)
WE = Word('we', 8, 7, True)
PA = Word('pa', 3, 8, True)
TEA = Word('tea', 1, 9, True)
ROT = Word('rot', 5, 9, True)
GO = Word('go', 9, 9, True)
EAST = Word('east', 1, 10, True)
TOE = Word('toe', 3, 11, True)
NET2 = Word('net', 7, 11, True)

BIRTHDAYS = {
    BirthDate(3, 21): CAPN,
    BirthDate(9, 8): BUZZ,
}

SPECIAL_BIRTHDAY = None

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
    WON,
    H_ONE,
    NET,
    H_TWO,
    H_THREE,
    H_SIX,
    IF,
    H_FIVE,
    H_FOUR,
    OUR,
    ABUZZ,
    BUZZ,
    CAP,
    CAPN,
    H_TEN,
    H_SEVEN,
    NOT,
    H_TWELVE,
    H_ELEVEN,
    END,
    H_EIGHT,
    H_NINE,
    NEO,
    OK,
    OCLOCK,
    CLOCK,
    LOCK,
]
