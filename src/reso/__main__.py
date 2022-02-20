import argparse
from math import log, ceil
from time import time
import numpy as np
from PIL import Image
from .resoboard import ResoBoard

def main(
    load_filename,
    save_prefix,
    iterations = 1,
    save_each_iteration = True,
    V = False):
    """Wraps the logic in 'resoboard' for simulating, exporting, etc.
    
    Used in the actual '__main__' of this function, with parameters passed from
    argparser.
    
    :param load_filename: location from which to load the image from
    :type load_filename: String
    :param save_prefix: location to save the file to.
    :type save_prefix: String
    :param iterations: Number of simulation steps to update the circuit.
    :type iterations: Int
    :param save_each_iteration: If true, save an image of the circuit each iteration.
    :type save_each_iteration: Bool
    :param V: If True, print verbose output while running
    :type V: Bool
    """
    
    # See this ugly variable here?
    # This is why Python gave us fstrings.
    # todo: Use fstring magic and see if things still print right.
    num_digits_in_fname = ceil(log(iterations+.1,10))
    
    if V:
        print("  Loading", load_filename,"and iterating",iterations,"time(s),")
        print("  and then saving to ",save_prefix,'x'*num_digits_in_fname,".png",sep='')
    
    # Instantiate our ResoBoard
    compile_start = time()
    RB = ResoBoard(load_filename)
    compile_end = time()
    
    if V:
        print(f"... Compiled in {compile_end - compile_start:.2f} seconds! Iterating now.")
    
    # Simulation!
    iter_start = time()
    for ii in range(iterations):
        if save_each_iteration:
            save_loc = save_prefix + str(ii).zfill(num_digits_in_fname) + ".png"
            Image.fromarray(np.swapaxes(RB.get_image(),0,1)).save(save_loc)
        if V:
            print("Iteration: ",ii)
        # update_image is true if we're on our last iteration.
        update_image = save_each_iteration or ii == iterations - 1
        RB.iterate(update_resels = False, update_image = update_image )
    
    iter_end = time()
    # Last iteration, always saved
    if V:
        print("Iteration: ", iterations)
        print(f"Completed {iterations + 1} steps in {iter_end - iter_start:.2f} seconds!")
    save_loc = save_prefix + str(iterations).zfill(num_digits_in_fname) + ".png"
    Image.fromarray(np.swapaxes(RB.get_image(),0,1)).save(save_loc)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Reso - graphical circuit design cellular automata")
    parser.add_argument("load_location", help="Location to load image from.",
                        type=str, nargs=1)
    parser.add_argument("--save", "-s", help="Prefix to save images to.",
                        type=str, nargs=1)
    parser.add_argument("--numiter","-n",
                        help="iterate the reso board n times. Defaults to 1.",
                        type=int, nargs=1)
    parser.add_argument("--outputlast","-o",
                        help="Only save the final iteration of the board.",
                        action="store_true")
    parser.add_argument("--verbose","-v", help="Print extra information; useful for debugging.",
                        action="store_true")

    args = parser.parse_args()
    
    if args.load_location is None:
        raise ValueError
    
    if args.save is None:
        raise ValueError

    load_filename   = args.load_location[0]
    save_prefix     = args.save[0]
    iterations = 1 if args.numiter  is None else args.numiter[0]
    save_each_iteration = not args.outputlast
    V = args.verbose
    
    main(load_filename, save_prefix, iterations, save_each_iteration, V)
