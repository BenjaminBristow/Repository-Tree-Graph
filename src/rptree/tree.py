import os
import pathlib


PIPE = "│"
ELBOW = "└──"
TEE = "├──"
PIPE_PREFIX = "│   "
SPACE_PREFIX = "    "
ELLIPSIS = "..."


class DirectoryTree:
    """Generate and print a tree representation of a directory."""

    def __init__(
        self,
        root_dir: str | pathlib.Path,
        depth: int | None = None,
        files_only: bool = False,
        dirs_only: bool = False,
        hidden: bool = False,
    ):
        self._generator = _TreeGenerator(
            root_dir,
            depth,
            files_only,
            dirs_only,
            hidden,
        )


    def generate(self) -> None:
        """Build the directory tree and print it to the terminal."""
        tree = self._generator.build_tree()

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
    ):
        self._root_dir = pathlib.Path(root_dir)
        self._depth = depth
        self._files_only = files_only
        self._dirs_only = dirs_only
        self._hidden = hidden
        self._tree: list[str] = []


    def build_tree(self) -> list[str]:
        """Build the complete directory tree."""
        self._tree_head()
        self._tree_body(self._root_dir)

        return self._tree


    def _tree_head(self) -> None:
        """Add the root directory to the tree."""
        self._tree.append(f"{self._root_dir}{os.sep}")
        self._tree.append(PIPE)


    def _tree_body(
        self,
        directory: pathlib.Path,
        prefix: str = "",
        current_depth: int = 0,
    ) -> None:
        """Recursively add the contents of a directory."""

        if self._depth is not None and current_depth >= self._depth:
            return

        entries = list(directory.iterdir())

        entries = sorted(
            entries,
            key=lambda entry: (entry.is_file(), entry.name.lower()),
        )

        visible_entries = self._get_visible_entries(entries)

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
            directory=directory,
            prefix=child_prefix,
            current_depth=next_depth,
        )

        if show_directory:
            self._tree.append(child_prefix.rstrip())


    def _add_file(
        self,
        file: pathlib.Path,
        prefix: str,
        connector: str,
    ) -> None:
        """Add a file to the tree."""

        if self._dirs_only and not self._files_only:
            return  

        self._tree.append(
            f"{prefix}{connector} {file.name}"
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

        if not self._hidden:
            entries = [
                entry
                for entry in entries
                if not entry.name.startswith(".")
            ]

        if self._files_only and not self._dirs_only:
            return [
                entry
                for entry in entries
                if entry.is_file()
            ]

        if self._dirs_only and not self._files_only:
            return [
                entry
                for entry in entries
                if entry.is_dir()
            ]

        return entries