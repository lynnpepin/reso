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
            return class_dict[value]
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

    :returns: todo
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
    """
    TODO -- document this, the init function, and clean up the comments

    Given an image, the goal is to identify contiguous regions of the same color
    pixel, where 'contiguity' is defined per-color.

    A small glossary:
     - Pixel: The basic element used in the region-mapper. Each pixel has colors
        defined as 3 ints (e.g. such as (255,0,127)) and an (x,y) coordinate.
     - Coordinate: Or pixel index, i.e. the (x,y) coordinate that defines a
        unique location in an image.
     - Class: An integer associated with the color of a pixel.
        E.g. One might have {(255,0,0) : 1, (0, 255, 0) : 2, (0, 0, 255) : 3},
        i.e. associated red, green, and blue with integers 1, 2, and 3.
     - Contiguity: Contiguity is defined per-class. For example, red pixels might
        only be contiguous on orthogonal neighbors, while blue pixels might be
        contiguous on both orthogonal and diagonal neighbors.
        "Contiguity" is defined per-class for flexibility.
     - Region: A collection of pixels sharing the same class, defined by their
        'contiguity'. Every region has a unique integer 'region id'.
     - Region ID: A unique integer associated with each region after the
        region-mapping algorithm is finished.
     - Adjacency: A region that is next to another region. Adjacencies to regions
        are defined similarly to contiguities.


    :param image: A numpy array of integers (0-255) in shape (w, h, 3)
    :type image: numpy.ndarray
    :param class_dict: Dictionary mapping 3-tuples (pixel) to ints (class)
    :type class_dict: Dict
    :param contiguities: Dictionary of class int --> list of coordinates.
        (E.g. One might use 'ortho_map' here.)
    :type contiguities: Dict
    :param adjacencies: Dictionary of class int --> list of coordinates.
        (E.g. One might use 'ortho_map' here.)
    :type adjacencies: Dict
    :param sparse: If True, use a dictionary instead of an array to map pixels to regions.
        (This is useful if most of the pixels in the image don't correspond to
        a class.)
    :type sparse: Bool
    :param wrap: If True, region adjacencies wrap around the edge of the image.
        (Like a torus, or teleporting through the side of the screen like in Pacman.)
    :type wrap: Bool
    """
    def __init__(self,
                 image,                 # 2D Numpy Array
                 class_dict,            # Dict of (value) --> Int >= 1
                 contiguities   = {},   # Dict of class int --> map (like ortho_map)
                 adjacencies    = {},   # Dict of class int --> map (like ortho map)
                 sparse         = True,
                 wrap           = False):

        # TODO: Split this off into other functions!
        width, height = image.shape[:2]

        assert(len(image.shape) == 3 or len(image.shape) == 2), \
            "image should be np array shaped (width, height) or (width, height, number_of_channels_in_image)"

        # Create self._image, holding a 2D numpy array of class ints
        # I.e. Convert an rgb-image (w,h,3) to class-image (w,h)
        # todo: this can be vectorized !!!
        self._image = np.zeros((width, height))
        for ii in range(width):
            for jj in range(height):
                self._image[ii, jj] = _value_to_class(class_dict, image[ii,jj])

        # Mapping of pixel coordinates to region indices.
        # If Sparse, self._region_at_pixel this is a dict mapping (x, y) tuples to int
        # otherwise, self._region_at_pixel is an *array* mapping [x,y] to int
        # Where the 'int' is a unique integer mapping to the region
        # An ID of -1 means there is no region at this pixel
        self._regions = []
        if sparse:
            self._region_at_pixel = dict()
        else:
            self._region_at_pixel = np.zeros((width, height)) - 1

        # _regions_with_class:
        # E.g. _regions_with_class[2] = [1,3,4] # Regions 1, 3, and 4 are the ones with class 3
        # Basically, we also want a mapping of all regions that have a certain class.
        self._regions_with_class = dict()

        # The busy work!
        # 'Region' integer IDs are incremented from 0 up
        region = 0
        # if rec[x,y] == True, then this pixel has already been recorded.
        rec = np.zeros((width, height), dtype=np.bool)
        for x in range(width):
         for y in range(height):
                # Each pixel already has its classed assigned,
                # where 0 indicates no class
                region_class = self._image[x,y]
                if rec[x,y] == False and not region_class == 0:
                    # An unexplored region with a class!
                    # Let's explore it, and list all the pixels in it.
                    list_of_pixels_in_region = []

                    # Here, we fill up Fill up list_of_pixels_in_region using BFS
                    # contig_map is A list of what we consider "contigous" pixels.
                    contig_map = _class_to_map(nbhd_offsets = contiguities, value = region_class)
                    # pixels_under_consideration:
                    # Every pixel we are looking at but have not computed yet.
                    pixels_under_consideration = [(x,y)]
                    rec[x,y] = True

                    while len(pixels_under_consideration) > 0:
                        # Loop through all our pixels. (BFS starts here.)
                        # Takes the first element from pixels_under_consideration...
                        xi, yi = pixels_under_consideration.pop()
                        list_of_pixels_in_region.append((xi, yi)) # = [..., (x,y)]
                        self._region_at_pixel[xi, yi] = region
                        # For each adjacent pixel,
                        #     if it's the same class,
                        #     add it to the list of pixels we're going to explore
                        for xJ, yJ in _get_adjacent_pixels(
                            x=xi, y=yi, w=width, h=height, nbhd_map = contig_map, wrap = wrap
                        ):
                            if self._image[xJ, yJ] == region_class and rec[xJ, yJ] == False:
                                # if the pixel is inside the region of our origin pixel,
                                # and if it is not already recorded...
                                pixels_under_consideration.append((xJ, yJ))
                                rec[xJ, yJ] = True

                    # we're done! add to our regions our
                    # (region_class, pixel_pixel_pixel ...)
                    self._regions.append((region_class, list_of_pixels_in_region))

                    # Add to our mapping of class --> region ID
                    # (and create the entry for the class index first,
                    #  if this is our first time seeing it.)
                    if not (region_class) in self._regions_with_class.keys():
                        self._regions_with_class[region_class] = [region]
                    else:
                        self._regions_with_class[region_class].append(region)

                    # finally, increment our region index
                    region += 1

        # We did it, we mapped all our regions!
        # Now it's time to identify adjacent regions.
        #     self._adjacent_regions[region_id] provides a list of region_ids
        #     of adjacent regions, as defined by the 'adjacencies'
        #     associated with that class.
        self._adjacent_regions = [[] for _ in range(len(self._regions))]

        # ii is region id
        for ii, (region_class, list_of_pixels) in enumerate(self._regions):
            # nbhd_map = The list of pixel offsets of what this class considers its neighbours
            nbhd_map = _class_to_map(nbhd_offsets = adjacencies, value = region_class)

            # For every pixel in region ii,
            for xi, yi in list_of_pixels:
                # For every pixel adjacent to that pixel,
                for xJ, yJ in _get_adjacent_pixels(
                    x=xi, y=yi, w=width, h=height, nbhd_map=nbhd_map, wrap=wrap
                ):
                    # If the neighbour is a valid region (not empty)
                    if not self._image[xJ,yJ] == 0:
                        neighbour = self._region_at_pixel[xJ,yJ]
                        if not (neighbour == ii) and \
                            not neighbour in self._adjacent_regions[ii]:
                            # If the neighbour is not us
                            #    and it's not the same class as us
                            #    and if we didn't already consider this neighbour...
                            # (neighbour is the integer ID for that region...)
                            # Add that neighbour to our list of regions!
                            self._adjacent_regions[ii].append(neighbour)


    # Helper functions from here on.
    def region_at_pixel(self, x, y):
        """Returns the ID of the region at that pixel,
            or -1 if that region does not belong to a class.
        :param x: x-index of pixel contained in the Region Mapper
        :type x: Int
        :param y: y-index of pixel contained in the Region Mapper
        :type y: Int

        :returns: The class at pixel (x,y), or -1 if such a class does not exist.
        :rtype: Int
        """
        # todo: What was I thinking with this design?
        # What was I thinking in 2018?
        # If you see this, don't judge me~
        if self._image[x,y] == 0:
            return -1
        else:
            return self._region_at_pixel[x,y]


    def regions(self, region_id):
        """Given the ID of a region, return
        (class_number, list of pixels indices in that region),
        i.e. a list of (x,y) coordinates.

        E.g. regions(region_at_pixel(x=10,y=12)) will tell you (1) the type of
        region at (10,12), and (2) every other pixel at that region.

        :param region_id: Integer that maps to a region.
        :type region_id: Int

        :returns: Tuple of (class) and (list of pixel indices) in that region.
        :rtype: Tuple
        """
        return self._regions[region_id]


    def regions_with_class(self, class_number):
        """Given the number of a class, return all regions with that class.

        For a class with integer 3, return a list of all region indices
        that have that class index.

        To get a list of pixel indices for a given region index,

        :param class_number: The integer associated with a class.
        :type class_number: Integer

        :returns: List of region IDs that have a given class number.
        :rtype: List of int
        """
        return self._regions_with_class[class_number]

    def adjacent_regions(self,region_id):
        """ Given the ID of a region, return all regions adjacent to it
        (as defined by its entry in the adjacencies dictionary)

        :param region_id: The ID associated with a region of pixels.
        :type region_id: Int

        :returns: List of all region IDs of regions adjacent to a given region ID.
        :rtype: List of int (or empty list)
        """
        return self._adjacent_regions[region_id]
