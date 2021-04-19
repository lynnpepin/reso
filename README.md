# Reso
![Reso logo](https://gitlab.com/lynnpepin/reso/-/raw/master/reso_logo.gif)

Reso is a low-level circuit design language and simulator, inspired by Redstone and Wireworld.

An input program is a circuit (perhaps described using an image). When a Reso program is ran through the Reso simulator, it outputs another valid Reso program! Things get interesting when you iterate this process.

While the simulator acts like a pure function, for performance reasons, it maintains state between iterations.

Because images are valid circuits, you can copy-and-paste smaller components to build up more complex circuits using your favorite image editor!

This implementation is (1) slow (it's in Python!) and (2) not-interactive (you can't edit circuits live!) I hope you can have fun with this despite those limitations. :)

## Usage

This implementation of Reso supports command line usage. Input is a single image, and outputs are iterations of the Reso simulation of the circuit described in the first image.

### Command line

Here's an example: Load `~/helloworld.png`, *iterate* (`-i`) 12 times, and *save* (`-s`) the results to `~/hello_00.png`, `~/hello_01.png`, ... `~/hello_04.png`, printing information *verbosely* (`-v`) along the way:


```
python3 reso.py ~/helloworld.png -i 12 -s hello_ -v
```

If you only wanted to save the end result, add the "-o" flag, as such:

```
python3 reso.py ~/helloworld.png -i 12 -s hello_ -v -o
```

And here is the full command-line usage:

```
usage: reso.py load_location [--iterate ITERATE] [--save SAVE] [--outputlast] [--verbose]    

positional arguments:
  load_location         Location to load image from

other arguments:
  --save SAVE, -s SAVE  Prefix to save images to.
  --iterate ITERATE, -i ITERATE
                        iterate the reso board n times. Defaults to 1.
  --outputlast, -o      Only save the final iteration of the board.
  --verbose, -v         Print extra information; useful for debugging.

```

### Palette

The palette is an important part of Reso! You can define a circuit using an image. Any pixel with a color in this palette of eight colors has semantic meaning, any other color doesn't.


| Color          | Meaning               | Hex code       |
| ---            | ---                   | ---            |
| Bright red     | Red wire (on)         | ```#ff0000```  |
| Dark red       | Red wire (off)        | ```#800000```  |
| Bright blue    | Blue wire (on)        | ```#0000ff```  |
| Dark blue      | Blue wire (off)       | ```#000080```  |
| Bright magenta | Output (node to wire) | ```#ff00ff```  |
| Dark magenta   | Input (wire to node)  | ```#800080```  |
| Bright cyan    | XOR logic node        | ```#00ffff```  |
| Dark cyan      | AND logic node        | ```#008080```  |

For backwards compatibility with new functionality, we reserve a total of 48 colors. (This is by convention and is not enforced by the Reso simulator.)

**Wires** push their signals through **input nodes**. Input nodes pass these signals to **logic nodes** and **output nodes**. Logic nodes are used to calculate the 'AND' or 'XOR' of every input signal, and push these on to **output nodes**. The output nodes act as one big *OR* gate, pushing the new signals out to wires.

Black and white (`#000` and `#fff`, respectively) are the only safe 'whitespace' colors. These will never have any semantic meaning. Any other color may be reserved at any time.

Here's that full palette:

| Hue               | Saturated (1)       | Dark (2)     | Light (3)        | Unsaturated (4)     |
| ---               | ---                 | ---          | ---              | ---                 |
| **Red (R)**       | ```#ff0000```       | ```#990000```| ```#ff9999```    | ```#994444```       |
| **Yellow (Y)**    | ```#ffff00```       | ```#999900```| ```#ffff99```    | ```#999944```       |
| **Green (G)**     | ```#00ff00```       | ```#009900```| ```#99ff99```    | ```#449944```       |
| **Cyan (C)**      | ```#00ffff```       | ```#009999```| ```#99ffff```    | ```#449999```       |
| **Blue (B)**      | ```#0000ff```       | ```#000099```| ```#9999ff```    | ```#444499```       |
| **Magenta (M)**   | ```#ff00ff```       | ```#990099```| ```#ff99ff```    | ```#994499```       |
| **Orange (O)**    | ```#ff9900```       | ```#994400```| ```#ffcc99```    | ```#996644```       |
| **Lime (L)**      | ```#99ff00```       | ```#449900```| ```#ccff99```    | ```#669944```       |
| **Teal (T)**      | ```#00ff99```       | ```#009944```| ```#99ffcc```    | ```#449966```       |
| **Sapphire (S)**  | ```#0099ff```       | ```#004499```| ```#99ccff```    | ```#446699```       |
| **Purple (P)**    | ```#9900ff```       | ```#440099```| ```#cc99ff```    | ```#664499```       |
| **Violet (V)**    | ```#ff0099```       | ```#990044```| ```#ff99cc```    | ```#994466```       |

(Note: Don't sample directly from your web-browser! They don't always render colors reliably.)

## Examples

![This is Reso gif](https://github.com/tpepin96/reso/blob/master/examples/this_is_reso.gif)

## Things to be done:

**Transferrable compiled graphs:** Reso is really a graph computation model of a logical circuit, and images are a way to define that graph. I want to better decouple that model, and make this a repository a better reference implementation.

Specifically, we consider pixels to represent logical "resels" which can also be represented textually, and regions of resels represent elements, which are represented internally as a graph implemented with Python dictionaries. But this graph isn't a standard, so a compiled graph can't be transferred between implementations.

**GUI and interactivity:** Some kind of GUI would be nifty too, rather than requiring expertise in some external graphical application. An interactive, Javascript webpage would make this a lot easier to mess around with, huh?

**Speed:** This is also really slow. Might reimplement in Rust when I get around to learning it!

**Palette:** The first six hues (Red, Yellow, Green, Cyan, Blue, Magenta) have roughly unequal brightness values while the second six hues (Orange, Lime, Teal, Sapphire, Purple, Violet) are more appealingly equal. I want to change the palette to use these latter halves, with wires represented by Orange and Sapphire, logic represented by Teal, and inputs represented by Violet.


## Architecture

I want to make a proper `ARCHITECTURE.md` eventually for this. :) But for now, check this section out.

```
.
├── doc
│       Contains a (WIP) whitepaper meant to describe this more formally.
│
├── README.md
├── regionmapper.py
│       A tool that is used to map adjacent elements in a 2D array to a graph
│       described as a dict. Used to map contiguous regions of pixels in a Reso
│       program to nodes in a graph, and vice-versa.
├── resoboard.py
│       Implements Reso as a "board". Example usage:
│           `board = ResoBoard(image); board.iterate(); img = board.get_image()`
│       Should be updated to use Pythonic Enums, proper docstrings, etc, but
│       the documentation is there!
│
│       The class ResoBoard does the heavy lifting here. If you want to use this
│       in another program, resoboard.ResoBoard is what you want to import.
│
├── reso.py
│       Provides command-line access to Reso.
├── testing
│       Contains images used in tests.py
└── tests.py
        Contains unit tests for this program

```
