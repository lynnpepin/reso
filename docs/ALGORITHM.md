# Reso algorithm (WIP page)

This page is a WIP for 0.0.x. This is a high-level overview of it all.

This page visually describes the algorithm used to compile Reso circuits and calculate their output.

Let's use a simple example circuit which evaluates the expression `(A and B) or (A xor B)`. The Reso circuit is as follows, with corresponding logic gate diagram:

TODO

Let's see how this is compiled by Reso!

## 1. Region mapping

The first stage of compilation is finding contiguous regions of elements.

Reso programs start out as RGB images. Each pixel can take on any of the possible 16777216 colors, but only 10 colors are semantically significant:

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

Input, output, AND and XOR elements are contiguous only on four orthoganal neighbors.

TODO

Wires, however, are contiguous on orthoganal and diagonal neighbors, for eight total. On-wires and off-wires are considered the same for region mapping:

TODO

So, we identify the following regions of adjacent pixels in our example circuit:

TODO

## 2. 
