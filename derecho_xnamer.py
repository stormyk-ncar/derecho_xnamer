#!/usr/bin/python3

# This is code for the Derecho supercomputer.
# this simply converts a dec1234 designator to an HPE friendly xname
# Author:  Storm Knight  CISL/HPCD/HSG  2024-07-29
# Work for Hire, property of NSF-NCAR
# No warranty expressed or implied.

# This reads from stdin, and replaces dec1234 with it's xname or deg0012 to it's xname
# This is super brittle and has expected edge cases
#         dec12345 will return an xname for dec1234 and append the 5 to it quietly
#         use at your own risk.
# IF more compute is added, and things get re-numberd this should be rewritten.

import sys
import re
import argparse


def dec_to_location_designator(dec_num):
    if dec_num>2432:
        dec_num=dec_num + 8  # First real gap
    # Extract the base 2 components from the decimal number
    r = ((dec_num -1) // 2048)
    x = (((dec_num -1) % 2048) // 256) %8
    c = (((dec_num -1) % 256) // 32)%8
    s = (((dec_num -1) % 32) // 4)%8
    b = (((dec_num -1) % 4) // 2)%2
    n = ((dec_num -1) % 2)

    # Format the location designator
    location_designator = f"x1{r}{str(x).zfill(2)}c{str(c).zfill(1)}s{str(s).zfill(1)}b{str(b).zfill(1)}n{str(n).zfill(1)}"
    return location_designator

def deg_to_location_designator(dec_num):
    if dec_num>64:
        dec_num = dec_num+14  # weird jump
    dec_num = dec_num+2560
    r = ((dec_num -1) // 2048)
    x = (((dec_num -1) % 2048) // 256) %8
    c = (((dec_num -1) % 128 ) // 16)%8
    s = (((dec_num -1) % 16) // 2)%8
    b = 0  #each node takes a blade
    n = ((dec_num -1) % 2)

    # Format the location designator
    location_designator = f"x1{r}{str(x).zfill(2)}c{str(c).zfill(1)}s{str(s).zfill(1)}b{str(b).zfill(1)}n{str(n).zfill(1)}"

    return location_designator


def replace_de_with_xnames(text):
    pattern = r'dec(\d{4})'
    matches = re.findall(pattern, text)
    for match in matches:
        dec_num = int(match)
        if dec_num>2488:
            continue
        location_designator = dec_to_location_designator(dec_num)
        text = text.replace(f"dec{match}", location_designator)
    pattern = r'deg(\d{4})'
    matches = re.findall(pattern, text)
    for match in matches:
        deg_num = int(match)
        if deg_num>82:
            continue;
        location_designator = deg_to_location_designator(deg_num)
        text = text.replace(f"deg{match}", location_designator)
    return text



def build_reverse():
    dec_list = [f"dec{str(i).zfill(4)}" for i in range(1, 2489)]
    deg_list = [f"deg{str(i).zfill(4)}" for i in range(1, 89)]
    combined_list = dec_list + deg_list
    reverse_table = {}
    for i, item in enumerate(combined_list):
        result = replace_de_with_xnames(item)
        reverse_table[result] = item
    return reverse_table

def replace_x_with_denames(text):
    #x1102c0s5b0n1
    pattern = r'x\d{4}c\ds\db\dn\d'  #the captures are for me to see better
    matches = re.findall(pattern, text)
    location_designator = build_reverse()
    for match in matches:
        text = text.replace(f"{match}", location_designator[match])
    return text




def main():
    parser = argparse.ArgumentParser(
            description="Replace derecho_names (deg0012)  to Xnames (x1102c0s5b0n1) via pipe",
            epilog="Example: ctt list | derecho_xnamer"
            )
    parser.add_argument('-r', '--reverse', action='store_true', help='reverse, xnames to derecho_names')

    args = parser.parse_args()

    input_text = sys.stdin.read()
    output_text = replace_de_with_xnames(input_text)
    if args.reverse:
        output_text=replace_x_with_denames(input_text)

    sys.stdout.write(output_text)


if __name__ == "__main__":
    main()
