from rptree.cli import main
from rptree.tree import DirectoryTree


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

    assert "rptree v1.0.1" in captured.out



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