'''
Configuration for the Doug & Paty clock
'''

from wordclock.configdefs import Word, BirthDate

VERSION_2 = True

CLOCK_NAME = 'Doug &amp; Paty'

LAT = 38.9865696556791
LON = -77.01922719335109

IT = Word('it', 0, 0, False)
TWIST = Word('twist', 0, 1, False)
WIST = Word('wist', 0, 2, False)
IS = Word('is', 0, 3, False)
HA = Word('ha', 0, 6, False)
T_HALF = Word('half', 0, 6, False)
A = Word('a', 0, 7, False)
FOR = Word('for', 0, 9, False)
OR = Word('or', 0, 10, False)

MA = Word('ma', 1, 0, False)
MASH = Word('mash', 1, 0, False)
A_1 = Word('a', 1, 1, False)
AS = Word('as', 1, 1, False)
ASH = Word('ash', 1, 1, False)
HA_1 = Word('ha', 1, 3, False)
HAP = Word('hap', 1, 3, False)
HAPPY = Word('happy', 1, 3, False)
A_2 = Word('a', 1, 4, False)
APP = Word('app', 1, 4, False)
PYE = Word('pye', 1, 6, False)
YE = Word('ye', 1, 7, False)
YET = Word('yet', 1, 7, False)
T_TEN = Word('ten', 1, 9, False)

T_TWENTY = Word('twenty', 2, 0, False)
T_TWENTYFIVE = Word('twentyfive', 2, 0, False)
WE = Word('we', 2, 1, False)
WEN = Word('wen', 2, 1, False)
WENT = Word('went', 2, 1, False)
T_FIVE = Word('five', 2, 6, False)
EAR = Word('ear', 2, 9, False)
A_3 = Word('a', 2, 10, False)

QUA = Word('qua', 3, 0, False)
QUART = Word('quart', 3, 0, False)
T_QUARTER = Word('quarter', 3, 0, False)
A_4 = Word('a', 3, 2, False)
ART = Word('art', 3, 2, False)
ERE = Word('ere', 3, 5, False)
REP = Word('rep', 3, 6, False)
REPAST = Word('repast', 3, 6, False)
PA = Word('pa', 3, 8, False)
PAS = Word('pas', 3, 8, False)
PAST = Word('past', 3, 8, False)
A_5 = Word('a', 3, 9, False)
AS_1 = Word('as', 3, 9, False)

OR_1 = Word('or', 4, 0, False)
ORB = Word('orb', 4, 0, False)
BIRTH = Word('birth', 4, 2, False)
BIRTHDAY = Word('birthday', 4, 2, False)
DAY = Word('day', 4, 7, False)
A_6 = Word('a', 4, 8, False)
TO = Word('to', 4, 10, False)

EON = Word('eon', 5, 0, False)
ON = Word('on', 5, 1, False)
H_ONE = Word('one', 5, 1, False)
NET = Word('net', 5, 2, False)
H_TWO = Word('two', 5, 4, False)
WOT = Word('wot', 5, 5, False)
H_THREE = Word('three', 5, 7, False)

FOU = Word('fou', 6, 1, False)
H_FOUR = Word('four', 6, 1, False)
OUR = Word('our', 6, 2, False)
H_FIVE = Word('five', 6, 5, False)
SI = Word('si', 6, 9, False)
H_SIX = Word('six', 6, 9, False)

H_EIGHT = Word('eight', 7, 0, False)
DO = Word('do', 7, 5, False)
DOUG = Word('doug', 7, 5, False)
H_TEN = Word('ten', 7, 9, False)

PA_1 = Word('pa', 8, 1, False)
PAT = Word('pat', 8, 1, False)
PATY = Word('paty', 8, 1, False)
A_7 = Word('a', 8, 2, False)
AT = Word('at', 8, 2, False)
LUCAS = Word('lucas', 8, 5, False)
CASA = Word('casa', 8, 7, False)
A_8 = Word('a', 8, 8, False)
AS_2 = Word('as', 8, 8, False)
SAT = Word('sat', 8, 9, False)
A_9 = Word('a', 8, 10, False)
AT_1 = Word('at', 8, 10, False)

H_SEVEN = Word('seven', 9, 1, False)
EVE = Word('eve', 9, 2, False)
EVEN = Word('even', 9, 2, False)
EVENT = Word('event', 9, 2, False)
VENT = Word('vent', 9, 3, False)
H_TWELVE = Word('twelve', 9, 6, False)
WE_1 = Word('we', 9, 7, False)

H_NINE = Word('nine', 10, 0, False)
IN = Word('in', 10, 1, False)
OCLOCK = Word('oclock', 10, 6, False)
CLOCK = Word('clock', 10, 7, False)
LO = Word('lo', 10, 8, False)
LOCK = Word('lock', 10, 8, False)

H_ELEVEN = Word('eleven', 5, 0, True)
EVE_1 = Word('eve', 7, 0, True)
EVEN_1 = Word('even', 7, 0, True)

TAW = Word('taw', 0, 1, True)
AW = Word('aw', 1, 1, True)
OF = Word('of', 5, 1, True)
SI_1 = Word('si', 9, 1, True)

SEA = Word('sea', 1, 2, True)
NO = Word('no', 5, 2, True)
NOG = Word('nog', 5, 2, True)

UH = Word('uh', 6, 3, True)

SAT_1 = Word('sat', 0, 4, True)
AT_2 = Word('at', 1, 4, True)
YE_1 = Word('ye', 8, 4, True)

PYE_1 = Word('pye', 1, 5, True)
YE_2 = Word('ye', 2, 5, True)
YET_1 = Word('yet', 2, 5, True)

RHO = Word('rho', 3, 6, True)
HO = Word('ho', 4, 6, True)
OUT = Word('out', 7, 6, True)
TO_1 = Word('to', 9, 6, True)

PA_2 = Word('pa', 3, 8, True)
AH = Word('ah', 4, 8, True)
HE = Word('he', 5, 8, True)

TEA = Word('tea', 1, 9, True)
LO_1 = Word('lo', 9, 9, True)

EAST = Word('east', 1, 10, True)
AS_3 = Word('as', 2, 10, True)

TO_2 = Word('to', 3, 11, True)
TOE = Word('toe', 3, 11, True)


BIRTHDAYS = {
    BirthDate(1, 31): DOUG,
    BirthDate(4, 22): PATY,
    BirthDate(4, 1): LUCAS,
}

SPECIAL_BIRTHDAY = None
