from PIL import Image
import numpy as np
from regionmapper import ortho_map, diag_map, RegionMapper

#### Palette stuff: RGB <--> 'resel' conversion
# Enumerations for each of the colors!
# Numbers are arbitrary, but note: 0 implicitly means 'blank'; do not use, and numbers must be unique.
pR = ord('R')   # 82    # On red wire
pr = ord('r')   # 114   # Off red wire
pG = ord('G')   # 71    # Unused
pg = ord('g')   # 103   # Unused
pB = ord('B')   # 66    # On blue wire
pb = ord('b')   # 98    # Off blue wire

pY = ord('Y')   # 89    # Unused
py = ord('y')   # 121   # Unused
pC = ord('C')   # 67    # XOR node
pc = ord('c')   # 99    # AND node
pM = ord('M')   # 77    # Output node (from input/logic node to wire)
pm = ord('m')   # 109   # Input node  (from wire to input/logic node)

#_pal is just a helper; we loop over it to create our resel-rgb dicts.
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

# Cheap implementation of a bidict with default values
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

#### Wire and Node classes used below to hold data about the state during iteration
class Wire:
    def __init__(self, regionid, state = False, next_state = False):
        self.regionid = regionid
        self.state = state
        self.next_state = next_state
        # State corresponds to the visual state of the wire between iterations
        # next_state is used only during iteration and remains false

class Node:
    # Node is everything that is not a wire
    def __init__(self, regionid, state = False):
        self.regionid = regionid
        self.state = state # Remains false between iterations
        # For 'and' nodes, state starts at False,
        # locks to -1 if connected to an off wire.


class ResoBoard:
    def __init__(self,
                 image,
                 resel_to_rgb = _resel_to_rgb,
                 rgb_to_resel = _rgb_to_resel):
        ##### Initialization:
        #   Grabs the image, converts it to self._resel_map, 
        #   identifies the different regions (wires, inputs, etc.) in self._resel map,
        #   Sets up associations between those regions so that they can be quickly accessed,
        #   And initializes Wire and Node objects corresponding to each region.
        
        #### Provides:
        # self._image       NP array (w, h, 3)
        # self._resel_map   NP array (w, h, resel values)
        # self._RM          Region mapper (where both on/off wires are considered the same class)
        # self._resel_objects
            # List of Wire() or Node() objects; indexed by arbitrary unique region ID (int)
        # self._red_wires, _blue_wires, _inputs, _outputs, _ands, _xors
            # Lists of Wire() (for *_wires) or Node() objects
            # Point to the same objects as in self._resel_objects
        # Adjacency dicts: Dictionaries mapped by region_id to a list of all adjacent Wire() or Node() objects
            # E.g. _adj_inputs[], a dictionary indexed by wire region id, returns a list of all inputs (pm) adjacent to that wire
            # We only need wire --> input, input --> xor/and/output, xor/and --> output, and output-->wire
            # self._adj_inputs[]  by wire_id, 
            # self._adj_xors[]    by input_id
            # self._adj_ands[]    by input id
            # self._adj_outputs[] by input_id, xor_id, or and_id
            # self._adj_wires[]   by output_id
        # Leftover arguments:
        # self._resel_to_rgb
        # self._rgb_to_resel

        #### Loading the image and converting it to self._resel_map
        # 'image' can be a string or a numpy aray.
        # If 'image' is str, load it first.
        if isinstance(image, str):
            image = np.swapaxes(np.array(Image.open(image)), 0, 1)[:,:,:3]
        # else: assume image is of format (width, height, 3), indexed (x,y)
        self._image = image
        
        # Convert our image to a resel_map (e.g. (255,0,0) becomes pR)
        width = self._image.shape[0]
        height = self._image.shape[1]
        self._resel_map = np.zeros((width, height))
        for ii in range(width):
            for jj in range(height):
                self._resel_map[ii,jj] = _get(rgb_to_resel, tuple(self._image[ii,jj]))
        
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
        # _adj_outputs[] for all input cells and all logic nodes
        # _adj_wires[]   for all output cells
        
        self._adj_inputs    = dict()
        self._adj_xors      = dict()
        self._adj_ands      = dict()
        self._adj_outputs   = dict()
        self._adj_wires     = dict()

        # Loop over the following:
        # For every region in _red_wires, create an entry in self._adj_xors[region]
        # for every *adjacent* region having a class in classids
        for from_list, to_dict, classids in \
            [((self._red_wires + self._blue_wires), self._adj_inputs, (pm,)),
             (self._inputs, self._adj_xors, (pC,)),
             (self._inputs, self._adj_ands, (pc,)),
             (self._inputs, self._adj_outputs, (pM,)),
             (self._xors, self._adj_outputs, (pM,)),
             (self._ands, self._adj_outputs, (pM,)),
             (self._outputs, self._adj_wires, (pR, pB))]:
             
             for resel in from_list:
                to_dict[resel.regionid] = []
                for adj_reg_id in self._RM.adjacent_regions(resel.regionid):
                    adj_reg_class = self._RM.regions(adj_reg_id)[0]
                    if adj_reg_class in classids:
                        to_dict[resel.regionid].append(self._resel_objects[adj_reg_id])
        
        #### Set up the self._rgb_to_resel, self._resel_to_rgb for later use:
        self._rgb_to_resel = rgb_to_resel
        self._resel_to_rgb = resel_to_rgb
    
    
    def _update(self, resel_map = False, image = True):
        # Update the values  in resel map and in the image
        # Use case: You ran iterate() and want to see the new image.
        if resel_map or image: # Only loop if we want to update something!
            for oncolor, offcolor, wires in ((pR, pr, self._red_wires), (pB, pb, self._blue_wires)):
                for wire in wires:
                    color = oncolor if wire.state else offcolor # Color to set the wire to
                    color_tuple = np.array(self._resel_to_rgb[color])
                    regionid = wire.regionid
                    pixel_list = self._RM.regions(regionid)[1]
                    for ii, jj in pixel_list:
                        if resel_map:
                            self._resel_map[ii,jj] = color
                        if image:
                            self._image[ii,jj] = color_tuple
                
    
    def get_resel_map(self):
        # Return a Numpy array representing the Reso board
        return self._resel_map
    
    def get_image(self):
        # Return the Numpy array containing the underlying image.
        # (Note: You may want to use np.swapaxes(_image, 0, 1))
        #   (It may be better to just do that here...)
        return self._image
    
    def iterate(self, update_resels = True, update_image = True):
        # Iterate the board, updating every Wire() object.
            # Also updates the resels if update_resels, and the image if update_image
        
        # For each wire,
        for wire in (self._red_wires + self._blue_wires):
            # For each input connected to that wire,
            for inputnode in self._adj_inputs[wire.regionid]:
                # Update the internal states of adjacent xor, and, outputs
                for xornode in self._adj_xors[inputnode.regionid]:
                    xornode.state = xornode.state ^ wire.state
                for andnode in self._adj_ands[inputnode.regionid]:
                    if not (andnode.state == -1):
                        if wire.state == False:
                            andnode.state = -1
                        else:
                            andnode.state = True
                for outnode in self._adj_outputs[inputnode.regionid]:
                    outnode.state = outnode.state or wire.state
        
        # For each logical element,
        for xornode in self._xors:
            for outnode in self._adj_outputs[xornode.regionid]:
                outnode.state = outnode.state or xornode.state
        
        for andnode in self._ands:
            if andnode.state == True:
                for outnode in self._adj_outputs[andnode.regionid]:
                    outnode.state = outnode.state or andnode.state
        
        # For each output,
        for outnode in self._outputs:
            # Update the next_state of each adjacent wire
            for wire in self._adj_wires[outnode.regionid]:
                 wire.next_state = wire.next_state or outnode.state
        
        # Finally, reset everything
        for wire in (self._red_wires + self._blue_wires):
            wire.state = wire.next_state
            wire.next_state = False

        for node in self._xors + self._ands + self._inputs + self._outputs:
            node.state = False
        
        # By default, also updates the resels and the image
        self._update(update_resels, update_image)
