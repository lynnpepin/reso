# Reso
![Reso logo](./reso_logo.gif)

Reso is a graphical digital logic design language, inspired by Redstone and Wireworld. Made for fun and education, written using Python3.

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

Reso programs are RGB images defined by pixels of different colors. Different hues have different functional meanings.

There are currently 48 reserved colors (12 hues of 4 shades each). Of these, only 4 hues with 2 shades each have syntactic meaning:

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

**Wires** push their signals through **input nodes**. Input nodes pass these signals to **logic nodes** and **output nodes**. Logic nodes are used to calculate the 'AND' or 'XOR' of every input signal, and push these on to **output nodes**. The output nodes act as one big *OR* gate, pushing the new signals out to wires.

Black and white (#000 and #fff, respectively) are the only safe 'whitespace' colors. These will never have any semantic meaning. Any other color may be reserved at any time.

Each f, 8, 4, and 0 corresponds to hex 0xff, 0x80, 0x40, and 0x00, respectively.

Here is the full list of currently reserved colors. Of these, only R1, R2, C1, C2, B1, B2, and M1 and M2 are in use.

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

![This is Reso gif](./examples/this_is_reso.gif)

More examples to come!

## Things to be done:

Reso is very new. While Turing-complete, I might add some functionality in the reserved-colors someday. E.g. It'd be cool if the (currently unused) yellow-color could interact with, say, GPIO pins.

Being such a visual language, an MS-Paint-esque IDE of sorts would be a cool and fun project!

Finally, being colorblind would probably make using Reso more difficult. Customizable pallets could help alleviate that, and it shouldn't be too hard for me to implement.
