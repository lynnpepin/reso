from PIL import Image
import numpy as np
from regionmapper import ortho_map, diag_map, RegionMapper

# Enumerations for the colors!
# Numbers are arbitrary, but note: 0 implicitly means 'blank'; do not use!
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

#_pal will be looped over to create our dictionaries, _resel_to_rgb and _rgb_to_resel
_pal = [(pR, (255,0,0)),
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
        (pm, (128,0,128))]

_resel_to_rgb = dict()
_rgb_to_resel = dict()

for resel, rgb in _pal:
    _rgb_to_resel[rgb] = resel
    _resel_to_rgb[resel] = rgb

def _get(d, k, default=0):
    # Used to get a value from a dictionary,
    # with a default value if that key is not found. 
    if k in d.keys():
        return d[k]
    else:
        return default

# Wire and Node classes used below to hold data about the state.
class Wire:
    def __init__(self, regionid, state = False, next_state = False):
        self.regionid = regionid
        self.state = state
        self.next_state = next_state

class Node:
    # Node is everything that is not a wire
    def __init__(self, regionid, state = False):
        self.regionid = regionid
        self.state = state

class ResoBoard:
    def __init__(self,
                 image,
                 resel_to_rgb = _resel_to_rgb,
                 rgb_to_resel = _rgb_to_resel):
        # Initialization:
        #   Grabs the image, converts it to self._resel_map, 
        #   identifies the different regions (wires, inputs, etc.) in self._resel map,
        #   Sets up associations between those regions so that they can be quickly accessed,
        #   And initializes Wire and Node objects corresponding to each region.

        #### Loading the image and converting it to self._resel_map
        # 'image' can be a string or a numpy aray.
        # If 'image' is str, load it first.
        if isinstance(image, str):
            image = np.swapaxes(np.array(Image.open(image)), 0, 1)
        # else: assume image is of format (width, height, 3), indexed (x,y)
        
        # Convert our image to a resel_map (e.g. (255,0,0) -> pR
        width = image.shape[0]
        height = image.shape[1]
        self._resel_map = np.zeros((width, height))
        for ii in range(width):
            for jj in range(height):
                self._resel_map[ii,jj] = _get(rgb_to_resel, tuple(image[ii,jj]))
        
        #### Identify the different regions, giving us our self._RM (RegionMapper)
        # resel_map --> region mapping
        class_dict = { pR : pR, pr : pR,    # pR is also used to denote red wires
                       pB : pB, pb : pB,    # pB is also used to denote blue wires
                       pG:pG, pg:pg, pC:pC, pc:pc, pY:pY, py:py, pM:pM, pm:pm } # Every other color maps to itself
                       
        contiguities = { pR : ortho_map + diag_map, pB : ortho_map + diag_map} # Wires are diagonally contiguous
        
        self._RM = RegionMapper( self._resel_map,             
                                 class_dict = class_dict,           
                                 contiguities   = contiguities,
                                 sparse         = True)
        # self._RM provides:
        #   self._RM.region_at_pixel(x,y)
        #   self._RM.regions(id)
        #   self._RM.regions_with_class(class)
        #   self._RM.adjacent_regions(region_id)
        
        #### Set up a Wire()/Node() object for each region, lists of all such objects (self._red_wires, etc...), and the regionid -> Wire()/Node() list self._resel_objects
        #       It is redundant in space usage, but results in faster lookup times
        #       Cleanup: But we can just use self._RM.regions_with_class(PR), right? It'll be uglier but who cares
        
        self._resel_objects = [None]*len(self._RM._regions) # One entry for every region
        self._red_wires     = []
        self._blue_wires    = []
        self._inputs        = []
        self._outputs       = []
        self._ands          = []
        self._xors          = []
        
        for regionid, (classid, _) in enumerate(self._RM._regions):
            if classid == pR or classid == pB: # A wire!
                new_object = Wire(regionid)
                if classid == pR:
                    self._red_wires.append(new_object) # Add it to _red_wires
                else:
                    self._blue_wires.append(new_object) # Add it to _blue_wires
            else:                              # A node!
                new_object = Node(regionid)
                if classid == pm:
                    self._inputs.append(new_object)
                elif classid == pM:
                    self._outputs.append(new_object)
                elif classid == pC:
                    self._xors.append(new_object)
                elif classid == pc:
                    self._ands.append(new_object)
                elif classid in (pG, pg, pY, py):
                    pass
                else:
                    print("Unrecognized classid", classid)
                    raise ValueError
            
            self._resel_objects[regionid] = new_object
        
        # Turn on wires if they are on in the self._resel_map
        for wires in (self._red_wires, self._blue_wires): 
            for wire in wires:
                wire_is_on = False
                pixels_in_wire = self._RM.regions(wire.regionid)[1]
                for ii, jj in pixels_in_wire:
                    if self._resel_map[ii, jj] == pR or self._resel_map[ii,jj] == pB:
                        wire_is_on = True
                        break
                wire.state = wire_is_on

        #### Set up adjacency dictionaries. dict[region_id] -> Wire()/Node() object
        # _adj_inputs[]  for wire_id, 
        # _adj_xors[]    for all input cells
        # _adj_ands[]    for all input cells
        # _adj_outputs[] for all input cells and for all logic nodes (xors, ands)
        # _adj_wires[]   for all output cells
        
        '''
        self._adj_inputs = dict()
        for wire in self._red_wires + self._blue_wires:
            self.adj_inputs[wire.regionid] = []
            for adjacent_region in self._RM.adjacent_regions(wire.regionid):
                if self._RM.regions[0] == pm: # If it's an input,
                    # Get the 
                    self.adj_inputs[wire.regionid].append
        '''
        # Refine algorithm, update all the info we need for each element
    
        
        
