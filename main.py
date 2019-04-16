#!/usr/bin/python3

import sys
import os.path as path

import ytsub
from utils import print_help

if __name__ == "__main__":
    argv = sys.argv.copy()
    options = {}

    options["filename"] = path.basename(argv[0])
    if len(argv) < 2:
        print_help(**options)
        exit(0)

    verb = argv[1].lower()
    try:
        getattr(sys.modules["ytsub"], "ytsub_%s" % verb)
    except AttributeError:
        print_help(**options)
        exit(0)

    clone_argv = argv.copy()
    for arg in clone_argv[2:]:
        if arg.startswith("--"):
            argv.pop(argv.index(arg))
            options[arg[2:]] = True

    ytsub.call(verb, argv[2:], **options)
