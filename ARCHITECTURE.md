Here's a brief description of the architecture of this program.


## Functional components

There are four functional components of Reso: The `regionmapper` tool which is used when compiling the graph, the `palette` code that defines some useful enumerations and mappings between pixels and 'resel' enums, the `resoboard` code that does the heavy lifting and logic of the simulator, and the `reso` code that wraps the logic for command line usage.

```
.
├── reso.py
│       Provides command-line access to Reso. Wraps the logic in resoboard.py
│
├── resoboard.py
│       Implements Reso as a "board". Example usage:
│           `board = ResoBoard(image); board.iterate(); img = board.get_image()`
│       Should be updated to use Pythonic Enums, proper docstrings, etc, but
│       the documentation is there!
│
│       The class ResoBoard does the heavy lifting here. If you want to use this
│       in another program, resoboard.ResoBoard is what you want to import.
│
├── palette.py
│       Provides enumeration of resels (twelve hues across two tones), and the
│       mapping between resels and RGB pixels.
│
└── regionmapper.py
        A tool that is used to map adjacent elements in a 2D array to a graph
        described as a dict. Used to map contiguous regions of pixels in a Reso
        program to nodes in a graph, and vice-versa.

```

## Testing components

This code contains unit tests as quick sanity-tests after code changes.

```
.
├── testing
│       Contains images used in `tests_for_regionmapper.py` and `tests_for_regionmapper.py`
│
├── tests_for_regionmapper.py
│       Exactly what it says on the tin. 'RegionMapper' was a separate project
│       with separate tests. 
│
└── tests.py
        Contains unit tests for this program
```


## Documentation components

And here are the non-code items we use :)

```
.
├── README.md
│       The first thing you should be reading.
│
├── ARCHITECTURE.md
│       This document! This describes roughly the project architecture.
│
└── doc
        This is garbage! But soon it will contain a more formal specification.

```

## Key concepts

Here are some low-level concepts to keep in mind if developing. (I should really make some diagrams here for the future... That is a todo for future me!)

1. **Pixels** are the individual components that make up an image. They are a 3-tuple of integers in the range `[0, 255]`.
2. **Images** are bitmaps, i.e. a grid of pixels. They have shape `(w, h, 3)`, where `w` and `h` are width and height, respectively.
3. **Resels** are simply enumerations. Pixels map directly to Resels, and vice versa!
4. A Reso **circuit** or **board** is a grid of Resels. It has a shape `(w, h)`.
    - There's no reason Reso can't be extended to grids of higher dimensions.
5. The **regions** of contiguous resels are identified using **RegionMapper**.
6. The **definition of contiguity** is defined on a per-class basis.
    - **Wires** are contiguous on all eight neighbors (diagonals and orthogonals.)
    - All other elements are contiguous on four neighbors (orthogonals).
    - This allows wires to cross over one another easily in 2D.
7. Definitions of **adjacency** between regions is defined similarly, but as of yet, all regions are adjacent only on orthogonals.
8. So, you can think of Reso as defining an **undirected graph** of elements.
    - This is why **input** and **output** nodes are necessary.
9. For efficiency, there is some 'hidden' state maintained during iteration. However, other than that, **all the state of a program is expressed in the wires on board.**

Here are some high-level concepts to understand if working with Reso:

1. Logical states are carried entirely in **wires,** as either on/off (or True/False).
2. Wires can cross over one another by diagonals. 
3. To input wires into a logical element, they must touch an **input** node.
4. There are two **logical** elements, **AND** and **XOR**.
5. For the outputs of logical elements to be accessible, they must be connected to an **output** node.
6. Finally, output nodes must be connected to **wires** for their values to be expressed.
7. For a logical **or**, simply connect wires to an input node, and connect that input node to an output node. No other logic element necessary.
8. For a logical **and**, connect a permanently-on wire to an **xor** node.
