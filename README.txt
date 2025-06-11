
- VGEditor -

an editor for vector-graphics written in python using pyside6.
this project is an assignment for the EiS course at JGU-Mainz in SoSe 2025 by group 3A.

to run this program: 'python main.py'
to clone the repo: 'git clone https://github.com/derjulian2/VGEditor'

requirements:
- pyside6 needs to be installed (system-wide or in a venv)

virtual environment setup (requires python3-venv and python3-pip packages):
'python3 -m venv ./venv'
'source venv/bin/activate'
'pip3 install pyside6'

- Notes - 

- trying to revamp rendering / shape calculation
-> QT-native rendering should still be used for like circles/stars, but for deformations, single-polygon rendering has to be used (is very slow to update very often)
-> maybe QPainterPath is so resource-intensive? (probably all of the computations though, maybe not make these transformations real-time-editable)
- refactor dialogues for adding/editing
-> maybe support right-click for more editing-options
- .svg import/export missing