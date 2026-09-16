import argparse
import pathlib
import sys

from importlib.metadata import version
from .tree import DirectoryTree

def main():
    args = parse_cmd_line_arguments()

    generate_tree(
        args.root_dir,
        args.depth,
        args.files,
        args.dirs,
        args.hidden,
    )

def generate_tree(
    root_dir,
    depth,
    files,
    dirs,
    hidden,
):
    root_dir = pathlib.Path(root_dir)


    if not root_dir.is_dir():
        print(
            f"Error: '{root_dir}' is not a valid directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    tree = DirectoryTree(
        root_dir,
        depth,
        files_only=files,
        dirs_only=dirs,
        hidden=hidden
    )
    tree.generate()


def parse_cmd_line_arguments():
    parser = argparse.ArgumentParser(
    prog="rptree",
    description="Generate a tree diagram of files and directories.",
    epilog="Thanks for using rptree!",
    )


    parser.version = f"rptree v{version('rptree')}"

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

    parser.add_argument(
        "-dp",
        "--depth",
        type=int,
        help="limit the depth of the generated tree",
    )

    parser.add_argument(
        "-f",
        "--files",
        action="store_true",
        help="show files only",
    )

    parser.add_argument(
        "-d",
        "--dirs",
        action="store_true",
        help="show directories only",
    )

    parser.add_argument(
        "-hd",
        "--hidden",
        action="store_true",
        help="show hidden files and directories",
    )

    return parser.parse_args()

