import numpy as np

'''
Public-facing variables:

ortho_map = ((1,0),  (0,-1), (-1,0), (0,1))
diag_map  = ((1,-1), (-1,-1),(-1,1), (1,1))
    
    These are used to calculate adjacent pixels.
    Useful for the contiguities and adjacencies dictionaries for RegionMapper

RegionMapper(image,
             class_dict,
             contiguities = {},
             adjacencies = {},
             sparse = True,
             wrap = False)
    Parameters:
        image: A Numpy array of shape (width, height, n_channels)
            E.g. image[x,y] = [255, 0, 0]
                Note: Axis 0 and 1 should represent x and y, respectively!
                If they're wrong, use np.swapaxes(picture, 0, 1)            
        class_dict: A dictionary mapping tuple of size n_channels --> int
            E.g. class_dict = { (255,0,0):1, (0,255,0):2, (0,0,255):3 }
                # Red is class 1, green is class 2, blue is class 3
        contiguities: A dictionary mapping classes to what they consider 'contiguous regions'
            E.g. contiguities = { 1 : ortho_map + diag_map, 3: diag_map }
                # Red regions are contiguous if they touch orthogonally or diagonally
                # Blue regions are contiguous only if they touch diagonally
                # Green regions are orthogonally contiguous (default)
        adjacencies: Same format as contiguities. Defines what is considered a neighbour for a given class.
            E.g. adjacencies = {} means (by default) regions of any class will only consider
            other regions to be its neighbour if a pixel of that region is orthogonally adjacent
        sparse: Boolean. Set True if most of the pixels in the image do not belong to a given class.
        wrap: Boolean. If True, the image is considered a torus. The top edge is adjacent to the bottom edge,
            and the left edge is adjacent to the right edge.
    
    Provides:
    RegionMapper.region_at_pixel(x,y):
        Returns the ID of the region at that pixel, or
        -1 if that region does not belong to a class.
    RegionMapper.regions(region_id):
        Given the ID of a region, return (class_number, list of pixels in that region)
    RegionMapper.regions_with_class(class_number):
        Given the number of a class, return all regions with that class.
    RegionMapper.adjacent_regions(region_id):
        Given the ID of a region, return all regions adjacent to it (as defined by
        its entry in the adjacencies dictionary)
'''


# Common maps
# E.g. ortho_map defines an orthogonal neighborhood
ortho_map = ((1,0),  (0,-1), (-1,0), (0,1))
diag_map  = ((1,-1), (-1,-1),(-1,1), (1,1))

def _value_to_class(class_dict, value):
    if len(value.shape) == 1: # Is tuple-able
        if tuple(value) in class_dict.keys():
            return class_dict[tuple(value)]
        else:
            return 0
    elif len(value.shape) == 0: # Is just an int
        if value in class_dict.keys():
            return class_dict[value]
        else: return 0
    else:
        raise ValueError


def _class_to_map(nbhd_offsets, value, default=ortho_map):
    # e.g. _class_to_map(contiguities, 3)
    # where contiguities = { 3 : ortho_map + diag_map, ... }
    # returns contiguities[3]
    # This is used to identify the x and y offsets used in the contiguities and adjacencies
    if value in nbhd_offsets.keys():
        return nbhd_offsets[value]
    else:
        return default


def _get_adjacent_pixels(x, y, w, h, nbhd_map = ortho_map, wrap = False):
    # Returns only valid pixels; order of pixels not guaranteed
    # E.g. adjacent_pixels(0,0,3,4) = [(1,0),(0,3),(0,2),(0,1)]
    # E.g. adjacent_pixles(0,0,0,0, wrap=False) = [(1,0),(0,1)]
    adj_pixels = []
    for offset_x, offset_y in nbhd_map:
        if wrap:
            adj_pixels.append(((x+offset_x) % w, (y+offset_y) % h))
        else:
            if 0 <= x + offset_x < w and 0 <= y + offset_y < h:
                adj_pixels.append((x+offset_x, y + offset_y))
    
    return adj_pixels


class RegionMapper:
    def __init__(self,
                 image,                 # 2D Numpy Array
                 class_dict,            # Dict of (value) --> Int >= 1
                 contiguities   = {},   # Dict of class int --> map (like ortho_map)
                 adjacencies    = {},   # Dict of class int --> map (like ortho map)
                 sparse         = True,
                 wrap           = False):
        
        width, height = image.shape[:2]
        
        assert(len(image.shape) == 3 or len(image.shape) == 2), "image should be np array shaped (width, height) or (width, height, number_of_channels_in_image)"
        
        ####
        # Create self._image:
        ####
        # rgb-image (w,h,3) to class-image (w,h)
        self._image = np.zeros((width, height))
        for ii in range(width):
         for jj in range(height):
            self._image[ii, jj] = _value_to_class(class_dict, image[ii,jj])
        
        ####
        # Cut up into regions:
        ####
        ## Some variables we will be using:
        # A list of all regions
        self._regions = []
        if sparse:
            self._region_at_pixel = dict()
        else:
            self._region_at_pixel = np.zeros((width, height)) - 1
        # _regions_with_class:
        # E.g. _regions_with_class[2] = [1,4,3] # Regions 1, 4, and 3 the ones with class 3
        self._regions_with_class = dict()
        
        ##The busy work:
        # Region number we are working with
        region = 0
        # A map of all pixels that have or have not been recorded
        rec = np.zeros((width, height), dtype=np.bool)
        for x in range(width):
         for y in range(height):
            if rec[x,y] == False:
                # An unexplored region! Time to check it out!
                region_class = self._image[x,y] # Let's get its class number, make sure it's not empty
                if not region_class == 0:
                    list_of_pixels_in_region = []   # ... and set up a list to fill with all these pixels!
                    
                    ##Fill up list_of_pixels_in_region using BFS
                    # contig_map: A list of what we consider "contigous" pixels. e.g. ((1,0),(-1,0)) only considers those left-right of us.
                    contig_map = _class_to_map(nbhd_offsets = contiguities, value = region_class)
                    # pixels_under_consideration: Every pixel we are looking at but have not computed yet.
                    pixels_under_consideration = [(x,y)]
                    rec[x,y] = True
                    #print("Hey!", x, y, region_class)
                    while len(pixels_under_consideration) > 0:
                        
                        #print(pixels_under_consideration)
                        #input()
                        xi, yi = pixels_under_consideration.pop() # Takes the first element from pixels_under_consideration
                        list_of_pixels_in_region.append((xi, yi)) # = [..., (x,y)]
                        self._region_at_pixel[xi, yi] = region
                        # For each adjacent pixel, if it's the same class, add it to the list of pixels we're going to explore
                        for xJ, yJ in _get_adjacent_pixels(x=xi, y=yi, w=width, h=height, nbhd_map = contig_map, wrap = wrap):
                           if self._image[xJ, yJ] == region_class and rec[xJ, yJ] == False:
                               pixels_under_consideration.append((xJ, yJ))
                               rec[xJ, yJ] = True
                    
                    self._regions.append((region_class, list_of_pixels_in_region))
                    
                    if not (region_class) in self._regions_with_class.keys():
                        self._regions_with_class[region_class] = [region]
                    else:
                        self._regions_with_class[region_class].append(region)
                    
                    region += 1
        
        ####
        # Identify adjacent regions
        ####
        self._adjacent_regions = [[] for _ in range(len(self._regions))]
        
        for ii, (region_class, list_of_pixels) in enumerate(self._regions): #ii is region id
            # nbhd_map = The list of pixel offsets of what this class considers its neighbours
            nbhd_map = _class_to_map(nbhd_offsets = adjacencies, value = region_class)
            
            for xi, yi in list_of_pixels:                               # For every pixel in region ii,
                for xJ, yJ in _get_adjacent_pixels(x=xi, y=yi, w=width, h=height, nbhd_map = nbhd_map, wrap = wrap): # For every pixel next to it,
                    if not self._image[xJ,yJ] == 0:                     # If the neighbour is a valid region (not empty) and
                        neighbour = self._region_at_pixel[xJ,yJ]        # (neighbour = The region number of the neighbour)
                        if not (neighbour == ii):                       # If the neighbour is not us,
                            if not neighbour in self._adjacent_regions[ii]: # and if we didn't already consider this neighbour...
                                self._adjacent_regions[ii].append(neighbour)# Add neighbour!
        
        
    def region_at_pixel(self,x,y):
        if self._image[x,y] == 0:
            return -1
        else:
            return self._region_at_pixel[x,y]
    
    def regions(self, region_id):
        return self._regions[region_id]
    
    def regions_with_class(self,class_number):
        return self._regions_with_class[class_number]
    
    def adjacent_regions(self,region_id):
        return self._adjacent_regions[region_id]
