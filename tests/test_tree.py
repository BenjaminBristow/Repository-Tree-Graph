from rptree.cli import main
from rptree.tree import DirectoryTree
from importlib.metadata import version


def test_empty_directory(tmp_path):
    tree = DirectoryTree(tmp_path)

    result = tree._generator.build_tree()

    assert result == [
        f"{tmp_path}/",
        "│",
    ]



def test_single_file(tmp_path):
    file1 = tmp_path / "file1.txt"
    file1.touch()

    tree = DirectoryTree(tmp_path)

    result = tree._generator.build_tree()

    assert "└── file1.txt" in result



def test_nested_directory(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()

    file1 = folder / "file1.txt"
    file1.touch()

    tree = DirectoryTree(tmp_path)

    result = tree._generator.build_tree()

    assert "└── folder/" in result
    assert "    └── file1.txt" in result



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



def test_cli_version(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["rptree", "--version"])

    try:
        main()
    except SystemExit:
        pass

    captured = capsys.readouterr()

    assert f"rptree v{version('rptree')}" in captured.out



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



def test_depth_limit_shows_one_ellipsis(tmp_path):
    folder = tmp_path / "folder"

    folder.mkdir()
    (folder / "file1.txt").touch()
    (folder / "file2.txt").touch()
    (folder / "another_folder").mkdir()

    tree = DirectoryTree(tmp_path, depth=1)

    result = tree._generator.build_tree()

    assert result.count("        ...") == 1



def test_depth_limit_empty_directory_no_ellipsis(tmp_path):
    folder = tmp_path / "empty"
    folder.mkdir()

    tree = DirectoryTree(tmp_path, depth=1)

    result = tree._generator.build_tree()

    assert "└── empty/" in result
    assert "..." not in result



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



def test_hidden_entries_are_hidden_by_default(tmp_path):
    visible_file = tmp_path / "visible.txt"
    hidden_file = tmp_path / ".hidden"

    visible_file.touch()
    hidden_file.touch()

    tree = DirectoryTree(tmp_path)

    result = tree._generator.build_tree()

    assert "visible.txt" in result[-1]
    assert not any(".hidden" in line for line in result)



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