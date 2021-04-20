import numpy as np

# todo:
# consider making this faster,
# per https://stackoverflow.com/questions/12321899/
# this is used in the 'compilation' step

# todo: this big docstring isn't necessary...

'''
Provides:

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


# Package constants, useful for defining neighborhoods.
# ortho_map defines an orthogonal neighborhood
# diag_map  defines a diagonal neighborhood
ortho_map = ((1,0),  (0,-1), (-1,0), (0,1))
diag_map  = ((1,-1), (-1,-1),(-1,1), (1,1))

def _value_to_class(class_dict, value):
    """ Map numpy array values using a dictionary.
    Convenience function for dictionaries that are keyed on tuples or integers.
    
    Used to map integers (numpy arrays of integers, shape (3,)) to integers.
    These integers enumerate the class that a pixel belongs to.
    
    :param class_dict: A mapping of tuples of integers (i.e. RGB pixels) to integers
    :type class_dict: dict
    :param value: The key used to index the class_dict.
    :type value: numpy.ndarray
    
    :raises ValueError: If the value has a shape with 2 or more axes.
    
    :returns: A mapping per class_dict, or 0 if that value is not available.
    :rtype: Anything
    
    >>> _value_to_class(
    ...     {(1,2,3) : 'some_class', 789 : 'another_class'},
    ...      np.array([1,2,3]))
    'some_class'

    >>> _value_to_class(
    ...     {(1,2,3) : 'some_class', 789 : 'another_class'},
    ...      np.array(789))
    'another_class'
    """
    # This was written when I was a baby. There's probably a better way to do
    # this using dictionaries.
    
    # E.g. If the shape of the array = (3,), e.g. np.array([255, 255, 255])
    if len(value.shape) == 1:
        if tuple(value) in class_dict.keys():
            return class_dict[tuple(value)]
        else:
            return 0
    # E.g. if the shape of the array = (), e.g. np.array(12345)
    elif len(value.shape) == 0:
        if value in class_dict.keys():
            return class_dict[a.reshape(-1)[0]]
        else:
            return 0
    else:
        raise ValueError


def _class_to_map(nbhd_offsets, value, default=ortho_map):
    """Index a dictionary 'nbhd_offsets' on 'value', returning 'default' if
    'value' is not a valid key.
    
    :param nbhd_offsets: 
    :type nbhd_offsets: dict
    :param value: The key used to index the dictionary 'nbhd_offsets'
    :type value: Any hashable object
    :param default: Default value to return if value is not in the keys, defaults
        to regionmapper.ortho_map
    :type default: Any object
    
    :returns:
    :rtype:
    """
    # e.g. _class_to_map(contiguities, 3)
    # where contiguities = { 3 : ortho_map + diag_map, ... }
    # returns contiguities[3]
    # This is used to identify the x and y offsets used in the contiguities and adjacencies
    
    # This was writen when I was a baby.
    # This can probably be replaced with collections.defaultdict... todo!
    
    if value in nbhd_offsets.keys():
        return nbhd_offsets[value]
    else:
        return default


def _get_adjacent_pixels(x, y, w, h, nbhd_map = ortho_map, wrap = False):
    """Returns a list of indices for adjacent pixels given a 'neighborhood map'.
    
    Where (x,y) is the central pixel index, this will return a list of adjacent
    pixels, as defined by the offsets in 'nbhd_map'.
    
    E.g. for (x,y) = (3,6) and nbhd_map = ((1,0),  (0,-1), (-1,0), (0,1)),
    this will return [(4, 6), (3, 5), (2, 6), (3, 7)].
    
    The 'wrap' parameter is only important if (x,y) are near the (w,h) boundaries.
    See the examples
    
    :param x: X-coordinate of the image
    :type x: Int
    :param y: Y-coordinate of the image
    :type y: Int
    :param w: Width of the image
    :type w: Int
    :param h: Height of the image
    :type h: Int
    :param nbhd_map: Iterable of tuple defining the "neighborhood". Defaults to
        region_mapper.ortho_map.
    :type nbhd_map:
    :param wrap: If True, wrap around the dictionary.
    :type wrap: Bool
    
    :returns: List of indices representing 'neighbors' of a pixel.
    :rtype: list of tuple of int
    
    >>> _get_adjacent_pixels(3,6,10,10)
    [(4, 6), (3, 5), (2, 6), (3, 7)]

    >>> _get_adjacent_pixels(x=3,y=6,w=4,h=7)
    [(3, 5), (2, 6)]

    >>> _get_adjacent_pixels(x=3,y=6,w=4,h=7, wrap=True)
    [(0, 6), (3, 5), (2, 6), (3, 0)]
    """
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
    """TODO
    
    :param image:
    :type image:
    :param class_dict:
    :type class_dict:
    :param contiguities:
    :type contiguities:
    :param adjacencies:
    :type adjacencies:
    :param sparse:
    :type sparse:
    :param wrap:
    :type wrap:
    """
    def __init__(self,
                 image,                 # 2D Numpy Array
                 class_dict,            # Dict of (value) --> Int >= 1
                 contiguities   = {},   # Dict of class int --> map (like ortho_map)
                 adjacencies    = {},   # Dict of class int --> map (like ortho map)
                 sparse         = True,
                 wrap           = False):
        
        width, height = image.shape[:2]
        
        assert(len(image.shape) == 3 or len(image.shape) == 2), \
            "image should be np array shaped (width, height) or (width, height, number_of_channels_in_image)"
        
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
                    # contig_map: A list of what we consider "contigous" pixels. e.g. ((1,0),(-1,0)) only considers those left and right of us.
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
        
        #ii is region id
        for ii, (region_class, list_of_pixels) in enumerate(self._regions):
            # nbhd_map = The list of pixel offsets of what this class considers its neighbours
            nbhd_map = _class_to_map(nbhd_offsets = adjacencies, value = region_class)
            
            # For every pixel in region ii,
            for xi, yi in list_of_pixels:
                # For every pixel adjacent to that pixel,
                for xJ, yJ in _get_adjacent_pixels(x=xi, y=yi, w=width, h=height, nbhd_map = nbhd_map, wrap = wrap):
                    # If the neighbour is a valid region (not empty),
                    if not self._image[xJ,yJ] == 0:
                        # (neighbour is an integer representing that region)
                        neighbour = self._region_at_pixel[xJ,yJ]
                        # If the neighbour is not us,
                        if not (neighbour == ii):                      
                            # If we didn't already consider this neighbour...
                            if not neighbour in self._adjacent_regions[ii]:
                                # Add that neighbour to our list of regions!
                                self._adjacent_regions[ii].append(neighbour)
        
        
    def region_at_pixel(self, x, y):
        """TODO:
        :param x:
        :type x:
        :param y:
        :type y:
        
        :returns:
        :rtype:
        """
        if self._image[x,y] == 0:
            return -1
        else:
            return self._region_at_pixel[x,y]
    
    def regions(self, region_id):
        """TODO:
        :param region_id:
        :type region_id:
        
        :returns:
        :rtype:
        """
        return self._regions[region_id]
    
    def regions_with_class(self, class_number):
        """TODO:
        :param class_number:
        :type class_number:
        
        :returns:
        :rtype:
        """
        return self._regions_with_class[class_number]
    
    def adjacent_regions(self,region_id):
        """TODO:
        :param class_number:
        :type class_number:
        
        :returns:
        :rtype:
        """
        return self._adjacent_regions[region_id]
