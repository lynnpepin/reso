# Reso

Reso is a graphical circuit-design programming language and almost a cellular automata. For fun and education, written using Python3.

Inputs are PNG images with a simple palette; outputs are also PNG images.

## Usage

Reso only supports command line usage or calling from the ResoBoard class. Inputs and outputs are in the form of images.

### Command line

Here's an example. Load ~/helloworld.png, iterate 12 times, and save the results to ~/hello_xx.png. "-v" means "Verbose".

```
python3 reso.py ~/helloworld.png -i 12 -s hello_ -v
```

If you only wanted to save the end result, add the "-o" flag, as such:

```
python3 reso.py ~/helloworld.png -i 12 -s hello_ -v -o
```

Full usage:

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

Reso programs are RGB images defined by pixels of different colors. Different hues have different functional meanings.

There are currently 48 reserved colors (12 hues of 4 shades each). Of these, only 4 hues with 2 shades each have syntactic meaning:

| Color                 | Meaning               |
| ---                   | ---                   |
| Bright red (#f00)     | Red wire (on)         |
| Dark red (#800)       | Red wire (off)        |
| Bright blue (#00f)    | Blue wire (on)        |
| Dark blue (#008)      | Blue wire (off)       |
| Bright magenta (#f0f) | Output (node to wire) |
| 

Despite the 24 reserved colors, this may be expanded. Black and White are considered the only safe 'whitespace' colors. 

Here is the full list of reserved colors. Of these, only R1, R2, C1, C2, B1, B2, and M1 and M2 are in use.

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

Check back later for some examples of running Reso programs!

## Things to be done:

Reso is very new. While Turing-complete, plans exist to add functionality to the yet-unused resrved palette. E.g. Perhaps the unused yellow-color could interact with RaspberryPi GPIO pins.

Being such a visual language, an MS-Paint-esque IDE of sorts would be useful!

Finally, being colorblind can make using Reso more difficult. If there is demand for it, customizable pallettes are possible.
