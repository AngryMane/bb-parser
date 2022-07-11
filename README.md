# bb-parser

This is a parser for bitbake file. I developed this for the following use-cases.

* parse bitbake with user's own reduce functions
* paser bitbake without any other bitbake modules

This paser is based on the official parser, and the official parser's license is [GPL-2.0-only](https://spdx.org/licenses/GPL-2.0-only.html).

* [BBHandler](https://git.yoctoproject.org/poky/tree/bitbake/lib/bb/parse/parse_py/BBHandler.py)
* [ConfHandler](https://git.yoctoproject.org/poky/tree/bitbake/lib/bb/parse/parse_py/ConfHandler.py)

# Why not official parser?

You can see the official paser by the following links. These are so greate works!

* [BBHandler](https://git.yoctoproject.org/poky/tree/bitbake/lib/bb/parse/parse_py/BBHandler.py)
* [ConfHandler](https://git.yoctoproject.org/poky/tree/bitbake/lib/bb/parse/parse_py/ConfHandler.py)

But for instance, if I want to develop a linter for bitbake file, it's difficult to develop with the official parser because ...

* the official parser doesn't support custom reduce functions. Therefore, user can't customize what to do when specific syntax has come.
* the official parser is difficult to use without other bitbake modules

As a work-around for these, I developed bb-paser.

# How to use

1. Download 3-files in bb-perser dir.  
1. Copy these files into your project.
1. use like this

    ```
    from BitbakeParser import BitbakeParser
    from BitbakeVisitor import BitbakeVisitorBase

    def main() -> None:
        if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
            return
        parser: BitbakeParser = BitbakeParser(BitbakeVisitorBase())
        parser.parse(sys.argv[1])
    ```
    Please note that `BitbakeVisitorBase` is just base class for visitor, so you can create your own visitor class derived on them.
