import argparse
import pathlib
import sys

from . import __version__
from .rptree import DirectoryTree

def main():
    args = parse_cmd_line_arguments()
    generate_tree(args.root_dir)

def generate_tree(root_dir):
    root_dir = pathlib.Path(root_dir)


    if not root_dir.is_dir():
        print(
            f"Error: '{root_dir}' is not a valid directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    tree = DirectoryTree(root_dir)
    tree.generate()


def parse_cmd_line_arguments():
    parser = argparse.ArgumentParser(
    prog="rptree",
    description="Generate a tree diagram of files and directories.",
    epilog="Thanks for using rptree!",
    )


    parser.version = f"rptree v{__version__}"

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        help="show the program version",
    )

    parser.add_argument(
        "root_dir",
        metavar="ROOT_DIR",
        nargs="?",
        default=".",
        help="directory to generate a tree for (default: current directory)",
    )

    return parser.parse_args()

