#!/usr/bin/env python3

# Python script to convert BibTex entries to HTML code
# snippets.
import sys
import argparse

def parseFile(inf):
    if inf:
        f = inf
    else:
        f = open(inf)
    for line in f:
        print(line)
    
    return None
                

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='BibTex to HTML converter')
    parser.add_argument('-i', '--input', dest='inputFile',help='Input BibText file')
    parser.add_argument('-o', '--output', dest='outputFile',help='Output HTML file')
    args = parser.parse_args()
    if args.inputFile:
        inf = args.inputFile
    else:
        inf = sys.stdin
    if args.outputFile:
        outf = args.outputFile
    else:
        outf = sys.stdout
        
    dt = parseFile(inf)
    
