import argparse
import pathlib
import sys
import json
import os

from importlib.metadata import version
from .tree import DirectoryTree, format_size

def main():
    args = parse_cmd_line_arguments()

    generate_tree(
        args.root_dir,
        args.depth,
        args.files,
        args.dirs,
        args.hidden,
        args.show_type,
        args.type_filter,
        args.show_size,
        args.search,
        args.modified,
        args.json,
        args.output,
        args.stats,
    )


def write_output(content: str, output: str | None) -> None:
    """Print output to the terminal or write it to a file."""

    if output:
        with open(output, "w") as file:
            file.write(content)
    else:
        print(content)


def generate_tree(
    root_dir,
    depth,
    files,
    dirs,
    hidden,
    show_type,
    type_filter,
    show_size,
    search,
    modified,
    json_output,
    output,
    stats,
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
        type_filter=type_filter,
    )

    if stats:
        statistics = tree._generator._build_statistics(root_dir)

        stats_output = []

        stats_output.append("")
        stats_output.append("=====================================================")
        stats_output.append(f"{root_dir.resolve().name}{os.sep}")
        stats_output.append("")
        stats_output.append(f"Files.     :  {statistics['files']}")
        stats_output.append(f"Directories:  {statistics['directories']}")
        stats_output.append(
            f"Total size :  {format_size(statistics['total_size'])}"
        )
        stats_output.append("")
        stats_output.append("File types:")

        if statistics["file_types"]:

            longest_type = max(
                len(file_type)
                for file_type in statistics["file_types"]
            )

            sorted_file_types = sorted(
                statistics["file_types"].items(),
                key=lambda item: (
                    item[0] == "Unknown",
                    -item[1]["count"],
                    item[0],
                ),
            )

            for file_type, data in sorted_file_types:

                if show_size:
                    stats_output.append(
                        f"  {file_type:<{longest_type}} : "
                        f"{data['count']:<7}"
                        f"[{format_size(data['size'])}]"
                    )
                else:
                    stats_output.append(
                        f"  {file_type:<{longest_type}} : "
                        f"{data['count']}"
                    )

        stats_output.append("=====================================================")
        stats_output.append("")

        write_output("\n".join(stats_output), output)

        return

    
    if json_output:
        json_data = json.dumps(
            tree._generator._build_json_tree(root_dir),
            indent=4,
        )

        write_output(json_data, output)

    else:
        tree_output = tree.get_output()

        write_output(tree_output, output)



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

    parser.add_argument(
        "--output",
        help="write the output to a file",
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="show file and directory statistics",
    )

    parser.add_argument(
        "--type-filter",
        help="Only show files of the specified type.",
    )


    return parser.parse_args()

