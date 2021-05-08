# Reso
![Reso logo](./reso_logo.gif)

Reso is a low-level circuit design language and simulator, inspired by things like Redstone, Conway's Game of Life, and Wireworld.

**What is Reso?**

 * Reso is a digital logic circuit graphical programming language!
 * Reso is a digital logic circuit simulator.
 * Reso program outputs other Reso programs.
 * Reso is *not* a cellular automata, despite similarities.
 * Reso is *not* useful or good yet, but I hope you can still have fun with it.

An input program is a circuit described by a (bitmap) image. When a Reso program is ran through the Reso simulator, it outputs another valid Reso program! Things get interesting when you iterate this process.

While the simulator acts like a pure function, for performance reasons, it maintains state between iterations.

Because images are valid circuits, you can copy-and-paste smaller components to build up more complex circuits using your favorite image editor!

This implementation is (1) slow (it's in Python!) and (2) not-interactive (you can't edit circuits live!) I hope you can have fun with this despite those limitations. :)

## Installation

TODO -- Packages and Python version here.

Not how to Git Clone with depth. (This is because I included slides, etc.)

## Usage

This implementation of Reso supports command line usage. Input is a single image, and outputs are iterations of the Reso simulation of the circuit described in the first image.

### Command line

Here's an example: Load `~/helloworld.png`, *iterate* (`-n`) 12 times, and *save* (`-s`) the results to `~/hello_00.png`, `~/hello_01.png`, ... `~/hello_04.png`, printing information *verbosely* (`-v`) along the way:


```
python3 reso.py ~/helloworld.png -n 12 -s hello_ -v
```

If you only wanted to save the end result, add the "-o" flag, as such:

```
python3 reso.py ~/helloworld.png -n 12 -s hello_ -v -o
```

And here is the full command-line usage:

```
usage: reso.py load_location [--numiter NUMITER] [--save SAVE] [--outputlast] [--verbose]    

positional arguments:
  load_location         Location to load image from

other arguments:
  --save SAVE, -s SAVE  Prefix to save images to.
  --numiter ITERATE, -n ITERATE
                        iterate the reso board n times. Defaults to 1.
  --outputlast, -o      Only save the final iteration of the board.
  --verbose, -v         Print extra information; useful for debugging.

```

### Palette

The palette is an important part of Reso! You can define a circuit using an image. Any pixel with a color in this palette of eight colors has semantic meaning, any other color doesn't.


| Color          | Meaning               | Hex code       |
| ---            | ---                   | ---            |
| Bright orange  | Orange wire (on)      | ```#ff8000```  |
| Dark  orange   | Orange wire (off)     | ```#804000```  |
| Bright sapphire| Sapphire wire (on)    | ```#0080ff```  |
| Dark sapphire  | Sapphire wire (off)   | ```#004080```  |
| Bright lime    | Lime wire (on)        | ```#80ff00```  |
| Dark lime      | Lime wire (off)       | ```#408000```  |
| Bright purple  | Output (node to wire) | ```#8000ff```  |
| Dark purple    | Input (wire to node)  | ```#400080```  |
| Bright teal    | XOR logic node        | ```#00ff80```  |
| Dark teal      | AND logic node        | ```#008040```  |

For backwards compatibility with new functionality, we reserve a total of 48 colors. (This is by convention and is not enforced by the Reso simulator.)

*A brief description of how programs run:* **Wires** push their signals through **input nodes**. There are three different colors of wire (orange, sapphire, and lime). Input nodes pass these signals to **logic nodes** and **output nodes**. Logic nodes are used to calculate the 'AND' or 'XOR' of every input signal, and push these on to **output nodes**. The output nodes act as one big *OR* gate, pushing the new signals out to wires.

The colors of different wires don't have any significance. They exist to make it easier to wire in 2D space, and to make it easier to keep track of which wire is which.

Here's the full palette of colors that we consider "reserved". Other colors are 'whitespace', i.e. will not have any semantic significance.

| Hue               | Saturated (1) | Dark (2)      | Light (3)     | Unsaturated (4) |
| ---               | ---           | ---           | ---           | ---           |
| **Red (R)**       | ```#ff0000``` | ```#800000``` | ```#ff8080``` | ```#804040``` |
| **Yellow (Y)**    | ```#ffff00``` | ```#808000``` | ```#ffff80``` | ```#808040``` |
| **Green (G)**     | ```#00ff00``` | ```#008000``` | ```#80ff80``` | ```#408040``` |
| **Cyan (C)**      | ```#00ffff``` | ```#008080``` | ```#80ffff``` | ```#408080``` |
| **Blue (B)**      | ```#0000ff``` | ```#000080``` | ```#8080ff``` | ```#404080``` |
| **Magenta (M)**   | ```#ff00ff``` | ```#800080``` | ```#ff80ff``` | ```#804080``` |
| **Orange (O)**    | ```#ff8000``` | ```#804000``` | ```#ffc080``` | ```#806040``` |
| **Lime (L)**      | ```#80ff00``` | ```#408000``` | ```#c0ff80``` | ```#608040``` |
| **Teal (T)**      | ```#00ff80``` | ```#008040``` | ```#80ffc0``` | ```#408060``` |
| **Sapphire (S)**  | ```#0080ff``` | ```#004080``` | ```#80c0ff``` | ```#406080``` |
| **Purple (P)**    | ```#8000ff``` | ```#400080``` | ```#c080ff``` | ```#604080``` |
| **Violet (V)**    | ```#ff0080``` | ```#800040``` | ```#ff80c0``` | ```#804060``` |

(Note: Don't sample directly from your web-browser! They don't always render colors reliably.)

## Examples

The Reso logo is actually a complete circuit in-and-of itself! Here is a small gif that explains what's going on, animated at 1/4th the speed (that is, one update every 2000ms):

![This is Reso gif](./examples/reso_logo_explained.gif)

## Things to be done:

Despite all the tests and documentation, Reso is a proof-of-concept and there's a lot to be done before this could even be a little useful!

Here are some neat ideas:

**Flag to map to nearby colors:** I've been having a weird issue with some versions of The GIMP, where colors are saved or picked incorrectly. Reso requires precise colors (e.g. `#ff8000` is a valid color but `#ff8800` is not.) Perhaps a flag to consider only the ~4 or so most-significant-bits per pixel, or to map colors within a certain range to their nearest one in the palette, would be useful?


**Export to GIF option:** Self explanatory! No more fiddling with GIMP or ffmpeg.

**Transferrable compiled graphs:** Reso is really a graph computation model of a logical circuit, and images are a way to define that graph. I want to better decouple that model, and make this a repository a better reference implementation.

Specifically, we consider pixels to represent logical "resels" which can also be represented textually, and regions of resels represent elements, which are represented internally as a graph implemented with Python dictionaries. But this graph isn't a standard, so a compiled graph can't be transferred between implementations.

**GUI and interactivity:** Some kind of GUI would be nifty too, rather than requiring expertise in some external graphical application. An interactive, Javascript webpage would make this a lot easier to mess around with, huh?

**Speed:** This is also really slow. Might reimplement in Rust when I get around to learning it!


**Port to a faster language:** Porting this to a faster language would be great. I think Rust would be fun (both because I want to learn it, and because there's some "Web Assembly" thing that makes me think it's easier to put Rust in the web than, say, C or C++.) 



## See Also

Here are a list of similar projects that I am aware of. Please make an issue or PR if you have something else to share!

 * Several sandbox videogames which have turing-complete circuit languages that empower the player to automate their world:
    * Minecraft's *Redstone* was the primary inspiration for this.
    * Terraria (Minecraft's 2D analogue) has a similar logic-gate wiring mechanism.
    * Hempuli is one of my favorite game devs, and seeing their development on [Baba Is You](https://en.wikipedia.org/wiki/Baba_Is_You) kept my brain on the right track for this.
    * Various other open-world sandbox games: Factorio, No Man's Sky, Dwarf Fortress, and others!
 * [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) -- A Turing-complete zero-player-game. By far the most popular cellular automata. Rest in Peace John Conway.
 * [Wireworld](https://en.wikipedia.org/wiki/Wireworld) -- Another cellular automata in which it is easy to implement logic circuits.
 * [Brian's Brain](https://en.wikipedia.org/wiki/Brian%27s_Brain) -- A cellular automaton similar to the previous.
 * [Bitmap Logic Simulator](https://realhet.wordpress.com/2015/09/02/bitmap-logic-simulator/) -- I'm not sure how this works, but check it out! It's a similar idea.
