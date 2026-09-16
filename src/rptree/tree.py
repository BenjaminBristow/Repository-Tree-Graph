import os
import pathlib
from datetime import datetime
import json


# Characters used to draw the directory tree in the terminal.
PIPE = "│"
ELBOW = "└──"
TEE = "├──"
PIPE_PREFIX = "│   "
SPACE_PREFIX = "    "
ELLIPSIS = "..."


# Maps file extensions to human-readable file types.
# This is used by the --type option and file statistics.
FILE_TYPES = {
    # Python
    ".py": "Python",
    ".pyw": "Python",
    ".pyx": "Cython",

    # Java
    ".java": "Java",
    ".class": "Java Bytecode",
    ".jar": "Java Archive",

    # C / C++
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++ Header",
    ".hh": "C++ Header",
    ".hxx": "C++ Header",

    # C#
    ".cs": "C#",

    # Go
    ".go": "Go",

    # Rust
    ".rs": "Rust",

    # Ruby
    ".rb": "Ruby",

    # PHP
    ".php": "PHP",

    # Swift
    ".swift": "Swift",

    # Kotlin
    ".kt": "Kotlin",
    ".kts": "Kotlin Script",

    # JavaScript / TypeScript
    ".js": "JavaScript",
    ".jsx": "JavaScript JSX",
    ".mjs": "JavaScript Module",
    ".cjs": "JavaScript CommonJS",
    ".ts": "TypeScript",
    ".tsx": "TypeScript JSX",
    ".mts": "TypeScript Module",
    ".cts": "TypeScript CommonJS",

    # Web
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".less": "Less",
    ".vue": "Vue",
    ".svelte": "Svelte",

    # Data / Configuration
    ".json": "JSON",
    ".jsonc": "JSON with Comments",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".ini": "INI",
    ".cfg": "Configuration",
    ".conf": "Configuration",
    ".env": "Environment",
    ".properties": "Properties",

    # Documentation / Text
    ".md": "Markdown",
    ".mdx": "MDX",
    ".txt": "Text",
    ".rst": "reStructuredText",
    ".rtf": "Rich Text",

    # Data
    ".csv": "CSV",
    ".tsv": "TSV",
    ".sql": "SQL",
    ".db": "Database",
    ".sqlite": "SQLite Database",
    ".sqlite3": "SQLite Database",

    # Shell / Scripts
    ".sh": "Shell",
    ".bash": "Bash",
    ".zsh": "Zsh",
    ".fish": "Fish",
    ".bat": "Batch",
    ".cmd": "Windows Command",
    ".ps1": "PowerShell",

    # Images
    ".png": "PNG Image",
    ".jpg": "JPEG Image",
    ".jpeg": "JPEG Image",
    ".gif": "GIF Image",
    ".bmp": "Bitmap Image",
    ".webp": "WebP Image",
    ".svg": "SVG Image",
    ".ico": "Icon",
    ".tif": "TIFF Image",
    ".tiff": "TIFF Image",
    ".avif": "AVIF Image",

    # Audio
    ".mp3": "MP3 Audio",
    ".wav": "WAV Audio",
    ".flac": "FLAC Audio",
    ".ogg": "OGG Audio",
    ".aac": "AAC Audio",
    ".m4a": "M4A Audio",
    ".wma": "WMA Audio",

    # Video
    ".mp4": "MP4 Video",
    ".mov": "QuickTime Video",
    ".avi": "AVI Video",
    ".mkv": "Matroska Video",
    ".webm": "WebM Video",
    ".wmv": "Windows Media Video",
    ".flv": "Flash Video",

    # Archives
    ".zip": "ZIP Archive",
    ".tar": "TAR Archive",
    ".gz": "GZIP Archive",
    ".bz2": "BZIP2 Archive",
    ".xz": "XZ Archive",
    ".7z": "7-Zip Archive",
    ".rar": "RAR Archive",

    # Documents
    ".pdf": "PDF Document",
    ".doc": "Word Document",
    ".docx": "Word Document",
    ".xls": "Excel Spreadsheet",
    ".xlsx": "Excel Spreadsheet",
    ".ppt": "PowerPoint Presentation",
    ".pptx": "PowerPoint Presentation",

    # Fonts
    ".ttf": "TrueType Font",
    ".otf": "OpenType Font",
    ".woff": "Web Font",
    ".woff2": "Web Font",
}


def get_file_type(file: pathlib.Path) -> str:
    """Return the type of a file based on its extension."""

    # Convert the extension to lowercase so .PY and .py are treated
    # as the same file type.
    return FILE_TYPES.get(file.suffix.lower(), "Unknown")


def get_file_size(file: pathlib.Path) -> str:
    """Return the size of a file in a human-readable format."""

    size = file.stat().st_size

    # Small files are displayed directly in bytes.
    if size < 1024:
        return f"{size} B"

    # Convert bytes to kilobytes once the file reaches 1 KB.
    if size < 1024**2:
        return f"{size / 1024:.1f} KB"

    # Convert bytes to megabytes once the file reaches 1 MB.
    if size < 1024**3:
        return f"{size / 1024**2:.1f} MB"

    # Files larger than 1 GB are displayed in gigabytes.
    return f"{size / 1024**3:.1f} GB"


def format_size(size: int) -> str:
    """Convert a size in bytes into a human-readable format."""

    if size < 1024:
        return f"{size} B"

    if size < 1024**2:
        return f"{size / 1024:.1f} KB"

    if size < 1024**3:
        return f"{size / 1024**2:.1f} MB"

    return f"{size / 1024**3:.1f} GB"


def get_modified_time(file: pathlib.Path) -> str:
    """Return the last modified time of a file."""

    modified_time = file.stat().st_mtime
    modified_datetime = datetime.fromtimestamp(modified_time)

    # Convert the timestamp into a format that is easier to read.
    return modified_datetime.strftime("%d/%m/%Y %H:%M")


class DirectoryTree:
    """Generate and print a tree representation of a directory."""

    def __init__(
        self,
        root_dir: str | pathlib.Path,
        depth: int | None = None,
        files_only: bool = False,
        dirs_only: bool = False,
        hidden: bool = False,
        show_type: bool = False,
        show_size: bool = False,
        search: str | None = None,
        modified: bool = False,
    ):
        # DirectoryTree acts as the public interface for the tree.
        # The actual work is delegated to _TreeGenerator.
        self._generator = _TreeGenerator(
            root_dir,
            depth,
            files_only,
            dirs_only,
            hidden,
            show_type,
            show_size,
            search,
            modified,
        )

    def generate(self) -> None:
        """Build the directory tree and print it to the terminal."""

        tree = self._generator.build_tree()

        # build_tree() returns each line separately, so print each
        # line to create the final tree in the terminal.
        for entry in tree:
            print(entry)


class _TreeGenerator:
    """Build the tree representation of a directory."""

    def __init__(
        self,
        root_dir: str | pathlib.Path,
        depth: int | None = None,
        files_only: bool = False,
        dirs_only: bool = False,
        hidden: bool = False,
        show_type: bool = False,
        show_size: bool = False,
        search: str | None = None,
        modified: bool = False,
    ):
        self._root_dir = pathlib.Path(root_dir)
        self._depth = depth
        self._files_only = files_only
        self._dirs_only = dirs_only
        self._hidden = hidden
        self._show_type = show_type
        self._show_size = show_size
        self._search = search
        self._modified = modified

        # The tree is built as a list of strings before being printed.
        self._tree: list[str] = []

    def build_tree(self) -> list[str]:
        """Build the complete directory tree."""

        # Build the root first, then recursively build everything underneath it.
        self._tree_head()
        self._tree_body(self._root_dir)

        return self._tree

    def _tree_head(self) -> None:
        """Add the root directory to the tree."""

        # resolve() gives us the actual directory name even when the user
        # runs rptree against "." where Path(".").name would be empty.
        root_name = self._root_dir.resolve().name

        self._tree.append(f"{root_name}{os.sep}")
        self._tree.append(PIPE)

    def _tree_body(
        self,
        directory: pathlib.Path,
        prefix: str = "",
        current_depth: int = 0,
    ) -> None:
        """Recursively add the contents of a directory."""

        # Stop recursion once the requested depth has been reached.
        if self._depth is not None and current_depth >= self._depth:
            return

        entries = list(directory.iterdir())

        # Sort directories before files, then sort alphabetically.
        entries = sorted(
            entries,
            key=lambda entry: (entry.is_file(), entry.name.lower()),
        )

        # Apply options such as --hidden, --files and --dirs.
        visible_entries = self._get_visible_entries(entries)

        # Search needs special handling because a directory must remain visible
        # if a matching file exists somewhere inside it.
        if self._search is not None:
            visible_entries = [
                entry
                for entry in visible_entries
                if (
                    entry.is_file() and self._matches_search(entry)
                )
                or (
                    entry.is_dir()
                    and self._directory_contains_match(entry)
                )
            ]

        # We iterate through the original entries rather than visible_entries.
        # This is important for --files because we still need to enter
        # directories to find files nested inside them.
        for entry in entries:
            if entry.is_dir():

                if self._files_only and not self._dirs_only:
                    self._tree_body(
                        entry,
                        prefix + PIPE_PREFIX,
                        current_depth + 1,
                    )
                    continue

            if entry not in visible_entries:
                continue

            # Find the entry's position amongst the entries that will
            # actually be displayed so the correct tree connector can be used.
            visible_index = visible_entries.index(entry)

            connector = (
                ELBOW
                if visible_index == len(visible_entries) - 1
                else TEE
            )

            if entry.is_dir():
                self._add_directory(
                    entry,
                    visible_index,
                    len(visible_entries),
                    prefix,
                    connector,
                    current_depth,
                )
            else:
                self._add_file(
                    entry,
                    prefix,
                    connector,
                )

    def _should_hide(self, entry: pathlib.Path) -> bool:
        """Return whether an entry should be hidden by the current filters."""

        if self._files_only and not self._dirs_only and entry.is_dir():
            return True

        if self._dirs_only and not self._files_only and entry.is_file():
            return True

        return False

    def _add_directory(
        self,
        directory: pathlib.Path,
        index: int,
        entries_count: int,
        prefix: str,
        connector: str,
        current_depth: int,
    ) -> None:
        """Add a directory and recursively add its contents."""

        # Directories are normally displayed, but --files hides them.
        show_directory = not self._files_only or self._dirs_only

        if show_directory:
            self._tree.append(
                f"{prefix}{connector} {directory.name}{os.sep}"
            )

        # Decide whether children need a vertical pipe depending on whether
        # this directory is the last visible entry at its level.
        if index != entries_count - 1:
            child_prefix = prefix + PIPE_PREFIX
        else:
            child_prefix = prefix + SPACE_PREFIX

        next_depth = current_depth + 1

        # If the next level would exceed the requested depth, stop here.
        if self._depth is not None and next_depth >= self._depth:
            if any(directory.iterdir()):
                self._tree.append(
                    f"{child_prefix}{SPACE_PREFIX}{ELLIPSIS}"
                )
            return

        # Recursively build this directory's contents.
        self._tree_body(
            directory=directory,
            prefix=child_prefix,
            current_depth=next_depth,
        )

        # Add spacing after a directory to keep the tree visually structured.
        if show_directory:
            self._tree.append(child_prefix.rstrip())

    def _add_file(
        self,
        file: pathlib.Path,
        prefix: str,
        connector: str,
    ) -> None:
        """Add a file to the tree."""

        # Files are not displayed when --dirs is active.
        if self._dirs_only and not self._files_only:
            return

        file_name = file.name

        # Add the human-readable file type when --type is enabled.
        if self._show_type:
            file_type = get_file_type(file)
            file_name += f" [{file_type}] "

        # Add the human-readable file size when --size is enabled.
        if self._show_size:
            file_size = get_file_size(file)
            file_name += f" [{file_size}] "

        # Add the last modification time when --modified is enabled.
        if self._modified:
            modified_time = get_modified_time(file)
            file_name += f" [Modified: {modified_time}] "

        self._tree.append(
            f"{prefix}{connector} {file_name}"
        )

    def _add_directory(
        self,
        directory: pathlib.Path,
        index: int,
        entries_count: int,
        prefix: str,
        connector: str,
        current_depth: int,
    ) -> None:
        """Add a directory and recursively add its contents."""

        show_directory = not self._files_only or self._dirs_only

        if show_directory:
            self._tree.append(
                f"{prefix}{connector} {directory.name}{os.sep}"
            )

        if index != entries_count - 1:
            child_prefix = prefix + PIPE_PREFIX
        else:
            child_prefix = prefix + SPACE_PREFIX

        next_depth = current_depth + 1

        if self._depth is not None and next_depth >= self._depth:
            if any(directory.iterdir()):
                self._tree.append(
                    f"{child_prefix}{SPACE_PREFIX}{ELLIPSIS}"
                )
            return

        self._tree_body(
            directory,
            child_prefix,
            next_depth,
        )

        if show_directory:
            self._tree.append(child_prefix.rstrip())

    def _get_visible_entries(
        self,
        entries: list[pathlib.Path],
    ) -> list[pathlib.Path]:
        """Return entries that should be displayed."""

        # Hidden files/directories are excluded unless --hidden is enabled.
        if not self._hidden:
            entries = [
                entry
                for entry in entries
                if not entry.name.startswith(".")
            ]

        # --files means directories are hidden from the output.
        if self._files_only and not self._dirs_only:
            return [
                entry
                for entry in entries
                if entry.is_file()
            ]

        # --dirs means files are hidden from the output.
        if self._dirs_only and not self._files_only:
            return [
                entry
                for entry in entries
                if entry.is_dir()
            ]

        return entries

    def _matches_search(self, entry: pathlib.Path) -> bool:
        """Return whether an entry matches the search term."""

        if self._search is None:
            return True

        # Search is case-insensitive and matches anywhere in the name.
        return self._search.lower() in entry.name.lower()

    def _directory_contains_match(
        self,
        directory: pathlib.Path,
    ) -> bool:
        """Return whether a directory or anything inside it matches the search term."""

        # A directory itself can match the search.
        if self._matches_search(directory):
            return True

        # Otherwise recursively search everything inside the directory.
        for entry in directory.iterdir():
            if entry.is_file() and self._matches_search(entry):
                return True

            if entry.is_dir() and self._directory_contains_match(entry):
                return True

        return False

    def _build_json_tree(
        self,
        directory: pathlib.Path,
    ) -> dict:
        """Build a dictionary representing a directory tree."""

        # JSON represents the tree using nested dictionaries instead of
        # the visual characters used by the terminal output.
        tree = {
            "name": directory.resolve().name,
            "type": "directory",
            "children": [],
        }

        entries = sorted(
            directory.iterdir(),
            key=lambda entry: (entry.is_file(), entry.name.lower()),
        )

        # Files-only JSON still needs to recursively enter directories.
        # The directories themselves are simply not included in the result.
        if self._files_only and not self._dirs_only:
            for entry in entries:
                if entry.is_dir():
                    nested_tree = self._build_json_tree(entry)
                    tree["children"].extend(
                        nested_tree["children"]
                    )

                elif entry in self._get_visible_entries(entries):
                    tree["children"].append(
                        self._build_json_file(entry)
                    )

            return tree

        visible_entries = self._get_visible_entries(entries)

        # Apply the same recursive search rules used by the normal tree.
        if self._search is not None:
            visible_entries = [
                entry
                for entry in visible_entries
                if (
                    entry.is_file() and self._matches_search(entry)
                )
                or (
                    entry.is_dir()
                    and self._directory_contains_match(entry)
                )
            ]

        for entry in visible_entries:
            if entry.is_dir():
                tree["children"].append(
                    self._build_json_tree(entry)
                )
            else:
                tree["children"].append(
                    self._build_json_file(entry)
                )

        return tree

    def _build_json_file(
        self,
        file: pathlib.Path,
    ) -> dict:
        """Build a dictionary representing a file."""

        result = {
            "name": file.name,
            "type": "file",
        }

        # Only add optional metadata when the corresponding CLI option
        # has been requested.
        if self._show_type:
            result["file_type"] = get_file_type(file)

        if self._show_size:
            result["size"] = get_file_size(file)

        if self._modified:
            result["modified"] = get_modified_time(file)

        return result

    def _build_statistics(
        self,
        directory: pathlib.Path,
    ) -> dict:
        """Build statistics for a directory tree."""

        # Start with empty statistics that will be updated while
        # recursively scanning the directory.
        statistics = {
            "files": 0,
            "directories": 0,
            "total_size": 0,
            "file_types": {},
        }

        entries = sorted(
            directory.iterdir(),
            key=lambda entry: (entry.is_file(), entry.name.lower()),
        )

        # --files still needs to enter directories so nested files
        # can be found. The directories themselves are not counted.
        if self._files_only and not self._dirs_only:
            for entry in entries:
                if entry.is_dir():
                    nested_statistics = self._build_statistics(entry)

                    statistics["files"] += nested_statistics["files"]
                    statistics["total_size"] += nested_statistics["total_size"]

                    # Merge file-type counts from the nested directory.
                    for file_type, count in nested_statistics["file_types"].items():
                        statistics["file_types"][file_type] = (
                            statistics["file_types"].get(file_type, 0) + count
                        )

                elif entry in self._get_visible_entries(entries):
                    statistics["files"] += 1
                    statistics["total_size"] += entry.stat().st_size

                    file_type = get_file_type(entry)

                    statistics["file_types"][file_type] = (
                        statistics["file_types"].get(file_type, 0) + 1
                    )

            return statistics

        # Apply normal visibility filters such as --hidden and --dirs.
        visible_entries = self._get_visible_entries(entries)

        # Apply the same recursive search behaviour as the normal tree.
        if self._search is not None:
            visible_entries = [
                entry
                for entry in visible_entries
                if (
                    entry.is_file() and self._matches_search(entry)
                )
                or (
                    entry.is_dir()
                    and self._directory_contains_match(entry)
                )
            ]

        for entry in visible_entries:
            if entry.is_dir():
                statistics["directories"] += 1

                # Recursively collect statistics from this directory.
                nested_statistics = self._build_statistics(entry)

                # Add the nested results to our current totals.
                statistics["files"] += nested_statistics["files"]
                statistics["directories"] += nested_statistics["directories"]
                statistics["total_size"] += nested_statistics["total_size"]

                # Merge the nested file-type counts into the current dictionary.
                for file_type, count in nested_statistics["file_types"].items():
                    statistics["file_types"][file_type] = (
                        statistics["file_types"].get(file_type, 0) + count
                    )

            else:
                statistics["files"] += 1
                statistics["total_size"] += entry.stat().st_size

                # Count how many files belong to each recognised file type.
                file_type = get_file_type(entry)

                statistics["file_types"][file_type] = (
                    statistics["file_types"].get(file_type, 0) + 1
                )

        return statistics