from rptree.cli import main
from importlib.metadata import version
from datetime import datetime
import json
import pathlib
from rptree.cli import generate_tree
from rptree.tree import (
    DirectoryTree,
    _TreeGenerator,
    get_file_type, 
    get_file_size, 
    get_modified_time,
    format_size,
)


# Tests that an empty directory produces only the root directory and tree line.
def test_empty_directory(tmp_path):
    tree = DirectoryTree(tmp_path)
    result = tree._generator.build_tree()

    assert result == [
        f"{tmp_path.name}/",
        "│",
    ]


# Tests that a single file is correctly displayed in the tree.
def test_single_file(tmp_path):
    file1 = tmp_path / "file1.txt"
    file1.touch()

    tree = DirectoryTree(tmp_path)
    result = tree._generator.build_tree()

    assert "└── file1.txt" in result


# Tests that nested directories and their files are correctly displayed.
def test_nested_directory(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()

    file1 = folder / "file1.txt"
    file1.touch()

    tree = DirectoryTree(tmp_path)
    result = tree._generator.build_tree()

    assert "└── folder/" in result
    assert "    └── file1.txt" in result


# Tests that multiple files are correctly displayed in the correct tree positions.
def test_multiple_files(tmp_path):
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.py"
    file3 = tmp_path / "file3.md"

    file1.touch()
    file2.touch()
    file3.touch()

    tree = DirectoryTree(tmp_path)
    result = tree._generator.build_tree()

    assert "├── file1.txt" in result
    assert "├── file2.py" in result
    assert "└── file3.md" in result


# Tests that multiple nested directories and their files are correctly displayed.
def test_multiple_nested_directories(tmp_path):
    folder1 = tmp_path / "folder1"
    folder2 = tmp_path / "folder2"

    folder1.mkdir()
    folder2.mkdir()

    file1 = folder1 / "file1.txt"
    file2 = folder2 / "file2.txt"

    file1.touch()
    file2.touch()

    tree = DirectoryTree(tmp_path)
    result = tree._generator.build_tree()

    assert "├── folder1/" in result
    assert "│   └── file1.txt" in result
    assert "└── folder2/" in result
    assert "    └── file2.txt" in result


# Tests that the CLI displays the current installed package version.
def test_cli_version(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["rptree", "--version"])

    try:
        main()
    except SystemExit:
        pass

    captured = capsys.readouterr()

    assert f"rptree v{version('rptree')}" in captured.out


# Tests that the CLI help message contains the expected description and arguments.
def test_cli_help(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["rptree", "--help"])

    try:
        main()
    except SystemExit:
        pass

    captured = capsys.readouterr()

    assert "Generate a tree diagram of files and directories." in captured.out
    assert "--version" in captured.out
    assert "ROOT_DIR" in captured.out


# Tests that the CLI returns an error when the supplied directory does not exist.
def test_cli_invalid_directory(capsys, monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "does-not-exist"],
    )

    try:
        main()
    except SystemExit as error:
        assert error.code == 1

    captured = capsys.readouterr()

    assert "Error: 'does-not-exist' is not a valid directory." in captured.err


# Tests that the CLI correctly generates a tree for a supplied directory.
def test_cli_directory(capsys, monkeypatch, tmp_path):
    file1 = tmp_path / "file1.txt"
    folder = tmp_path / "folder"

    file1.touch()
    folder.mkdir()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", str(tmp_path)],
    )

    main()

    captured = capsys.readouterr()

    assert f"{tmp_path.name}/" in captured.out
    assert "├── folder/" in captured.out
    assert "└── file1.txt" in captured.out


# Tests that the depth option prevents the tree from displaying deeper levels.
def test_depth_limit(tmp_path):
    folder1 = tmp_path / "folder1"
    folder2 = folder1 / "folder2"
    file1 = folder2 / "file1.txt"

    folder2.mkdir(parents=True)
    file1.touch()

    tree = DirectoryTree(tmp_path, depth=1)
    result = tree._generator.build_tree()

    assert "└── folder1/" in result
    assert "    └── folder2/" not in result
    assert "        └── file1.txt" not in result


# Tests that the depth option allows directories up to the requested depth.
def test_depth_allows_nested_directories(tmp_path):
    folder1 = tmp_path / "folder1"
    folder2 = folder1 / "folder2"
    file1 = folder2 / "file1.txt"

    folder2.mkdir(parents=True)
    file1.touch()

    tree = DirectoryTree(tmp_path, depth=2)
    result = tree._generator.build_tree()

    assert "└── folder1/" in result
    assert "    └── folder2/" in result
    assert "        └── file1.txt" not in result


# Tests that an ellipsis is displayed when deeper contents are hidden by the depth limit.
def test_depth_limit_shows_ellipsis(tmp_path):
    folder = tmp_path / "folder"
    file1 = folder / "file1.txt"
    file2 = folder / "file2.txt"

    folder.mkdir()
    file1.touch()
    file2.touch()

    tree = DirectoryTree(tmp_path, depth=1)
    result = tree._generator.build_tree()

    assert "└── folder/" in result
    assert "        ..." in result
    assert "file1.txt" not in result
    assert "file2.txt" not in result


# Tests that only one ellipsis is displayed for a directory whose contents exceed the depth limit.
def test_depth_limit_shows_one_ellipsis(tmp_path):
    folder = tmp_path / "folder"

    folder.mkdir()

    (folder / "file1.txt").touch()
    (folder / "file2.txt").touch()
    (folder / "another_folder").mkdir()

    tree = DirectoryTree(tmp_path, depth=1)
    result = tree._generator.build_tree()

    assert result.count("        ...") == 1


# Tests that an empty directory does not display an unnecessary ellipsis.
def test_depth_limit_empty_directory_no_ellipsis(tmp_path):
    folder = tmp_path / "empty"
    folder.mkdir()

    tree = DirectoryTree(tmp_path, depth=1)
    result = tree._generator.build_tree()

    assert "└── empty/" in result
    assert "..." not in result


# Tests that the ellipsis appears at the correct level when using a depth of two.
def test_depth_two_shows_ellipsis_at_correct_level(tmp_path):
    folder1 = tmp_path / "folder1"
    folder2 = folder1 / "folder2"

    folder2.mkdir(parents=True)
    (folder2 / "file.txt").touch()

    tree = DirectoryTree(tmp_path, depth=2)
    result = tree._generator.build_tree()

    assert "└── folder1/" in result
    assert "    └── folder2/" in result
    assert "            ..." in result
    assert "file.txt" not in result


# Tests that the files-only option displays files without displaying directories.
def test_files_only(tmp_path):
    folder = tmp_path / "folder"
    file1 = tmp_path / "file1.txt"
    file2 = folder / "file2.txt"

    folder.mkdir()
    file1.touch()
    file2.touch()

    tree = DirectoryTree(tmp_path, files_only=True)
    result = tree._generator.build_tree()

    assert "└── file1.txt" in result
    assert "file2.txt" not in result
    assert "folder/" not in result


# Tests that the files-only option still finds files inside nested directories.
def test_files_only_in_nested_directories(tmp_path):
    folder1 = tmp_path / "folder1"
    folder2 = folder1 / "folder2"
    file1 = folder1 / "file1.txt"
    file2 = folder2 / "file2.txt"

    folder2.mkdir(parents=True)
    file1.touch()
    file2.touch()

    tree = DirectoryTree(
        tmp_path,
        files_only=True,
    )

    result = tree._generator.build_tree()

    assert any("file1.txt" in line for line in result)
    assert any("file2.txt" in line for line in result)
    assert "folder1/" not in result
    assert "folder2/" not in result


# Tests that the directories-only option displays directories without displaying files.
def test_directories_only(tmp_path):
    folder1 = tmp_path / "folder1"
    folder2 = folder1 / "folder2"
    file1 = tmp_path / "file1.txt"

    folder2.mkdir(parents=True)
    file1.touch()

    tree = DirectoryTree(tmp_path, dirs_only=True)
    result = tree._generator.build_tree()

    assert "└── folder1/" in result
    assert "    └── folder2/" in result
    assert "file1.txt" not in result


# Tests that enabling both files-only and directories-only displays both types of entries.
def test_files_and_directories_together(tmp_path):
    folder = tmp_path / "folder"
    file1 = tmp_path / "file1.txt"

    folder.mkdir()
    file1.touch()

    tree = DirectoryTree(
        tmp_path,
        files_only=True,
        dirs_only=True,
    )

    result = tree._generator.build_tree()

    assert "├── folder/" in result
    assert "└── file1.txt" in result


# Tests that the CLI files option displays files and hides directories.
def test_cli_files(capsys, monkeypatch, tmp_path):
    folder = tmp_path / "folder"
    file1 = tmp_path / "file1.txt"

    folder.mkdir()
    file1.touch()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--files", str(tmp_path)],
    )

    main()

    captured = capsys.readouterr()

    assert "file1.txt" in captured.out
    assert "folder/" not in captured.out


# Tests that the CLI dirs option displays directories and hides files.
def test_cli_dirs(capsys, monkeypatch, tmp_path):
    folder = tmp_path / "folder"
    file1 = tmp_path / "file1.txt"

    folder.mkdir()
    file1.touch()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--dirs", str(tmp_path)],
    )

    main()

    captured = capsys.readouterr()

    assert "folder/" in captured.out
    assert "file1.txt" not in captured.out


# Tests that the files-only option respects the depth limit.
def test_files_only_with_depth_limit(tmp_path):
    folder = tmp_path / "folder"
    nested_file = folder / "nested.txt"
    root_file = tmp_path / "root.txt"

    folder.mkdir()
    nested_file.touch()
    root_file.touch()

    tree = DirectoryTree(
        tmp_path,
        depth=1,
        files_only=True,
    )

    result = tree._generator.build_tree()

    assert any("root.txt" in line for line in result)
    assert not any("nested.txt" in line for line in result)
    assert "folder/" not in result


# Tests that the directories-only option respects the depth limit.
def test_directories_only_with_depth_limit(tmp_path):
    folder = tmp_path / "folder"
    nested_folder = folder / "nested"

    nested_folder.mkdir(parents=True)

    tree = DirectoryTree(
        tmp_path,
        depth=1,
        dirs_only=True,
    )

    result = tree._generator.build_tree()

    assert any("folder/" in line for line in result)
    assert not any("nested/" in line for line in result)


# Tests that hidden files are not displayed unless the hidden option is enabled.
def test_hidden_entries_are_hidden_by_default(tmp_path):
    visible_file = tmp_path / "visible.txt"
    hidden_file = tmp_path / ".hidden"

    visible_file.touch()
    hidden_file.touch()

    tree = DirectoryTree(tmp_path)
    result = tree._generator.build_tree()

    assert "visible.txt" in result[-1]
    assert not any(".hidden" in line for line in result)


# Tests that the CLI hidden option displays both visible and hidden files.
def test_cli_hidden(capsys, monkeypatch, tmp_path):
    visible_file = tmp_path / "visible.txt"
    hidden_file = tmp_path / ".hidden"

    visible_file.touch()
    hidden_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--hidden", str(tmp_path)],
    )

    main()

    captured = capsys.readouterr()

    assert "visible.txt" in captured.out
    assert ".hidden" in captured.out


# Tests that hidden directories and their contents are hidden by default.
def test_hidden_directories_are_hidden_by_default(tmp_path):
    hidden_dir = tmp_path / ".hidden"
    hidden_file = hidden_dir / "secret.txt"
    visible_file = tmp_path / "visible.txt"

    hidden_dir.mkdir()
    hidden_file.touch()
    visible_file.touch()

    tree = DirectoryTree(tmp_path)
    result = tree._generator.build_tree()

    assert any("visible.txt" in line for line in result)
    assert not any(".hidden" in line for line in result)
    assert not any("secret.txt" in line for line in result)


# Tests that the hidden option allows hidden directories and their contents to be displayed.
def test_hidden_directories_can_be_shown(tmp_path):
    hidden_dir = tmp_path / ".hidden"
    hidden_file = hidden_dir / "secret.txt"

    hidden_dir.mkdir()
    hidden_file.touch()

    tree = DirectoryTree(
        tmp_path,
        hidden=True,
    )

    result = tree._generator.build_tree()

    assert any(".hidden/" in line for line in result)
    assert any("secret.txt" in line for line in result)


# Tests that Python files are correctly identified as Python files.
def test_get_file_type_python(tmp_path):
    file = tmp_path / "example.py"
    file.touch()

    assert get_file_type(file) == "Python"


# Tests that Markdown files are correctly identified as Markdown files.
def test_get_file_type_markdown(tmp_path):
    file = tmp_path / "README.md"
    file.touch()

    assert get_file_type(file) == "Markdown"


# Tests that unknown file extensions return Unknown as their type.
def test_get_file_type_unknown(tmp_path):
    file = tmp_path / "example.xyz"
    file.touch()

    assert get_file_type(file) == "Unknown"


# Tests that files without extensions return Unknown as their type.
def test_get_file_type_no_extension(tmp_path):
    file = tmp_path / "README"
    file.touch()

    assert get_file_type(file) == "Unknown"


# Tests that file type detection is case-insensitive.
def test_get_file_type_uppercase_extension(tmp_path):
    file = tmp_path / "example.PY"
    file.touch()

    assert get_file_type(file) == "Python"


# Tests that the type option adds a human-readable type to supported files.
def test_type_option_shows_file_type(tmp_path):
    python_file = tmp_path / "example.py"
    markdown_file = tmp_path / "README.md"

    python_file.touch()
    markdown_file.touch()

    tree = DirectoryTree(
        tmp_path,
        show_type=True,
    )

    result = tree._generator.build_tree()

    assert any("example.py [Python]" in line for line in result)
    assert any("README.md [Markdown]" in line for line in result)


# Tests that the type option labels files with unknown extensions as Unknown.
def test_type_option_unknown_file(tmp_path):
    file = tmp_path / "example.xyz"
    file.touch()

    tree = DirectoryTree(
        tmp_path,
        show_type=True,
    )

    result = tree._generator.build_tree()

    assert any("example.xyz [Unknown]" in line for line in result)


# Tests that the type option does not add type labels to directories.
def test_type_option_does_not_label_directories(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()

    tree = DirectoryTree(
        tmp_path,
        show_type=True,
    )

    result = tree._generator.build_tree()

    assert "└── folder/" in result
    assert not any("[Unknown]" in line for line in result)


# Tests that file types are not displayed when the type option is disabled.
def test_type_option_disabled_by_default(tmp_path):
    file = tmp_path / "example.py"
    file.touch()

    tree = DirectoryTree(tmp_path)
    result = tree._generator.build_tree()

    assert any("example.py" in line for line in result)
    assert not any("[Python]" in line for line in result)


# Tests that the CLI type option displays file types and leaves directories unchanged.
def test_cli_type(capsys, monkeypatch, tmp_path):
    python_file = tmp_path / "example.py"
    unknown_file = tmp_path / "example.xyz"
    folder = tmp_path / "folder"

    python_file.touch()
    unknown_file.touch()
    folder.mkdir()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--type", str(tmp_path)],
    )

    main()

    captured = capsys.readouterr()

    assert "example.py [Python]" in captured.out
    assert "example.xyz [Unknown]" in captured.out
    assert "folder/" in captured.out
    assert "folder/ [Unknown]" not in captured.out


# Tests that the type option works correctly alongside the files-only option.
def test_cli_type_with_files(capsys, monkeypatch, tmp_path):
    python_file = tmp_path / "example.py"
    folder = tmp_path / "folder"

    python_file.touch()
    folder.mkdir()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--type", "--files", str(tmp_path)],
    )

    main()

    captured = capsys.readouterr()

    assert "example.py [Python]" in captured.out
    assert "folder/" not in captured.out


# Tests that files smaller than 1 KB are displayed in bytes.
def test_get_file_size_bytes(tmp_path):
    file = tmp_path / "small.txt"
    file.write_bytes(b"a" * 500)

    assert get_file_size(file) == "500 B"


# Tests that files between 1 KB and 1 MB are displayed in kilobytes.
def test_get_file_size_kilobytes(tmp_path):
    file = tmp_path / "medium.txt"
    file.write_bytes(b"a" * 2048)

    assert get_file_size(file) == "2.0 KB"


# Tests that files between 1 MB and 1 GB are displayed in megabytes.
def test_get_file_size_megabytes(tmp_path):
    file = tmp_path / "large.txt"
    file.write_bytes(b"a" * (2 * 1024**2))

    assert get_file_size(file) == "2.0 MB"


# Tests that files of at least 1 GB are displayed in gigabytes.
def test_get_file_size_gigabytes(tmp_path):
    file = tmp_path / "huge.txt"
    file.write_bytes(b"a" * (2 * 1024**3))

    assert get_file_size(file) == "2.0 GB"


# Tests that an empty file is correctly reported as 0 bytes.
def test_get_file_size_empty_file(tmp_path):
    file = tmp_path / "empty.txt"
    file.touch()

    assert get_file_size(file) == "0 B"


# Tests that the size option adds the file size to displayed files.
def test_size_option_shows_file_size(tmp_path):
    file = tmp_path / "example.txt"
    file.write_bytes(b"a" * 2048)

    tree = DirectoryTree(
        tmp_path,
        show_size=True,
    )

    result = tree._generator.build_tree()

    assert any("example.txt [2.0 KB]" in line for line in result)


# Tests that the size option correctly displays empty files as 0 bytes.
def test_size_option_empty_file(tmp_path):
    file = tmp_path / "empty.txt"
    file.touch()

    tree = DirectoryTree(
        tmp_path,
        show_size=True,
    )

    result = tree._generator.build_tree()

    assert any("empty.txt [0 B]" in line for line in result)


# Tests that the size option does not add size labels to directories.
def test_size_option_does_not_label_directories(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()

    tree = DirectoryTree(
        tmp_path,
        show_size=True,
    )

    result = tree._generator.build_tree()

    assert "└── folder/" in result
    assert not any("[0 B]" in line for line in result)



# Tests that file sizes are not displayed when the size option is disabled.
def test_size_option_disabled_by_default(tmp_path):
    file = tmp_path / "example.txt"
    file.write_bytes(b"a" * 2048)

    tree = DirectoryTree(tmp_path)
    result = tree._generator.build_tree()

    assert any("example.txt" in line for line in result)
    assert not any("[2.0 KB]" in line for line in result)



# Tests that the CLI size option displays file sizes correctly.
def test_cli_size(capsys, monkeypatch, tmp_path):
    file = tmp_path / "example.txt"
    file.write_bytes(b"a" * 2048)

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--size", str(tmp_path)],
    )

    main()

    captured = capsys.readouterr()

    assert "example.txt [2.0 KB]" in captured.out



# Tests that the type and size options work correctly together.
def test_cli_type_and_size(capsys, monkeypatch, tmp_path):
    file = tmp_path / "example.py"
    file.write_bytes(b"a" * 2048)

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--type", "--size", str(tmp_path)],
    )

    main()

    captured = capsys.readouterr()

    assert "example.py [Python]  [2.0 KB]" in captured.out



# Tests that a filename matching the search term returns True.
def test_search_matches_filename(tmp_path):
    file = tmp_path / "database.py"
    file.touch()

    tree = DirectoryTree(tmp_path, search="data")

    assert tree._generator._matches_search(file) is True



# Tests that a filename not matching the search term returns False.
def test_search_does_not_match_filename(tmp_path):
    file = tmp_path / "database.py"
    file.touch()

    tree = DirectoryTree(tmp_path, search="python")

    assert tree._generator._matches_search(file) is False



# Tests that search matching is case-insensitive.
def test_search_is_case_insensitive(tmp_path):
    file = tmp_path / "Database.py"
    file.touch()

    tree = DirectoryTree(tmp_path, search="database")

    assert tree._generator._matches_search(file) is True



# Tests that every entry matches when no search term is provided.
def test_search_disabled_matches_everything(tmp_path):
    file = tmp_path / "database.py"
    file.touch()

    tree = DirectoryTree(tmp_path)

    assert tree._generator._matches_search(file) is True



# Tests that a directory matches when its own name contains the search term.
def test_search_matches_directory_name(tmp_path):
    directory = tmp_path / "database"
    directory.mkdir()

    tree = DirectoryTree(tmp_path, search="data")

    assert tree._generator._directory_contains_match(directory) is True



# Tests that a directory matches when a file directly inside it matches.
def test_search_matches_file_inside_directory(tmp_path):
    directory = tmp_path / "src"
    directory.mkdir()

    file = directory / "database.py"
    file.touch()

    tree = DirectoryTree(tmp_path, search="database")

    assert tree._generator._directory_contains_match(directory) is True



# Tests that a directory matches when a nested directory contains a matching file.
def test_search_matches_nested_file(tmp_path):
    directory = tmp_path / "src"
    nested_directory = directory / "backend"
    nested_directory.mkdir(parents=True)

    file = nested_directory / "database.py"
    file.touch()

    tree = DirectoryTree(tmp_path, search="database")

    assert tree._generator._directory_contains_match(directory) is True



# Tests that multiple levels of directories are kept when a deeply nested file matches.
def test_search_keeps_all_parent_directories(tmp_path):
    directory = (
        tmp_path
        / "src"
        / "backend"
        / "database"
        / "models"
    )
    directory.mkdir(parents=True)

    file = directory / "user_database.py"
    file.touch()

    tree = DirectoryTree(tmp_path, search="database")

    assert tree._generator._directory_contains_match(
        tmp_path / "src"
    ) is True



# Tests that an unrelated directory does not match the search term.
def test_search_does_not_match_unrelated_directory(tmp_path):
    directory = tmp_path / "src"
    directory.mkdir()

    file = directory / "main.py"
    file.touch()

    tree = DirectoryTree(tmp_path, search="database")

    assert tree._generator._directory_contains_match(directory) is False



# Tests that only matching files are shown when searching.
def test_search_shows_matching_files_only(tmp_path, capsys):
    matching_file = tmp_path / "database.py"
    matching_file.touch()

    unrelated_file = tmp_path / "main.py"
    unrelated_file.touch()

    tree = DirectoryTree(tmp_path, search="database")
    tree.generate()

    captured = capsys.readouterr()

    assert "database.py" in captured.out
    assert "main.py" not in captured.out



# Tests that parent directories are shown when they contain a matching file.
def test_search_shows_parent_directories(tmp_path, capsys):
    directory = tmp_path / "src"
    directory.mkdir()

    file = directory / "database.py"
    file.touch()

    tree = DirectoryTree(tmp_path, search="database")
    tree.generate()

    captured = capsys.readouterr()

    assert "src/" in captured.out
    assert "database.py" in captured.out



# Tests that deeply nested parent directories are all shown when a file matches.
def test_search_shows_deeply_nested_parent_directories(tmp_path, capsys):
    directory = (
        tmp_path
        / "src"
        / "backend"
        / "database"
        / "models"
    )
    directory.mkdir(parents=True)

    file = directory / "user_database.py"
    file.touch()

    tree = DirectoryTree(tmp_path, search="database")
    tree.generate()

    captured = capsys.readouterr()

    assert "src/" in captured.out
    assert "backend/" in captured.out
    assert "database/" in captured.out
    assert "models/" in captured.out
    assert "user_database.py" in captured.out



# Tests that unrelated files inside a matching directory remain hidden.
def test_search_hides_unrelated_files_inside_matching_directory(
    tmp_path,
    capsys,
):
    directory = tmp_path / "tests"
    directory.mkdir()

    matching_file = directory / "test_tree.py"
    matching_file.touch()

    unrelated_file = directory / "README.md"
    unrelated_file.touch()

    tree = DirectoryTree(tmp_path, search="test")
    tree.generate()

    captured = capsys.readouterr()

    assert "tests/" in captured.out
    assert "test_tree.py" in captured.out
    assert "README.md" not in captured.out



# Tests that unrelated directories are hidden when searching.
def test_search_hides_unrelated_directories(tmp_path, capsys):
    matching_directory = tmp_path / "src"
    matching_directory.mkdir()

    matching_file = matching_directory / "database.py"
    matching_file.touch()

    unrelated_directory = tmp_path / "docs"
    unrelated_directory.mkdir()

    unrelated_file = unrelated_directory / "README.md"
    unrelated_file.touch()

    tree = DirectoryTree(tmp_path, search="database")
    tree.generate()

    captured = capsys.readouterr()

    assert "src/" in captured.out
    assert "database.py" in captured.out
    assert "docs/" not in captured.out
    assert "README.md" not in captured.out



# Tests that a matching directory does not automatically show unrelated files inside it.
def test_search_matching_directory_does_not_show_all_contents(
    tmp_path,
    capsys,
):
    directory = tmp_path / "tests"
    directory.mkdir()

    matching_file = directory / "test_tree.py"
    matching_file.touch()

    unrelated_file = directory / "example.py"
    unrelated_file.touch()

    tree = DirectoryTree(tmp_path, search="tests")
    tree.generate()

    captured = capsys.readouterr()

    assert "tests/" in captured.out
    assert "test_tree.py" not in captured.out
    assert "example.py" not in captured.out



# Tests that searching works correctly through the command-line interface.
def test_cli_search(tmp_path, capsys, monkeypatch):
    matching_file = tmp_path / "database.py"
    matching_file.touch()

    unrelated_file = tmp_path / "main.py"
    unrelated_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--search", "database", str(tmp_path)],
    )

    main()

    captured = capsys.readouterr()

    assert "database.py" in captured.out
    assert "main.py" not in captured.out



# Tests that search works together with the file type option.
def test_cli_search_and_type(tmp_path, capsys, monkeypatch):
    matching_file = tmp_path / "database.py"
    matching_file.touch()

    unrelated_file = tmp_path / "main.py"
    unrelated_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--search", "database", "--type", str(tmp_path)],
    )

    main()

    captured = capsys.readouterr()

    assert "database.py [Python]" in captured.out
    assert "main.py" not in captured.out



# Tests that search works together with the file size option.
def test_cli_search_and_size(tmp_path, capsys, monkeypatch):
    matching_file = tmp_path / "database.py"
    matching_file.write_bytes(b"a" * 2048)

    unrelated_file = tmp_path / "main.py"
    unrelated_file.write_bytes(b"b" * 1024)

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--search", "database", "--size", str(tmp_path)],
    )

    main()

    captured = capsys.readouterr()

    assert "database.py [2.0 KB]" in captured.out
    assert "main.py" not in captured.out



# Tests that search works together with both the file type and size options.
def test_cli_search_type_and_size(tmp_path, capsys, monkeypatch):
    matching_file = tmp_path / "database.py"
    matching_file.write_bytes(b"a" * 2048)

    unrelated_file = tmp_path / "main.py"
    unrelated_file.write_bytes(b"b" * 1024)

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            "--search",
            "database",
            "--type",
            "--size",
            str(tmp_path),
        ],
    )

    main()

    captured = capsys.readouterr()

    assert "database.py [Python]  [2.0 KB]" in captured.out
    assert "main.py" not in captured.out



# Tests that hidden files are still excluded from search unless --hidden is used.
def test_search_respects_hidden_option(tmp_path, capsys):
    hidden_file = tmp_path / ".database.py"
    hidden_file.touch()

    tree = DirectoryTree(tmp_path, search="database")
    tree.generate()

    captured = capsys.readouterr()

    assert ".database.py" not in captured.out



# Tests that hidden matching files can be found when hidden files are enabled.
def test_search_with_hidden_option(tmp_path, capsys):
    hidden_file = tmp_path / ".database.py"
    hidden_file.touch()

    tree = DirectoryTree(
        tmp_path,
        search="database",
        hidden=True,
    )
    tree.generate()

    captured = capsys.readouterr()

    assert ".database.py" in captured.out



# Tests that a file's modification time is returned in the expected format.
def test_get_modified_time(tmp_path):
    file = tmp_path / "example.txt"
    file.touch()

    modified_time = get_modified_time(file)

    assert len(modified_time) == 16
    assert modified_time[2] == "/"
    assert modified_time[5] == "/"
    assert modified_time[10] == " "
    assert modified_time[13] == ":"



# Tests that the modification time uses the file's actual modification timestamp.
def test_get_modified_time_matches_file_timestamp(tmp_path):
    file = tmp_path / "example.txt"
    file.touch()

    expected_time = datetime.fromtimestamp(
        file.stat().st_mtime
    ).strftime("%d/%m/%Y %H:%M")

    assert get_modified_time(file) == expected_time



# Tests that the modified option displays a file's modification time.
def test_modified_option_shows_modified_time(tmp_path, capsys):
    file = tmp_path / "example.py"
    file.touch()

    tree = DirectoryTree(
        tmp_path,
        modified=True,
    )
    tree.generate()

    expected_time = get_modified_time(file)

    captured = capsys.readouterr()

    assert f"example.py [Modified: {expected_time}]" in captured.out



# Tests that the modified option does not add information to directories.
def test_modified_option_does_not_label_directories(tmp_path, capsys):
    directory = tmp_path / "example"
    directory.mkdir()

    tree = DirectoryTree(
        tmp_path,
        modified=True,
    )
    tree.generate()

    captured = capsys.readouterr()

    assert "example/ [Modified:" not in captured.out



# Tests that modification times are not shown unless the modified option is enabled.
def test_modified_option_disabled_by_default(tmp_path, capsys):
    file = tmp_path / "example.py"
    file.touch()

    tree = DirectoryTree(tmp_path)
    tree.generate()

    captured = capsys.readouterr()

    assert "[Modified:" not in captured.out



# Tests that the modified option works through the command-line interface.
def test_cli_modified(tmp_path, capsys, monkeypatch):
    file = tmp_path / "example.py"
    file.touch()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--modified", str(tmp_path)],
    )

    main()

    expected_time = get_modified_time(file)

    captured = capsys.readouterr()

    assert f"example.py [Modified: {expected_time}]" in captured.out



# Tests that the modified option works together with the type option.
def test_cli_modified_and_type(tmp_path, capsys, monkeypatch):
    file = tmp_path / "example.py"
    file.touch()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--modified", "--type", str(tmp_path)],
    )

    main()

    expected_time = get_modified_time(file)

    captured = capsys.readouterr()

    assert (
        f"example.py [Python]  [Modified: {expected_time}]"
        in captured.out
    )



# Tests that the modified option works together with the size option.
def test_cli_modified_and_size(tmp_path, capsys, monkeypatch):
    file = tmp_path / "example.py"
    file.write_bytes(b"a" * 2048)

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--modified", "--size", str(tmp_path)],
    )

    main()

    expected_time = get_modified_time(file)

    captured = capsys.readouterr()

    assert (
        f"example.py [2.0 KB]  [Modified: {expected_time}]"
        in captured.out
    )



# Tests that the modified option works together with search.
def test_cli_modified_and_search(tmp_path, capsys, monkeypatch):
    matching_file = tmp_path / "database.py"
    matching_file.touch()

    unrelated_file = tmp_path / "main.py"
    unrelated_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", "--modified", "--search", "database", str(tmp_path)],
    )

    main()

    expected_time = get_modified_time(matching_file)

    captured = capsys.readouterr()

    assert f"database.py [Modified: {expected_time}]" in captured.out
    assert "main.py" not in captured.out



# Tests that all file information options work together.
def test_cli_type_size_modified_search(
    tmp_path,
    capsys,
    monkeypatch,
):
    matching_file = tmp_path / "database.py"
    matching_file.write_bytes(b"a" * 2048)

    unrelated_file = tmp_path / "main.py"
    unrelated_file.write_bytes(b"b" * 1024)

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            "--type",
            "--size",
            "--modified",
            "--search",
            "database",
            str(tmp_path),
        ],
    )

    main()

    expected_time = get_modified_time(matching_file)

    captured = capsys.readouterr()

    assert (
        f"database.py [Python]  [2.0 KB]  "
        f"[Modified: {expected_time}]"
        in captured.out
    )

    assert "main.py" not in captured.out



# Test that a JSON tree correctly represents a directory and its files.
def test_build_json_tree(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    src = project / "src"
    src.mkdir()

    main_file = src / "main.py"
    main_file.write_text("print('hello')")

    readme = project / "README.md"
    readme.write_text("# Project")

    generator = _TreeGenerator(project)

    result = generator._build_json_tree(project)

    assert result == {
        "name": "project",
        "type": "directory",
        "children": [
            {
                "name": "src",
                "type": "directory",
                "children": [
                    {
                        "name": "main.py",
                        "type": "file",
                    }
                ],
            },
            {
                "name": "README.md",
                "type": "file",
            },
        ],
    }



# Test that an empty directory produces a JSON tree with no children.
def test_build_json_tree_empty_directory(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    generator = _TreeGenerator(project)

    result = generator._build_json_tree(project)

    assert result == {
        "name": "project",
        "type": "directory",
        "children": [],
    }



# Test that nested directories are recursively represented in the JSON tree.
def test_build_json_tree_nested_directories(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    src = project / "src"
    src.mkdir()

    backend = src / "backend"
    backend.mkdir()

    database = backend / "database"
    database.mkdir()

    file = database / "models.py"
    file.write_text("class User:")

    generator = _TreeGenerator(project)

    result = generator._build_json_tree(project)

    assert result["children"][0]["name"] == "src"
    assert result["children"][0]["children"][0]["name"] == "backend"
    assert (
        result["children"][0]["children"][0]["children"][0]["name"]
        == "database"
    )



# Test that the JSON tree hides hidden files by default.
def test_build_json_tree_hides_hidden_files(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    visible = project / "visible.py"
    visible.write_text("print('visible')")

    hidden = project / ".hidden"
    hidden.write_text("hidden")

    generator = _TreeGenerator(project)

    result = generator._build_json_tree(project)

    names = [child["name"] for child in result["children"]]

    assert "visible.py" in names
    assert ".hidden" not in names



# Test that the JSON tree includes hidden files when hidden mode is enabled.
def test_build_json_tree_shows_hidden_files(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    visible = project / "visible.py"
    visible.write_text("print('visible')")

    hidden = project / ".hidden"
    hidden.write_text("hidden")

    generator = _TreeGenerator(
        project,
        hidden=True,
    )

    result = generator._build_json_tree(project)

    names = [child["name"] for child in result["children"]]

    assert "visible.py" in names
    assert ".hidden" in names



# Test that the JSON tree recursively includes nested hidden files when hidden mode is enabled.
def test_build_json_tree_shows_nested_hidden_files(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    src = project / "src"
    src.mkdir()

    hidden = src / ".config"
    hidden.write_text("hidden")

    generator = _TreeGenerator(
        project,
        hidden=True,
    )

    result = generator._build_json_tree(project)

    src_result = result["children"][0]

    assert src_result["name"] == "src"
    assert src_result["children"][0]["name"] == ".config"



# Test that JSON output with files_only includes files inside nested directories.
def test_build_json_tree_files_only(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    src = project / "src"
    src.mkdir()

    main_file = src / "main.py"
    main_file.write_text("print('hello')")

    readme = project / "README.md"
    readme.write_text("# Project")

    generator = _TreeGenerator(
        project,
        files_only=True,
    )

    result = generator._build_json_tree(project)

    names = [child["name"] for child in result["children"]]

    assert "README.md" in names
    assert "src" not in names



# Test that JSON output with dirs_only includes directories but not files.
def test_build_json_tree_dirs_only(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    src = project / "src"
    src.mkdir()

    readme = project / "README.md"
    readme.write_text("# Project")

    generator = _TreeGenerator(
        project,
        dirs_only=True,
    )

    result = generator._build_json_tree(project)

    names = [child["name"] for child in result["children"]]

    assert "src" in names
    assert "README.md" not in names



# Test that JSON output with files_only recursively finds files inside directories.
def test_build_json_tree_files_only_nested(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    src = project / "src"
    src.mkdir()

    backend = src / "backend"
    backend.mkdir()

    main_file = backend / "main.py"
    main_file.write_text("print('hello')")

    generator = _TreeGenerator(
        project,
        files_only=True,
    )

    result = generator._build_json_tree(project)

    assert result["children"] == [
        {
            "name": "main.py",
            "type": "file",
        }
    ]



# Test that JSON output with dirs_only recursively includes directories.
def test_build_json_tree_dirs_only_nested(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    src = project / "src"
    src.mkdir()

    backend = src / "backend"
    backend.mkdir()

    main_file = backend / "main.py"
    main_file.write_text("print('hello')")

    generator = _TreeGenerator(
        project,
        dirs_only=True,
    )

    result = generator._build_json_tree(project)

    assert result["children"][0]["name"] == "src"
    assert result["children"][0]["type"] == "directory"

    assert result["children"][0]["children"][0]["name"] == "backend"
    assert result["children"][0]["children"][0]["type"] == "directory"

    assert result["children"][0]["children"][0]["children"] == []



# Test that the CLI outputs valid JSON when the --json option is used.
def test_cli_json(capsys, monkeypatch, tmp_path):
    file1 = tmp_path / "file1.txt"
    folder = tmp_path / "folder"

    file1.touch()
    folder.mkdir()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", str(tmp_path), "--json"],
    )

    main()

    captured = capsys.readouterr()

    result = json.loads(captured.out)

    assert result["name"] == tmp_path.name
    assert result["type"] == "directory"
    assert len(result["children"]) == 2



# Test that the CLI includes hidden files when --json and --hidden are used together.
def test_cli_json_hidden(capsys, monkeypatch, tmp_path):
    visible_file = tmp_path / "visible.txt"
    hidden_file = tmp_path / ".hidden.txt"

    visible_file.touch()
    hidden_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", str(tmp_path), "--json", "--hidden"],
    )

    main()

    captured = capsys.readouterr()

    result = json.loads(captured.out)

    names = [
        child["name"]
        for child in result["children"]
    ]

    assert "visible.txt" in names
    assert ".hidden.txt" in names



# Test that the CLI outputs only files when --json and --files are used together.
def test_cli_json_files(capsys, monkeypatch, tmp_path):
    file1 = tmp_path / "file1.txt"
    folder = tmp_path / "folder"

    file1.touch()
    folder.mkdir()

    nested_file = folder / "nested.txt"
    nested_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", str(tmp_path), "--json", "--files"],
    )

    main()

    captured = capsys.readouterr()

    result = json.loads(captured.out)

    names = [
        child["name"]
        for child in result["children"]
    ]

    assert "file1.txt" in names
    assert "nested.txt" in names
    assert "folder" not in names



# Test that the CLI outputs only directories when --json and --dirs are used together.
def test_cli_json_dirs(capsys, monkeypatch, tmp_path):
    file1 = tmp_path / "file1.txt"
    folder = tmp_path / "folder"

    file1.touch()
    folder.mkdir()

    nested_folder = folder / "nested"
    nested_folder.mkdir()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", str(tmp_path), "--json", "--dirs"],
    )

    main()

    captured = capsys.readouterr()

    result = json.loads(captured.out)

    names = [
        child["name"]
        for child in result["children"]
    ]

    assert "folder" in names
    assert "file1.txt" not in names

    nested_names = [
        child["name"]
        for child in result["children"][0]["children"]
    ]

    assert "nested" in nested_names



# Test that the CLI includes file types when --json and --type are used together.
def test_cli_json_type(capsys, monkeypatch, tmp_path):
    python_file = tmp_path / "script.py"
    text_file = tmp_path / "notes.txt"

    python_file.touch()
    text_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", str(tmp_path), "--json", "--type"],
    )

    main()

    captured = capsys.readouterr()

    result = json.loads(captured.out)

    children = {
        child["name"]: child
        for child in result["children"]
    }

    assert children["script.py"]["type"] == "file"
    assert children["script.py"]["file_type"] == "Python"

    assert children["notes.txt"]["type"] == "file"
    assert children["notes.txt"]["file_type"] == "Text"



# Test that the CLI includes file sizes when --json and --size are used together.
def test_cli_json_size(capsys, monkeypatch, tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"a" * 2048)

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", str(tmp_path), "--json", "--size"],
    )

    main()

    captured = capsys.readouterr()

    result = json.loads(captured.out)

    children = {
        child["name"]: child
        for child in result["children"]
    }

    assert children["test.txt"]["type"] == "file"
    assert children["test.txt"]["size"] == "2.0 KB"



# Test that the CLI includes file modification times when --json and --modified are used together.
def test_cli_json_modified(capsys, monkeypatch, tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        ["rptree", str(tmp_path), "--json", "--modified"],
    )

    main()

    captured = capsys.readouterr()

    result = json.loads(captured.out)

    children = {
        child["name"]: child
        for child in result["children"]
    }

    assert children["test.txt"]["type"] == "file"
    assert "modified" in children["test.txt"]
    assert len(children["test.txt"]["modified"]) == 16



# Test that the CLI includes all file metadata when JSON and every metadata option are used together.
def test_cli_json_all_metadata(capsys, monkeypatch, tmp_path):
    test_file = tmp_path / "script.py"
    test_file.write_bytes(b"a" * 2048)

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--json",
            "--type",
            "--size",
            "--modified",
        ],
    )

    main()

    captured = capsys.readouterr()

    result = json.loads(captured.out)

    child = result["children"][0]

    assert child["name"] == "script.py"
    assert child["type"] == "file"
    assert child["file_type"] == "Python"
    assert child["size"] == "2.0 KB"
    assert "modified" in child
    assert len(child["modified"]) == 16



# Test that the CLI applies filename searching when JSON output is enabled.
def test_cli_json_search(capsys, monkeypatch, tmp_path):
    matching_file = tmp_path / "important.py"
    other_file = tmp_path / "notes.txt"
    folder = tmp_path / "src"

    matching_file.touch()
    other_file.touch()
    folder.mkdir()

    nested_match = folder / "important_helper.py"
    nested_other = folder / "other.py"

    nested_match.touch()
    nested_other.touch()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--json",
            "--search",
            "important",
        ],
    )

    main()

    captured = capsys.readouterr()

    result = json.loads(captured.out)

    names = [
        child["name"]
        for child in result["children"]
    ]

    assert "important.py" in names
    assert "notes.txt" not in names
    assert "src" in names

    src = next(
        child
        for child in result["children"]
        if child["name"] == "src"
    )

    nested_names = [
        child["name"]
        for child in src["children"]
    ]

    assert "important_helper.py" in nested_names
    assert "other.py" not in nested_names



# Test that JSON output correctly combines search, hidden files, and all file metadata options.
def test_cli_json_all_options(capsys, monkeypatch, tmp_path):
    matching_file = tmp_path / "important.py"
    hidden_file = tmp_path / ".important.py"
    other_file = tmp_path / "notes.txt"
    folder = tmp_path / "src"

    matching_file.write_bytes(b"a" * 2048)
    hidden_file.touch()
    other_file.touch()
    folder.mkdir()

    nested_match = folder / "important_helper.py"
    nested_match.touch()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--json",
            "--hidden",
            "--search",
            "important",
            "--type",
            "--size",
            "--modified",
        ],
    )

    main()

    captured = capsys.readouterr()

    result = json.loads(captured.out)

    children = {
        child["name"]: child
        for child in result["children"]
    }

    assert "important.py" in children
    assert ".important.py" in children
    assert "notes.txt" not in children
    assert "src" in children

    important = children["important.py"]

    assert important["type"] == "file"
    assert important["file_type"] == "Python"
    assert important["size"] == "2.0 KB"
    assert "modified" in important

    src = children["src"]

    nested_names = [
        child["name"]
        for child in src["children"]
    ]

    assert "important_helper.py" in nested_names



# Test that the CLI writes JSON output to a file when --json and --output are used together.
def test_cli_json_output_file(capsys, monkeypatch, tmp_path):
    test_file = tmp_path / "test.txt"
    output_file = tmp_path / "tree.json"

    test_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--json",
            "--output",
            str(output_file),
        ],
    )

    main()

    captured = capsys.readouterr()

    assert captured.out == ""
    assert output_file.exists()

    with open(output_file) as file:
        result = json.load(file)

    assert result["name"] == tmp_path.name
    assert result["type"] == "directory"

    names = [
        child["name"]
        for child in result["children"]
    ]

    assert "test.txt" in names



# Test that --output overwrites an existing output file with the new JSON tree.
def test_cli_json_output_overwrites_existing_file(capsys, monkeypatch, tmp_path):
    test_file = tmp_path / "test.txt"
    output_file = tmp_path / "tree.json"

    test_file.touch()
    output_file.write_text("old content")

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--json",
            "--output",
            str(output_file),
        ],
    )

    main()

    captured = capsys.readouterr()

    assert captured.out == ""

    with open(output_file) as file:
        result = json.load(file)

    assert result["name"] == tmp_path.name
    assert result["type"] == "directory"

    names = [
        child["name"]
        for child in result["children"]
    ]

    assert "test.txt" in names



# Test that --output works correctly when combined with all JSON metadata and filtering options.
def test_cli_json_output_all_options(capsys, monkeypatch, tmp_path):
    test_file = tmp_path / "example.py"
    hidden_file = tmp_path / ".hidden.py"
    output_file = tmp_path / "tree.json"

    test_file.write_text("print('hello')")
    hidden_file.write_text("print('hidden')")

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--json",
            "--output",
            str(output_file),
            "--hidden",
            "--type",
            "--size",
            "--modified",
            "--search",
            "py",
        ],
    )

    main()

    captured = capsys.readouterr()

    assert captured.out == ""
    assert output_file.exists()

    with open(output_file) as file:
        result = json.load(file)

    names = [
        child["name"]
        for child in result["children"]
    ]

    assert "example.py" in names
    assert ".hidden.py" in names

    example_file = next(
        child
        for child in result["children"]
        if child["name"] == "example.py"
    )

    assert example_file["type"] == "file"
    assert example_file["file_type"] == "Python"
    assert "size" in example_file
    assert "modified" in example_file



# Check that statistics correctly count files, directories, total size, and file types.
def test_build_statistics(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    python_file = root / "main.py"
    text_file = root / "notes.txt"
    java_file = root / "Main.java"

    python_file.write_text("print('hello')")
    text_file.write_text("hello")
    java_file.write_text("public class Main {}")

    generator = _TreeGenerator(root)

    statistics = generator._build_statistics(root)

    assert statistics["files"] == 3
    assert statistics["directories"] == 0

    expected_size = (
        python_file.stat().st_size
        + text_file.stat().st_size
        + java_file.stat().st_size
    )

    assert statistics["total_size"] == expected_size

    assert statistics["file_types"] == {
        "Python": {
            "count": 1,
            "size": python_file.stat().st_size,
        },
        "Text": {
            "count": 1,
            "size": text_file.stat().st_size,
        },
        "Java": {
            "count": 1,
            "size": java_file.stat().st_size,
        },
    }


# Test that an empty directory produces zero files, directories, and total size.
def test_build_statistics_empty_directory(tmp_path):
    generator = _TreeGenerator(tmp_path)

    statistics = generator._build_statistics(tmp_path)

    assert statistics == {
        "files": 0,
        "directories": 0,
        "total_size": 0,
        "file_types": {},
    }


# Check that statistics correctly include files and directories nested inside other directories.
def test_build_statistics_nested_directories(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    src = root / "src"
    src.mkdir()

    python_file = src / "main.py"
    text_file = src / "notes.txt"

    python_file.write_text("print('hello')")
    text_file.write_text("hello")

    generator = _TreeGenerator(root)

    statistics = generator._build_statistics(root)

    assert statistics["files"] == 2
    assert statistics["directories"] == 1

    expected_size = (
        python_file.stat().st_size
        + text_file.stat().st_size
    )

    assert statistics["total_size"] == expected_size

    assert statistics["file_types"] == {
        "Python": {
            "count": 1,
            "size": python_file.stat().st_size,
        },
        "Text": {
            "count": 1,
            "size": text_file.stat().st_size,
        },
    }


# Test that statistics only include files matching the search term.
def test_build_statistics_search(tmp_path):
    matching_file = tmp_path / "main.py"
    unrelated_file = tmp_path / "notes.txt"

    matching_file.write_text("print('hello')")
    unrelated_file.write_text("hello")

    generator = _TreeGenerator(
        tmp_path,
        search="main",
    )

    statistics = generator._build_statistics(tmp_path)

    assert statistics["files"] == 1
    assert statistics["directories"] == 0
    assert statistics["total_size"] == matching_file.stat().st_size

    assert statistics["file_types"] == {
        "Python": {
            "count": 1,
            "size": matching_file.stat().st_size,
        },
    }


# Test that statistics find matching files inside nested directories when searching.
def test_build_statistics_nested_search(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    matching_file = src / "main.py"
    unrelated_file = src / "notes.txt"

    matching_file.write_text("print('hello')")
    unrelated_file.write_text("hello")

    generator = _TreeGenerator(
        tmp_path,
        search="main",
    )

    statistics = generator._build_statistics(tmp_path)

    assert statistics["files"] == 1
    assert statistics["directories"] == 1
    assert statistics["total_size"] == matching_file.stat().st_size

    assert statistics["file_types"] == {
        "Python": {
            "count": 1,
            "size": matching_file.stat().st_size,
        },
    }


# Test that hidden files are excluded by default and included when hidden mode is enabled.
def test_build_statistics_hidden_files(tmp_path):
    visible_file = tmp_path / "visible.py"
    hidden_file = tmp_path / ".hidden.py"

    visible_file.write_text("visible")
    hidden_file.write_text("hidden")

    generator = _TreeGenerator(tmp_path)

    statistics = generator._build_statistics(tmp_path)

    assert statistics["files"] == 1

    generator = _TreeGenerator(
        tmp_path,
        hidden=True,
    )

    statistics = generator._build_statistics(tmp_path)

    assert statistics["files"] == 2


# Test that files-only statistics include nested files but do not count directories.
def test_build_statistics_files_only(tmp_path):
    directory = tmp_path / "folder"
    directory.mkdir()

    file = directory / "test.py"
    file.write_text("hello")

    generator = _TreeGenerator(
        tmp_path,
        files_only=True,
    )

    statistics = generator._build_statistics(tmp_path)

    assert statistics["files"] == 1
    assert statistics["directories"] == 0
    assert statistics["total_size"] == file.stat().st_size

    assert statistics["file_types"] == {
        "Python": {
            "count": 1,
            "size": file.stat().st_size,
        },
    }


# Test that directories-only statistics count directories but exclude files.
def test_build_statistics_dirs_only(tmp_path):
    directory = tmp_path / "folder"
    directory.mkdir()

    file = directory / "test.py"
    file.write_text("hello")

    generator = _TreeGenerator(
        tmp_path,
        dirs_only=True,
    )

    statistics = generator._build_statistics(tmp_path)

    assert statistics["files"] == 0
    assert statistics["directories"] == 1
    assert statistics["total_size"] == 0
    assert statistics["file_types"] == {}


# Test that files with unknown extensions are counted under the Unknown file type.
def test_build_statistics_unknown_file_type(tmp_path):
    unknown_file = tmp_path / "data.xyz"
    unknown_file.write_text("some data")

    generator = _TreeGenerator(tmp_path)

    statistics = generator._build_statistics(tmp_path)

    assert statistics["files"] == 1
    assert statistics["total_size"] == unknown_file.stat().st_size

    assert statistics["file_types"] == {
        "Unknown": {
            "count": 1,
            "size": unknown_file.stat().st_size,
        },
    }


# Test that multiple files of the same type have their counts and sizes combined.
def test_build_statistics_multiple_same_file_type(tmp_path):
    first_python_file = tmp_path / "main.py"
    second_python_file = tmp_path / "utils.py"

    first_python_file.write_text("print('hello')")
    second_python_file.write_text("print('world')")

    generator = _TreeGenerator(tmp_path)

    statistics = generator._build_statistics(tmp_path)

    expected_size = (
        first_python_file.stat().st_size
        + second_python_file.stat().st_size
    )

    assert statistics["files"] == 2
    assert statistics["total_size"] == expected_size

    assert statistics["file_types"] == {
        "Python": {
            "count": 2,
            "size": expected_size,
        },
    }


# Test that file types from nested directories are combined correctly.
def test_build_statistics_nested_file_types(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    python_file = src / "main.py"
    java_file = tmp_path / "Main.java"

    python_file.write_text("print('hello')")
    java_file.write_text("public class Main {}")

    generator = _TreeGenerator(tmp_path)

    statistics = generator._build_statistics(tmp_path)

    expected_size = (
        python_file.stat().st_size
        + java_file.stat().st_size
    )

    assert statistics["files"] == 2
    assert statistics["directories"] == 1
    assert statistics["total_size"] == expected_size

    assert statistics["file_types"] == {
        "Python": {
            "count": 1,
            "size": python_file.stat().st_size,
        },
        "Java": {
            "count": 1,
            "size": java_file.stat().st_size,
        },
    }


# Test that statistics correctly calculate the total size of nested files.
def test_build_statistics_nested_total_size(tmp_path):
    directory = tmp_path / "src"
    directory.mkdir()

    file_one = directory / "one.txt"
    file_two = directory / "two.txt"

    file_one.write_bytes(b"a" * 1024)
    file_two.write_bytes(b"b" * 2048)

    generator = _TreeGenerator(tmp_path)

    statistics = generator._build_statistics(tmp_path)

    assert statistics["total_size"] == 3072


# Test that format_size returns bytes for values below 1 KB.
def test_format_size_bytes():
    assert format_size(500) == "500 B"



# Test that format_size converts bytes into kilobytes.
def test_format_size_kilobytes():
    assert format_size(2048) == "2.0 KB"



# Test that format_size converts bytes into megabytes.
def test_format_size_megabytes():
    assert format_size(2 * 1024**2) == "2.0 MB"



# Test that format_size converts bytes into gigabytes.
def test_format_size_gigabytes():
    assert format_size(2 * 1024**3) == "2.0 GB"



# Test that format_size correctly handles exactly 1 KB.
def test_format_size_exactly_one_kilobyte():
    assert format_size(1024) == "1.0 KB"



# Test that format_size correctly handles exactly 1 MB.
def test_format_size_exactly_one_megabyte():
    assert format_size(1024**2) == "1.0 MB"



# Test that format_size correctly handles exactly 1 GB.
def test_format_size_exactly_one_gigabyte():
    assert format_size(1024**3) == "1.0 GB"



# Test that statistics count files correctly when --stats is used.
def test_cli_stats_file_count(capsys, monkeypatch, tmp_path):
    file_one = tmp_path / "one.txt"
    file_two = tmp_path / "two.txt"

    file_one.touch()
    file_two.touch()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--stats",
        ],
    )

    main()

    captured = capsys.readouterr()

    assert "Files.     :  2" in captured.out



# Test that --stats does not also print the normal directory tree.
def test_cli_stats_does_not_print_tree(capsys, monkeypatch, tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--stats",
        ],
    )

    main()

    captured = capsys.readouterr()

    assert "Files.     :" in captured.out
    assert "Directories:" in captured.out
    assert "Total size :" in captured.out
    assert "File types:" in captured.out

    assert "└── test.txt" not in captured.out
    assert "├── test.txt" not in captured.out



# Test that --stats handles a directory containing no files.
def test_cli_stats_no_files(capsys, monkeypatch, tmp_path):
    (tmp_path / "directory").mkdir()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--stats",
        ],
    )

    main()

    captured = capsys.readouterr()

    assert "Files.     :  0" in captured.out
    assert "Directories:  1" in captured.out
    assert "Total size :  0 B" in captured.out



# Test that --stats does not crash when there are no file types to display.
def test_cli_stats_no_file_types_does_not_crash(
    capsys,
    monkeypatch,
    tmp_path,
):
    (tmp_path / "directory").mkdir()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--stats",
        ],
    )

    main()

    captured = capsys.readouterr()

    assert "File types:" in captured.out
    assert "Traceback" not in captured.out



# Test that --stats respects the --hidden option.
def test_cli_stats_hidden(capsys, monkeypatch, tmp_path):
    visible_file = tmp_path / "visible.txt"
    hidden_file = tmp_path / ".hidden.txt"

    visible_file.touch()
    hidden_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--stats",
            "--hidden",
        ],
    )

    main()

    captured = capsys.readouterr()

    assert "Files.     :  2" in captured.out



# Test that --stats excludes hidden files by default.
def test_cli_stats_hidden_excluded_by_default(
    capsys,
    monkeypatch,
    tmp_path,
):
    visible_file = tmp_path / "visible.txt"
    hidden_file = tmp_path / ".hidden.txt"

    visible_file.touch()
    hidden_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--stats",
        ],
    )

    main()

    captured = capsys.readouterr()

    assert "Files.     :  1" in captured.out



# Test that --stats respects the --files option.
def test_cli_stats_files_only(capsys, monkeypatch, tmp_path):
    test_file = tmp_path / "test.txt"
    test_directory = tmp_path / "directory"

    test_file.touch()
    test_directory.mkdir()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--stats",
            "--files",
        ],
    )

    main()

    captured = capsys.readouterr()

    assert "Files.     :  1" in captured.out
    assert "Directories:  0" in captured.out



# Test that --stats respects the --dirs option.
def test_cli_stats_dirs_only(capsys, monkeypatch, tmp_path):
    test_file = tmp_path / "test.txt"
    test_directory = tmp_path / "directory"

    test_file.touch()
    test_directory.mkdir()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--stats",
            "--dirs",
        ],
    )

    main()

    captured = capsys.readouterr()

    assert "Files.     :  0" in captured.out
    assert "Directories:  1" in captured.out



# Test that --stats respects the --search option.
def test_cli_stats_search(capsys, monkeypatch, tmp_path):
    matching_file = tmp_path / "example.py"
    non_matching_file = tmp_path / "notes.txt"

    matching_file.touch()
    non_matching_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--stats",
            "--search",
            "py",
        ],
    )

    main()

    captured = capsys.readouterr()

    assert "Files.     :  1" in captured.out



# Test that --stats search finds matching files inside nested directories.
def test_cli_stats_nested_search(capsys, monkeypatch, tmp_path):
    nested_directory = tmp_path / "project"
    nested_directory.mkdir()

    matching_file = nested_directory / "main.py"
    matching_file.touch()

    non_matching_file = nested_directory / "notes.txt"
    non_matching_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--stats",
            "--search",
            "py",
        ],
    )

    main()

    captured = capsys.readouterr()

    assert "Files.     :  1" in captured.out
    assert "Directories:  1" in captured.out



# Test that --stats works with multiple filtering options together.
def test_cli_stats_combined_options(capsys, monkeypatch, tmp_path):
    python_file = tmp_path / "example.py"
    hidden_python_file = tmp_path / ".hidden.py"
    text_file = tmp_path / "notes.txt"

    python_file.write_bytes(b"a" * 2048)
    hidden_python_file.write_bytes(b"b" * 1024)
    text_file.write_bytes(b"c" * 512)

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--stats",
            "--hidden",
            "--search",
            "py",
        ],
    )

    main()

    captured = capsys.readouterr()

    assert "Files.     :  2" in captured.out
    assert "Directories:  0" in captured.out
    assert "Total size :  3.0 KB" in captured.out
    assert "File types:" in captured.out
    assert "Python : 2" in captured.out



# Check that statistics correctly include files and directories nested inside other directories.
def test_build_statistics_nested_directories(tmp_path):
    """Test statistics for nested directories."""

    root = tmp_path / "project"
    root.mkdir()

    src = root / "src"
    src.mkdir()

    python_file = src / "main.py"
    text_file = src / "notes.txt"

    python_file.write_text("print('hello')")
    text_file.write_text("hello")

    generator = _TreeGenerator(root)

    statistics = generator._build_statistics(root)

    assert statistics["files"] == 2
    assert statistics["directories"] == 1

    expected_size = (
        python_file.stat().st_size
        + text_file.stat().st_size
    )

    assert statistics["total_size"] == expected_size

    assert statistics["file_types"] == {
        "Python": {
            "count": 1,
            "size": python_file.stat().st_size,
        },
        "Text": {
            "count": 1,
            "size": text_file.stat().st_size,
        },
    }



# Check that statistics correctly include files and directories nested inside other directories.
def test_build_statistics_nested_directories(tmp_path):
    """Test statistics for nested directories."""

    root = tmp_path / "project"
    root.mkdir()

    src = root / "src"
    src.mkdir()

    python_file = src / "main.py"
    text_file = src / "notes.txt"

    python_file.write_text("print('hello')")
    text_file.write_text("hello")

    generator = _TreeGenerator(root)

    statistics = generator._build_statistics(root)

    assert statistics["files"] == 2
    assert statistics["directories"] == 1

    expected_size = (
        python_file.stat().st_size
        + text_file.stat().st_size
    )

    assert statistics["total_size"] == expected_size

    assert statistics["file_types"] == {
        "Python": {
            "count": 1,
            "size": python_file.stat().st_size,
        },
        "Text": {
            "count": 1,
            "size": text_file.stat().st_size,
        },
    }



# Check that statistics correctly include files and directories nested inside other directories.
def test_build_statistics_nested_directories(tmp_path):
    """Test statistics for nested directories."""

    root = tmp_path / "project"
    root.mkdir()

    src = root / "src"
    src.mkdir()

    python_file = src / "main.py"
    text_file = src / "notes.txt"

    python_file.write_text("print('hello')")
    text_file.write_text("hello")

    generator = _TreeGenerator(root)

    statistics = generator._build_statistics(root)

    assert statistics["files"] == 2
    assert statistics["directories"] == 1

    expected_size = (
        python_file.stat().st_size
        + text_file.stat().st_size
    )

    assert statistics["total_size"] == expected_size

    assert statistics["file_types"] == {
        "Python": {
            "count": 1,
            "size": python_file.stat().st_size,
        },
        "Text": {
            "count": 1,
            "size": text_file.stat().st_size,
        },
    }



# Test that statistics correctly calculate the total size of nested files.
def test_build_statistics_nested_total_size(tmp_path):
    directory = tmp_path / "src"
    directory.mkdir()

    file_one = directory / "one.txt"
    file_two = directory / "two.txt"

    file_one.write_bytes(b"a" * 1024)
    file_two.write_bytes(b"b" * 2048)

    generator = _TreeGenerator(tmp_path)

    statistics = generator._build_statistics(tmp_path)

    assert statistics["total_size"] == 3072



# Test that --stats displays file types in descending count order.
def test_cli_stats_file_type_order(capsys, monkeypatch, tmp_path):
    python_one = tmp_path / "one.py"
    python_two = tmp_path / "two.py"
    text_file = tmp_path / "notes.txt"

    python_one.touch()
    python_two.touch()
    text_file.touch()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--stats",
        ],
    )

    main()

    captured = capsys.readouterr()

    python_position = captured.out.index("Python")
    text_position = captured.out.index("Text")

    assert python_position < text_position



# Test that --stats always displays Unknown as the final file type.
def test_cli_stats_unknown_file_type_last(
    capsys,
    monkeypatch,
    tmp_path,
):
    python_file = tmp_path / "example.py"
    unknown_one = tmp_path / "one.xyz"
    unknown_two = tmp_path / "two.xyz"

    python_file.touch()
    unknown_one.touch()
    unknown_two.touch()

    monkeypatch.setattr(
        "sys.argv",
        [
            "rptree",
            str(tmp_path),
            "--stats",
        ],
    )

    main()

    captured = capsys.readouterr()

    python_position = captured.out.index("Python")
    unknown_position = captured.out.index("Unknown")

    assert python_position < unknown_position



# Test that depth=0 only displays the root directory.
def test_depth_zero(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    (root / "file.txt").write_text("hello")
    (root / "folder").mkdir()
    (root / "folder" / "nested.txt").write_text("hello")

    tree = DirectoryTree(root, depth=0)
    tree.generate()

    output = capsys.readouterr().out

    assert "project/" in output
    assert "file.txt" not in output
    assert "folder" not in output



# Test that depth=1 displays the root directory and its immediate contents.
def test_depth_one(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    (root / "file.txt").write_text("hello")
    (root / "folder").mkdir()
    (root / "folder" / "nested.txt").write_text("hello")

    tree = DirectoryTree(root, depth=1)
    tree.generate()

    output = capsys.readouterr().out

    assert "project/" in output
    assert "file.txt" in output
    assert "folder/" in output
    assert "nested.txt" not in output



# Test that a depth larger than the directory tree does not cause an error.
def test_depth_larger_than_tree(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    (root / "folder").mkdir()
    (root / "folder" / "file.txt").write_text("hello")

    tree = DirectoryTree(root, depth=100)
    tree.generate()

    output = capsys.readouterr().out

    assert "project/" in output
    assert "folder/" in output
    assert "file.txt" in output



# Test that a directory matching the search term is displayed.
def test_search_matching_directory(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    matching_directory = root / "important_files"
    matching_directory.mkdir()

    (matching_directory / "test.txt").write_text("hello")

    tree = DirectoryTree(root, search="important")
    tree.generate()

    output = capsys.readouterr().out

    assert "important_files/" in output



# Test that searching is case-insensitive.
def test_search_case_insensitive(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    (root / "MyFile.PY").write_text("print('hello')")

    tree = DirectoryTree(root, search="myfile")
    tree.generate()

    output = capsys.readouterr().out

    assert "MyFile.PY" in output



# Test that a search with no matches produces no matching files.
def test_search_no_matches(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    (root / "hello.txt").write_text("hello")
    (root / "world.txt").write_text("world")

    tree = DirectoryTree(root, search="does-not-exist")
    tree.generate()

    output = capsys.readouterr().out

    assert "hello.txt" not in output
    assert "world.txt" not in output



# Test that a directory is retained when a file deep inside it matches the search.
def test_search_deep_nested_match(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    source = root / "src"
    source.mkdir()

    nested = source / "components"
    nested.mkdir()

    (nested / "important.py").write_text("print('hello')")

    tree = DirectoryTree(root, search="important")
    tree.generate()

    output = capsys.readouterr().out

    assert "src/" in output
    assert "components/" in output
    assert "important.py" in output



# Test that files-only mode still finds matching files inside directories.
def test_files_only_with_search(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    source = root / "src"
    source.mkdir()

    (source / "main.py").write_text("print('hello')")
    (source / "notes.txt").write_text("notes")

    tree = DirectoryTree(
        root,
        files_only=True,
        search="main",
    )
    tree.generate()

    output = capsys.readouterr().out

    assert "main.py" in output
    assert "notes.txt" not in output
    assert "src/" not in output



# Test that dirs-only mode can be combined with searching.
def test_dirs_only_with_search(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    matching = root / "important_folder"
    matching.mkdir()

    other = root / "other_folder"
    other.mkdir()

    (other / "important.txt").write_text("hello")

    tree = DirectoryTree(
        root,
        dirs_only=True,
        search="important_folder",
    )
    tree.generate()

    output = capsys.readouterr().out

    assert "important_folder/" in output
    assert "other_folder/" not in output



# Test that the type filter is case-insensitive.
def test_type_filter_case_insensitive(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    (root / "main.py").write_text("print('hello')")

    tree = DirectoryTree(
        root,
        type_filter="PYTHON",
    )
    tree.generate()

    output = capsys.readouterr().out

    assert "main.py" in output



# Test that directories containing a matching file type are retained.
def test_type_filter_nested_directory(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    source = root / "src"
    source.mkdir()

    (source / "main.py").write_text("print('hello')")
    (source / "notes.txt").write_text("notes")

    docs = root / "docs"
    docs.mkdir()

    (docs / "README.md").write_text("# README")

    tree = DirectoryTree(
        root,
        type_filter="Python",
    )
    tree.generate()

    output = capsys.readouterr().out

    assert "src/" in output
    assert "main.py" in output
    assert "docs/" not in output
    assert "README.md" not in output



# Test that a type filter with no matching files produces no files.
def test_type_filter_no_matches(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    (root / "notes.txt").write_text("notes")
    (root / "README.md").write_text("# README")

    tree = DirectoryTree(
        root,
        type_filter="Python",
    )
    tree.generate()

    output = capsys.readouterr().out

    assert "notes.txt" not in output
    assert "README.md" not in output



# Test that type filtering can be combined with files-only mode.
def test_type_filter_with_files_only(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    source = root / "src"
    source.mkdir()

    (source / "main.py").write_text("print('hello')")
    (source / "notes.txt").write_text("notes")

    tree = DirectoryTree(
        root,
        files_only=True,
        type_filter="Python",
    )
    tree.generate()

    output = capsys.readouterr().out

    assert "main.py" in output
    assert "notes.txt" not in output
    assert "src/" not in output



# Test that type filtering can be combined with hidden files.
def test_type_filter_with_hidden_files(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    (root / ".hidden.py").write_text("print('hidden')")
    (root / "main.py").write_text("print('visible')")

    tree = DirectoryTree(
        root,
        type_filter="Python",
    )
    tree.generate()

    output = capsys.readouterr().out

    assert "main.py" in output
    assert ".hidden.py" not in output



# Test that hidden directories are excluded by default.
def test_hidden_directory_excluded(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    hidden = root / ".hidden"
    hidden.mkdir()

    (hidden / "secret.txt").write_text("secret")

    tree = DirectoryTree(root)
    tree.generate()

    output = capsys.readouterr().out

    assert ".hidden" not in output
    assert "secret.txt" not in output



# Test that hidden directories are displayed when hidden mode is enabled.
def test_hidden_directory_included(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    hidden = root / ".hidden"
    hidden.mkdir()

    (hidden / "secret.txt").write_text("secret")

    tree = DirectoryTree(
        root,
        hidden=True,
    )
    tree.generate()

    output = capsys.readouterr().out

    assert ".hidden/" in output
    assert "secret.txt" in output



# Test that a hidden directory containing a search match is only shown when hidden mode is enabled.
def test_hidden_directory_with_search(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    hidden = root / ".hidden"
    hidden.mkdir()

    (hidden / "important.txt").write_text("important")

    tree = DirectoryTree(
        root,
        search="important",
    )
    tree.generate()

    output = capsys.readouterr().out

    assert ".hidden" not in output

    tree = DirectoryTree(
        root,
        hidden=True,
        search="important",
    )
    tree.generate()

    output = capsys.readouterr().out

    assert ".hidden/" in output
    assert "important.txt" in output



# Test that modified time information is displayed when requested.
def test_modified_time_display(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    (root / "file.txt").write_text("hello")

    tree = DirectoryTree(
        root,
        modified=True,
    )
    tree.generate()

    output = capsys.readouterr().out

    assert "[Modified:" in output
    assert "file.txt" in output



# Test that get_modified_time returns Unavailable when stat raises an OSError.
def test_modified_time_unavailable(monkeypatch, tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("hello")

    original_stat = pathlib.Path.stat

    def raise_os_error(self):
        if self == file:
            raise OSError("Permission denied")

        return original_stat(self)

    monkeypatch.setattr(
        pathlib.Path,
        "stat",
        raise_os_error,
    )

    assert get_modified_time(file) == "Unavailable"


# Test that statistics handle a directory that cannot be accessed.
def test_build_statistics_inaccessible_directory(monkeypatch, tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    blocked = root / "blocked"
    blocked.mkdir()

    original_iterdir = pathlib.Path.iterdir

    def raise_for_blocked(self):
        if self == blocked:
            raise PermissionError("Permission denied")

        return original_iterdir(self)

    monkeypatch.setattr(
        pathlib.Path,
        "iterdir",
        raise_for_blocked,
    )

    generator = _TreeGenerator(root)

    statistics = generator._build_statistics(root)

    assert statistics["files"] == 0
    assert statistics["directories"] == 1



# Test that the tree generator skips an inaccessible directory without crashing.
def test_tree_inaccessible_directory(monkeypatch, tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    blocked = root / "blocked"
    blocked.mkdir()

    original_iterdir = pathlib.Path.iterdir

    def raise_for_blocked(self):
        if self == blocked:
            raise PermissionError("Permission denied")

        return original_iterdir(self)

    monkeypatch.setattr(
        pathlib.Path,
        "iterdir",
        raise_for_blocked,
    )

    generator = _TreeGenerator(root)

    tree = generator.build_tree()

    assert "project/" in tree
    assert any("blocked/" in entry for entry in tree)


# Test that statistics continue safely when a file disappears before stat is called.
def test_statistics_file_stat_error(monkeypatch, tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    file = root / "file.txt"
    file.write_text("hello")

    original_stat = pathlib.Path.stat

    def raise_for_file(self):
        if self == file:
            raise OSError("File disappeared")

        return original_stat(self)

    monkeypatch.setattr(
        pathlib.Path,
        "stat",
        raise_for_file,
    )

    generator = _TreeGenerator(root)

    statistics = generator._build_statistics(root)

    assert statistics["files"] == 1
    assert statistics["total_size"] == 0
    assert statistics["file_types"]["Text"]["count"] == 1
    assert statistics["file_types"]["Text"]["size"] == 0



# Test that a symlink is skipped instead of being recursively followed.
def test_symlink_is_skipped(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    folder = root / "folder"
    folder.mkdir()

    (folder / "file.txt").write_text("hello")

    link = root / "link"

    try:
        link.symlink_to(folder, target_is_directory=True)
    except OSError:
        pytest.skip("Symbolic links are not available")

    generator = _TreeGenerator(root)

    tree = generator.build_tree()

    assert any("folder/" in entry for entry in tree)
    assert not any("link" in entry for entry in tree)



# Test that a self-referencing symlink cannot cause recursive traversal.
def test_self_referencing_symlink_is_skipped(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    loop = root / "loop"

    try:
        loop.symlink_to(root, target_is_directory=True)
    except OSError:
        pytest.skip("Symbolic links are not available")

    generator = _TreeGenerator(root)

    tree = generator.build_tree()

    assert "project/" in tree
    assert not any("loop" in entry for entry in tree)



# Test that statistics do not count files through a symbolic link.
def test_statistics_skip_symlink(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    folder = root / "folder"
    folder.mkdir()

    (folder / "file.txt").write_text("hello")

    link = root / "link"

    try:
        link.symlink_to(folder, target_is_directory=True)
    except OSError:
        pytest.skip("Symbolic links are not available")

    generator = _TreeGenerator(root)

    statistics = generator._build_statistics(root)

    assert statistics["files"] == 1
    assert statistics["directories"] == 1



# Test that JSON generation skips symbolic links instead of following them.
def test_json_tree_skip_symlink(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    folder = root / "folder"
    folder.mkdir()

    (folder / "file.txt").write_text("hello")

    link = root / "link"

    try:
        link.symlink_to(folder, target_is_directory=True)
    except OSError:
        pytest.skip("Symbolic links are not available")

    generator = _TreeGenerator(root)

    tree = generator._build_json_tree(root)

    names = [child["name"] for child in tree["children"]]

    assert "folder" in names
    assert "link" not in names



# Test that statistics with --size include both file counts and total sizes for each file type.
def test_statistics_with_size(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    first = root / "one.txt"
    second = root / "two.txt"

    first.write_bytes(b"a" * 100)
    second.write_bytes(b"b" * 200)

    generator = _TreeGenerator(root, show_size=True)

    statistics = generator._build_statistics(root)

    assert statistics["file_types"]["Text"]["count"] == 2
    assert statistics["file_types"]["Text"]["size"] == 300
    assert statistics["total_size"] == 300



# Test that statistics respect the search filter when calculating file counts and sizes.
def test_statistics_search_with_size(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    matching = root / "important.txt"
    other = root / "other.txt"

    matching.write_bytes(b"a" * 100)
    other.write_bytes(b"b" * 200)

    generator = _TreeGenerator(
        root,
        search="important",
    )

    statistics = generator._build_statistics(root)

    assert statistics["files"] == 1
    assert statistics["total_size"] == 100
    assert statistics["file_types"]["Text"]["count"] == 1
    assert statistics["file_types"]["Text"]["size"] == 100



# Test that normal tree output can be written to a file.
def test_cli_output_file(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    file = root / "main.py"
    file.write_text("print('hello')")

    output_file = tmp_path / "tree.txt"

    generate_tree(
        root,
        None,
        False,
        False,
        False,
        False,
        None,
        False,
        None,
        False,
        False,
        str(output_file),
        False,
    )

    captured = capsys.readouterr()

    assert captured.out == ""
    assert output_file.exists()

    output = output_file.read_text()

    assert "project/" in output
    assert "main.py" in output



# Test that normal tree output written to a file contains the same tree content.
def test_cli_output_file_with_options(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    file = root / "main.py"
    file.write_text("print('hello')")

    output_file = tmp_path / "tree.txt"

    generate_tree(
        root,
        None,
        False,
        False,
        False,
        True,
        None,
        True,
        None,
        False,
        False,
        str(output_file),
        False,
    )

    captured = capsys.readouterr()

    assert captured.out == ""

    output = output_file.read_text()

    assert "main.py" in output
    assert "[Python]" in output
    assert "[Modified:" not in output



# Test that JSON output can be written to a file.
def test_cli_json_output_file(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    file = root / "main.py"
    file.write_text("print('hello')")

    output_file = tmp_path / "tree.json"

    generate_tree(
        root,
        None,
        False,
        False,
        False,
        False,
        None,
        False,
        None,
        False,
        True,
        str(output_file),
        False,
    )

    captured = capsys.readouterr()

    assert captured.out == ""
    assert output_file.exists()

    output = output_file.read_text()

    assert '"name": "project"' in output
    assert '"type": "directory"' in output
    assert '"name": "main.py"' in output
    assert '"type": "file"' in output



# Test that JSON output written to a file is valid JSON.
def test_cli_json_output_file_is_valid_json(tmp_path, capsys):
    import json

    root = tmp_path / "project"
    root.mkdir()

    file = root / "main.py"
    file.write_text("print('hello')")

    output_file = tmp_path / "tree.json"

    generate_tree(
        root,
        None,
        False,
        False,
        False,
        False,
        None,
        False,
        None,
        False,
        True,
        str(output_file),
        False,
    )

    capsys.readouterr()

    output = output_file.read_text()
    data = json.loads(output)

    assert data["name"] == "project"
    assert data["type"] == "directory"
    assert data["children"][0]["name"] == "main.py"



# Test that statistics output can be written to a file.
def test_cli_stats_output_file(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    file = root / "main.py"
    file.write_text("print('hello')")

    output_file = tmp_path / "stats.txt"

    generate_tree(
        root,
        None,
        False,
        False,
        False,
        False,
        None,
        False,
        None,
        False,
        False,
        str(output_file),
        True,
    )

    captured = capsys.readouterr()

    assert captured.out == ""
    assert output_file.exists()

    output = output_file.read_text()

    assert "project/" in output
    assert "Files." in output
    assert "Directories:" in output
    assert "Total size :" in output
    assert "File types:" in output
    assert "Python" in output



# Test that statistics output with file sizes can be written to a file.
def test_cli_stats_size_output_file(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    file = root / "main.py"
    file.write_text("print('hello')")

    output_file = tmp_path / "stats.txt"

    generate_tree(
        root,
        None,
        False,
        False,
        False,
        False,
        None,
        True,
        None,
        False,
        False,
        str(output_file),
        True,
    )

    captured = capsys.readouterr()

    assert captured.out == ""

    output = output_file.read_text()

    assert "File types:" in output
    assert "Python" in output
    assert "[" in output
    assert "]" in output



# Test that an existing output file is overwritten rather than appended to.
def test_cli_output_file_is_overwritten(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    file = root / "main.py"
    file.write_text("print('hello')")

    output_file = tmp_path / "tree.txt"
    output_file.write_text("OLD CONTENT")

    generate_tree(
        root,
        None,
        False,
        False,
        False,
        False,
        None,
        False,
        None,
        False,
        False,
        str(output_file),
        False,
    )

    capsys.readouterr()

    output = output_file.read_text()

    assert "OLD CONTENT" not in output
    assert "project/" in output
    assert "main.py" in output



# Test that output files are created when the requested path does not exist.
def test_cli_output_file_is_created(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    file = root / "main.py"
    file.write_text("print('hello')")

    output_directory = tmp_path / "output"
    output_file = output_directory / "tree.txt"

    output_directory.mkdir()

    generate_tree(
        root,
        None,
        False,
        False,
        False,
        False,
        None,
        False,
        None,
        False,
        False,
        str(output_file),
        False,
    )

    capsys.readouterr()

    assert output_file.exists()
    assert output_file.read_text() != ""



# Test that search options still work when the tree is written to a file.
def test_cli_output_file_with_search(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    matching_file = root / "database.py"
    matching_file.write_text("")

    unrelated_file = root / "main.py"
    unrelated_file.write_text("")

    output_file = tmp_path / "tree.txt"

    generate_tree(
        root,
        None,
        False,
        False,
        False,
        False,
        None,
        False,
        "database",
        False,
        False,
        str(output_file),
        False,
    )

    captured = capsys.readouterr()

    assert captured.out == ""

    output = output_file.read_text()

    assert "database.py" in output
    assert "main.py" not in output



# Test that type filtering still works when the tree is written to a file.
def test_cli_output_file_with_type_filter(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    python_file = root / "main.py"
    python_file.write_text("")

    text_file = root / "notes.txt"
    text_file.write_text("")

    output_file = tmp_path / "tree.txt"

    generate_tree(
        root,
        None,
        False,
        False,
        False,
        False,
        "Python",
        False,
        None,
        False,
        False,
        str(output_file),
        False,
    )

    captured = capsys.readouterr()

    assert captured.out == ""

    output = output_file.read_text()

    assert "main.py" in output
    assert "notes.txt" not in output



# Test that depth limiting still works when the tree is written to a file.
def test_cli_output_file_with_depth(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()

    source = root / "src"
    source.mkdir()

    file = source / "main.py"
    file.write_text("")

    output_file = tmp_path / "tree.txt"

    generate_tree(
        root,
        1,
        False,
        False,
        False,
        False,
        None,
        False,
        None,
        False,
        False,
        str(output_file),
        False,
    )

    captured = capsys.readouterr()

    assert captured.out == ""

    output = output_file.read_text()

    assert "project/" in output
    assert "src/" in output
    assert "main.py" not in output