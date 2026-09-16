import argparse
import pathlib
import sys
import json

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
        args.show_type,
        args.show_size,
        args.search,
        args.modified,
        args.json
    )

def generate_tree(
    root_dir,
    depth,
    files,
    dirs,
    hidden,
    show_type,
    show_size,
    search,
    modified,
    json_output,
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
        hidden=hidden,
        show_type=show_type,
        show_size=show_size,
        search=search,
        modified=modified,
    )
    if json_output:
        print(json.dumps(tree._generator._build_json_tree(root_dir), indent=4))
    else:
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

    parser.add_argument(
        "-t",
        "--type",
        action="store_true",
        dest="show_type",
        help="show file types",
    )

    parser.add_argument(
        "-s",
        "--size",
        action="store_true",
        dest="show_size",
        help="show file sizes",
    )

    parser.add_argument(
        "--search",
        help="show only files matching the search term",
    )

    parser.add_argument(
        "-m",
        "--modified",
        action="store_true",
        dest="modified",
        help="show file modification times",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="output the tree as JSON",
    )

    return parser.parse_args()

