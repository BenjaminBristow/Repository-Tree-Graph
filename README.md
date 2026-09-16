# rptree

A Python command-line tool that generates a tree diagram of files and directories.

`rptree` recursively explores a directory and displays its structure in a simple tree format. It supports depth limits, file and directory filtering, hidden files and directories, and can be installed as a Python command-line tool.

## Features

* Generate a tree diagram of files and directories
* Recursively display nested directories
* Sort files and directories alphabetically
* Limit the tree depth
* Show files only
* Show directories only
* Include hidden files and directories
* Command-line interface
* Version information
* Help information
* Automated tests
* Installable Python package

## Example

Running:

```bash
rptree .
```

Could produce:

```text
Repository-Tree-Graph/
│
├── src/
│   └── rptree/
│       ├── __init__.py
│       ├── cli.py
│       └── tree.py
│
├── tests/
│   └── test_tree.py
│
├── .gitignore
├── LICENSE
├── README.md
└── pyproject.toml
```

## Global Installation

`rptree` can be installed as a standalone command-line tool using `pipx`. This allows it to be used from any directory without activating a virtual environment.

### Install pipx

If `pipx` is not already installed, install it using Homebrew:

```bash
brew install pipx
```

Check that it is installed:

```bash
pipx --version
```

### Install rptree

Clone the repository and move into the project directory:

```bash
git clone https://github.com/BenjaminBristow/Repository-Tree-Graph.git
cd Repository-Tree-Graph
```

Install `rptree` using `pipx`:

```bash
pipx install .
```

If `pipx` reports that its application directory is not on your `PATH`, run:

```bash
pipx ensurepath
```

Then restart your terminal.

### Use rptree from anywhere

Once installed, `rptree` can be run from any directory:

```bash
cd ~/Desktop
rptree
```

Because `rptree` uses the current directory by default, this will generate a tree of the Desktop.

You can also specify a directory directly:

```bash
rptree ~/Documents
```

Check the installation with:

```bash
rptree --version
```

This installation method keeps `rptree` isolated from the system Python environment while making the command available globally.


## Development Installation 
This installation method is intended for development, testing, and making changes to the rptree source code using a virtual environment.

### Clone the repository

Clone the repository from GitHub:

```bash
git clone https://github.com/BenjaminBristow/Repository-Tree-Graph.git
```

Navigate into the project:

```bash
cd Repository-Tree-Graph
```

### Create a virtual environment

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### Install rptree

Install the package with:

```bash
pip install .
```

Once installed, the `rptree` command will be available inside the virtual environment.

## Getting Started

Once `rptree` is installed, you can run it from the terminal.

### Generate a tree

To generate a tree for the current directory:

```bash
rptree
```

You can also provide a directory:

```bash
rptree /path/to/directory
```

For example:

```bash
rptree ~/Projects
```

### Windows paths

On Windows, provide the directory path as normal:

```powershell
rptree C:\Users\YourName\Projects
```

## Command Options

### `--depth`

Limit how deep `rptree` recursively explores directories.

```bash
rptree --depth 2
```

Short option:

```bash
rptree -dp 2
```

For example, a depth limit can be useful when working with a large project where displaying every nested directory would produce too much output.

### `--files`

Show files only.

```bash
rptree --files
```

Short option:

```bash
rptree -f
```

Directories are still traversed so that files inside nested directories can be found.

### `--dirs`

Show directories only.

```bash
rptree --dirs
```

Short option:

```bash
rptree -d
```

Files are hidden from the output while directories remain visible.

### `--hidden`

Include hidden files and directories.

```bash
rptree --hidden
```

Short option:

```bash
rptree -hd
```

By default, hidden files and directories are not displayed.

For example, files such as:

```text
.gitignore
.env
```

and directories such as:

```text
.git/
```

are hidden unless `--hidden` is used.

### Combining options

The options can be combined.

For example:

```bash
rptree --files --depth 2
```

shows files up to a depth of 2.

You can also use the short options:

```bash
rptree -f -dp 2
```

Another example:

```bash
rptree --hidden --depth 3
```

includes hidden entries while limiting the depth of the tree.

## Version

To display the installed version:

```bash
rptree --version
```

or:

```bash
rptree -v
```

Example output:

```text
rptree v1.0.1
```

## Help

To display all available command-line options:

```bash
rptree --help
```

or:

```bash
rptree -h
```

This displays information about the available options and how to use them.

## Testing

The project uses `pytest` for automated testing.

To install pytest:

```bash
pip install pytest
```

Run the complete test suite with:

```bash
pytest
```

The current test suite contains **27 tests** covering functionality including:

* Tree generation
* Directory traversal
* Sorting
* Depth limits
* File filtering
* Directory filtering
* Hidden files
* Hidden directories
* Nested directories
* Command-line arguments
* Combined options

## Project Structure

```text
Repository-Tree-Graph/
├── src/
│   └── rptree/
│       ├── __init__.py
│       ├── cli.py
│       └── tree.py
│
├── tests/
│   └── test_tree.py
│
├── .gitignore
├── LICENSE
├── README.md
└── pyproject.toml
```

### `src/rptree/`

Contains the main `rptree` Python package.

### `cli.py`

Handles the command-line interface, including arguments such as:

```text
--depth
--files
--dirs
--hidden
```

### `tree.py`

Contains the logic responsible for recursively generating the directory tree.

### `tests/`

Contains the automated tests used to verify that `rptree` behaves correctly.

### `pyproject.toml`

Contains the project's package configuration, metadata, Python version requirements, and command-line entry point.

## Requirements

* Python 3.10 or newer
* pip

`rptree` currently has no external runtime dependencies.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
