# rptree

A simple Python command-line tool that generates a tree diagram of files and directories.

## What It Does

`rptree` takes a directory on your computer and displays its files and subdirectories in a tree structure.

For example:

```text
/Users/myusername/Projects/Repository-Tree-Graph/
│
├── src/
│   └── rptree/
│       ├── __init__.py
│       ├── cli.py
│       └── tree.py
│
├── tests/
├── README.md
├── LICENSE
├── pyproject.toml
└── .gitignore
```

## Installation

Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/BenjaminBristow/Repository-Tree-Graph.git
cd Repository-Tree-Graph
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install `rptree`:

```bash
pip install .
```

The `rptree` command is then available in the virtual environment.

## How To Use

Run:

```bash
rptree <directory>
```

For example:

```bash
rptree /Users/myusername/Repository-Tree-Graph
```

If no directory is provided, `rptree` uses the current directory:

```bash
rptree
```

On Windows, you can provide a Windows directory path:

```bash
rptree C:\Users\YourName\Repository-Tree-Graph
```

## Version

To display the current version:

```bash
rptree -v
```

or:

```bash
rptree --version
```

## Help

To display the available commands:

```bash
rptree -h
```

or:

```bash
rptree --help
``
```
