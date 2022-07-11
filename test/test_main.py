#!/usr/bin/env python3
import os
import sys

# trick for test
current_pash = os.path.abspath(os.curdir)
target_path = current_pash + "/../bb-parser"
sys.path.append(target_path)

from BitbakeParser import BitbakeParser
from BitbakeVisitor import BitbakeVisitorBase

def main() -> None:
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
        return
    parser: BitbakeParser = BitbakeParser(BitbakeVisitorBase())
    parser.parse(sys.argv[1])

if __name__ == "__main__":
    main()
