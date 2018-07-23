from resoboard import ResoBoard
from PIL import Image
import argparse
from math import log, ceil
import numpy as np


def main(load_filename,
         save_prefix,
         iterations = 1,
         save_each_iteration = True,
         V = False):
    
    num_digits_in_fname = ceil(log(iterations+.1,10))
    
    if V:
        print("  Loading", load_filename,"and iterating",iterations,"time(s),")
        print("  and then saving to ",save_prefix,'x'*num_digits_in_fname,".png",sep='')
    
    
    RB = ResoBoard(load_filename)
    
    for ii in range(iterations):
        if save_each_iteration:
            save_loc = save_prefix + str(ii).zfill(num_digits_in_fname) + ".png"
            Image.fromarray(np.swapaxes(RB.get_image(),0,1)).save(save_loc)
        if V:
            print("Iteration: ",ii)
        update_image = save_each_iteration or ii == iterations - 1
        RB.iterate(update_resels = False, update_image = update_image )
    
    # Last iteration, always printed
    if V:
        print("Iteration: ", iterations)
    save_loc = save_prefix + str(iterations).zfill(num_digits_in_fname) + ".png"
    Image.fromarray(np.swapaxes(RB.get_image(),0,1)).save(save_loc)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Reso!")
    parser.add_argument("load_location", help="Location to load image from",
                        type=str, nargs=1)
    parser.add_argument("--save", "-s", help="Prefix to save images to.",
                        type=str, nargs=1)
    parser.add_argument("--iterate","-i",
                        help="iterate n times. Default 1.",
                        type=int, nargs=1)
    parser.add_argument("--outputlast","-o", help="Only save the final iteration.",
                        action="store_true")
    parser.add_argument("--verbose","-v", help="Print extra info while working.",
                        action="store_true")

    args = parser.parse_args()
    
    if args.load_location is None:
        raise ValueError
    
    if args.save is None:
        raise ValueError

    load_filename   = args.load_location[0]
    save_prefix     = args.save[0]
    iterations = 1 if args.iterate  is None else args.iterate[0]
    save_each_iteration = not args.outputlast
    V = args.verbose
    
    main(load_filename, save_prefix, iterations, save_each_iteration, V)
