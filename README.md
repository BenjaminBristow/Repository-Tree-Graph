# rptree

A simple Python command-line tool that generates a tree diagram of files and directories.

## What It Does

`rptree` takes a directory on your computer and displays its files and subdirectories in a tree structure.

For example:

```text
/Users/myusername/Projects/Repository-Tree-Graph/
│
├── rptree_dir/
│   ├── __init__.py
│   ├── rptree.py
│   └── cli.py
│
├── tree.py
├── README.md
└── .gitignore
```

## How To Use

Open a terminal and navigate to the project directory.

Run:

```bash
python3 tree.py <directory>
```

For example:

```bash
python3 tree.py //Users/myusername/Repository-Tree-Graph
```

On Windows, you can provide a Windows directory path:

```bash
python tree.py C:\Users\YourName\Repository-Tree-Graph
```

## Version

To display the current version:

```bash
python3 tree.py -v
```

or:

```bash
python3 tree.py --version
```

## Help

To display the available commands:

```bash
python3 tree.py -h
```

or:

```bash
python3 tree.py --help
```

## Current Features

* Generate a tree diagram of a directory
* Display files and subdirectories recursively
* Sort directory contents
* Command-line interface
* Version information
* Help information

## Project Structure

```text
Repository-Tree_Graph/
├── tree.py
├── rptree_dir/
│   ├── __init__.py
│   ├── cli.py
│   └── rptree.py
├── README.md
└── .gitignore
```
