# Reso whitepaper

Reso is a graphical circuit design language which compiles to a graph. A program is defined by a bitmap image, and basic graphics programs such as Paint or GIMP are appropriate editors for Reso programs. It is inspired by Minecraft's *redstone*.

Despite appearances, Reso is not a cellular automata. I don't think it's technically a graph automata either.

The goal of Reso is to be an interesting and fun circuit editor. Efficiency for real-world applications is not a goal, but an optimized and interactive rewrite with web technologies would go a far way into making this "fun".

## Semi-Formal Description

> **Summary:** 
> 
> TODO - table of notation
> 
> A Reso program can be defined as two ways:
>
> 1. As an image, i.e. a 2D grid of colored pixels,
> 2. or as an undirected graph of circuit elements.
>
> A Reso program is compiled from an image to this graph. They are tied together by mapping regions of connected pixels to nodes in the graph. Each simulated step updates the image / graph, meaning each iteration of Reso outputs another valid Reso program. Because the underlying structure of the circuit remains mostly the same, recompilation is not necessary at each step.
>
>
>TODO - diagram of Reso program with compiled graph on top, showing w, h, G, V
>
>Read on for more details/

A Reso program is an $n$-dimensional grid $I$ of elements. For our purposes, $n = 2$, and so this 2D grid has dimensions $h, w$. An element $p \in I$ is indexed $I_{i,j}$ for $i \in 1..h$ and $j \in 1..w$. A Reso program $I$ compiles to a graph $G = (V,E)$, where each node $V$ contains information $s \in \Sigma, P$, where $s$ describes the type of node, and $P$ is a list of coordinates $i, j$ that maps the  element to pixels in $I$.


### ** Table of Notation **

| Symbol | Meaning |
|-|-
| $I$    | Reso program image, a grid with $n$ dimensions. Assuming $n = 2$, $I$ is of size $w, h$
| $n$    | Number of dimensions of a Reso program image. In this paper, $n = 2$.
| $w, h$ | Size of Reso image.
| $p \in I$    | A pixel of the Reso grid, indexed as $p = I_{i, j}$ for indices $i, j$
| $\Sigma$     | Alphabet of pixels / vertices in Reso. See below.
| $G = (V, E)$ | Graph $G$ that a Reso program compiles to.

### ** Alphabet $\Sigma$ **

TODO: All colors (and reserved colors) in the Reso language

