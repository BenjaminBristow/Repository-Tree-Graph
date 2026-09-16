from rptree.cli import main
from importlib.metadata import version
from datetime import datetime
import json
from rptree.tree import (
    DirectoryTree,
    _TreeGenerator,
    get_file_type, 
    get_file_size, 
    get_modified_time
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