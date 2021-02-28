# Reso
![Reso logo](https://gitlab.com/lynnpepin/reso/-/raw/master/reso_logo.gif)

Reso is a low-level circuit design language, kind of like Redstone or Wireworld. You can describe a graph using an image.

## Usage

This implementation of Reso supports command line usage. Input is a single image, and outputs are iterations of the Reso simulation of the circuit described in the first image.


### Command line

Here's an example: Load ~/helloworld.png, iterate 12 times, and save the results to ~/hello_xx.png. "-v" means "Verbose".

```
python3 reso.py ~/helloworld.png -i 12 -s hello_ -v
```

If you only wanted to save the end result, add the "-o" flag, as such:

```
python3 reso.py ~/helloworld.png -i 12 -s hello_ -v -o
```

Full CLI usage:

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

For backwards compatibility, we reserve a total of 48 colors.

**Wires** push their signals through **input nodes**. Input nodes pass these signals to **logic nodes** and **output nodes**. Logic nodes are used to calculate the 'AND' or 'XOR' of every input signal, and push these on to **output nodes**. The output nodes act as one big *OR* gate, pushing the new signals out to wires.

Black and white (`#000` and `#fff`, respectively) are the only safe 'whitespace' colors. These will never have any semantic meaning. Any other color may be reserved at any time.

Here's that full palette:

| Hue             | Saturated (1)    | Dark (2)  | Light (3)     | Unsaturated (4)   |
| ---             | ---              | ---       | ---           | ---               |
| **Red (R)**     | ```#f00```       | ```#800```| ```#f88```    | ```#844```        |
| **Yellow (Y)**  | ```#ff0```       | ```#880```| ```#ff8```    | ```#884```        |
| **Green (G)**   | ```#0f0```       | ```#080```| ```#8f8```    | ```#484```        |
| **Cyan (C)**    | ```#0ff```       | ```#088```| ```#8ff```    | ```#488```        |
| **Blue (B)**    | ```#00f```       | ```#008```| ```#88f```    | ```#448```        |
| **Magenta (M)** | ```#f0f```       | ```#808```| ```#f8f```    | ```#848```        |
| **Orange (O)**    | ```#f80```       | ```#840```| ```#fc8```    | ```#864```        |
| **Lime (L)**      | ```#8f0```       | ```#480```| ```#cf8```    | ```#684```        |
| **Teal (T)**      | ```#0f8```       | ```#084```| ```#8fc```    | ```#486```        |
| **Sapphire (S)**  | ```#08f```       | ```#048```| ```#8cf```    | ```#468```        |
| **Purple (P)**    | ```#80f```       | ```#408```| ```#c8f```    | ```#648```        |
| **Violet (V)**    | ```#f08```       | ```#804```| ```#f8c```    | ```#846```        |

## Examples

![This is Reso gif](https://github.com/tpepin96/reso/blob/master/examples/this_is_reso.gif)

## Things to be done:

Reso is really a graph computation model, and images are a way to define a graph. I want to better decouple that model, and make this a repository a reference implementation.

Some kind of GUI would be nifty too, rather than requiring expertise in some external graphical application.

This is also really slow. I want to add connectivity with Raspberry Pi GPIO pins in some manner so this can be used with real circuits, but first I want to make this faster! Maybe C or something.

## Architecture

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
