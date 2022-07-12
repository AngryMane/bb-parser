#!/usr/bin/env python3
import os
import sys

# trick for test
current_pash = os.path.abspath(os.curdir)
target_path = current_pash + "/../bb-parser"
sys.path.append(target_path)

from BitbakeParser import BitbakeParser
from BitbakeVisitor import BitbakeVisitorBase


class TestVisitor(BitbakeVisitorBase):
    def warning_callback(
        self: "BitbakeVisitorBase", file_path: str, lineno: int, detail: str
    ) -> None:
        print(f"[WARNING]{file_path}:{lineno}  {detail}")

    def error_callback(
        self: "BitbakeVisitorBase", file_path: str, lineno: int, detail: str
    ) -> None:
        print(f"[ERROR]{file_path}:{lineno}  {detail}")


def main() -> None:
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
        return
    parser: BitbakeParser = BitbakeParser(TestVisitor())
    parser.parse(sys.argv[1])


if __name__ == "__main__":
    main()
