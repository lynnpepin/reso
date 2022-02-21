'''pallete.py

This represents the twelve hues (RYGCBM, OLTSPV) across the two tones (saturated
and dark). The two other tones (light, unsaturated) are 'reserved' by convention
but not represented here.

We use capital letters and lowercase letters to refer to saturated and dark,
respectively. (e.g. pR = ord('R'), corresponding to '#ff0000', and
pr = ord('r'), corresponding to '#800000'.

This code provides useful enums, etc. With no imports, an
'import palette from *' should be fine. (Note that 'from package import *' is
usually a bad idea!)

If you want to import all the enums from this namespace and want to avoid *,
but you *also* don't want to write 'palette.pR' (because it's so long!)
then here are some easy copy-pastes for you:

from palette import pR, pY, pG, pC, pB, pM
from palette import pO, pL, pT, pS, pP, pV
from palette import pr, py, pg, pc, pb, pm
from palette import po, pl, pt, ps, pp, pv
from palette import get, resel_to_rgb, rgb_to_resel

'''

# palette.py
# These represent the twelve hues, across two tones (saturated, dark) from the palette in README.md
# By convention, 

# Palette stuff below!
# These are useful enums for colors in our palette.
# Here, we assign enums to match meaningful characters rather than arbitrary ints.
# (where 'meaningful character' is taken from enums.)

# These letters correspond to RYGCBM OLTSPV
# (Red, Yellow, Green, Cyan, Blue, Magenta; Orange, Lime, Teal, Sapphire, Purple, Violet)

pO = ord('O')   # 79    # On orange wire
po = ord('o')   # 111   # Off orange wire
pL = ord('L')   # 76    # On lime wire
pl = ord('l')   # 108   # Off lime wire
pT = ord('T')   # 84    # Xor node
pt = ord('t')   # 116   # And node
pS = ord('S')   # 83    # On sapphire wire
ps = ord('s')   # 115   # Off sapphire wire
pP = ord('P')   # 80    # Output node (from input/logic node to wire)
pp = ord('p')   # 112   # Input node (from wire to input/logic node)
pV = ord('V')   # 86
pv = ord('v')   # 118

pR = ord('R')   # 82
pr = ord('r')   # 114
pG = ord('G')   # 71
pg = ord('g')   # 103
pB = ord('B')   # 66
pb = ord('b')   # 98

pY = ord('Y')   # 89 
py = ord('y')   # 121
pC = ord('C')   # 67
pc = ord('c')   # 99
pM = ord('M')   # 77
pm = ord('m')   # 109


#_pal is just a helper; we loop over it to create our resel-rgb dicts.
# This represents the 12 hues, 'Saturated' and 'Dark'
_pal = [
    (pR, (255,0,0)),
    (pr, (128,0,0)),
    (pG, (0,255,0)),
    (pg, (0,128,0)),
    (pB, (0,0,255)),
    (pb, (0,0,128)),
    (pY, (255,255,0)),
    (py, (128,128,0)),
    (pC, (0,255,255)),
    (pc, (0,128,128)), 
    (pM, (255,0,255)),
    (pm, (128,0,128)),
    (pO, (255,128,0)),
    (po, (128,64,0)),
    (pL, (128,255,0)),
    (pl, (64,128,0)),
    (pT, (0,255,128)),
    (pt, (0,128,64)),
    (pS, (0,128,255)),
    (ps, (0,64,128)),
    (pP, (128,0,255)),
    (pp, (64,0,128)),
    (pV, (255,0,128)),
    (pv, (128,0,64)),
]

# We implement a cheap bidict here
resel_to_rgb = dict()
rgb_to_resel = dict()

for resel, rgb in _pal:
    rgb_to_resel[rgb] = resel
    resel_to_rgb[resel] = rgb

# And we implement a cheap defaultdict with this function
def get(dd, kk, default=0):
    """Get dd[kk], or return default if kk is not in dd.keys()
    
    :param dd: Dictionary
    :type dd: dict
    :param kk: Any hashable key
    :type kk: object
    :param default: The default value to return if kk is not a valid key
    :type default: object (anything!)
    
    :return: dd[kk], or 'default' if kk is not in dd.keys
    :rtype: object (anything!)
    """
    if kk in dd.keys():
        return dd[kk]
    else:
        return default

