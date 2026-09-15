## What It Does
  when given a directory on your device, it will create a tree diagram of all the sub-directories and files within that directory

## How To Use It 
  - Go to the terminal
  - Go to the rptree_dir directory
  - type:
  ```text
  "python3 tree.py " folowed by the directory you want a tree of
  ```
      -> on Mac you can do //Users/yourname/TheRestOfTheDirectory
      -> on Windows you can do CD:\TheRestOfTheDirectory

## What You Should See
  I used Mac and this was my output when I used it on itself
  
  ```text
/Users/myusername/Projects/rptree_project/
│
├── rptree_dir/
│   ├── __pycache__/
│   │   ├── cli.cpython-314.pyc
│   │   ├── __init__.cpython-314.pyc
│   │   └── rptree.cpython-314.pyc
│   │
│   ├── __init__.py
│   ├── rptree.py
│   └── cli.py
│
├── tree.py
├── .DS_Store
└── README.md
```   
    
## Other Commands
```text
  python3 tree.py -v
  python3 tree.py --version
```
 -> this gives you the version
    
```text
  python tree.py -h
  python tree.py --help
```
-> gives a list of all commands
