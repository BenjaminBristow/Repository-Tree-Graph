from rptree.cli import main
from rptree.tree import DirectoryTree, get_file_type, get_file_size
from importlib.metadata import version


# Tests that an empty directory produces only the root directory and tree line.
def test_empty_directory(tmp_path):
    tree = DirectoryTree(tmp_path)
    result = tree._generator.build_tree()

    assert result == [
        f"{tmp_path}/",
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

    assert f"{tmp_path}/" in captured.out
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