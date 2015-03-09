PluggableCura
=============

Cura pluggable unicorn edition. Basicly PinkUnicorn but with plugins (Making it PluggableUnicorn™©)


Dependencies
------------
- python3
- python3-pyqt5
- python3-numpy

Installing Qt
-------------
- sudo apt-get install python3-pyqt5
- sudo apt-get install python3-pyqt5.qtquick
- sudo apt-get install python3-pyqt5.qtopengl
- sudo apt-get install qtdeclarative5-window-plugin
- sudo apt-get install qtdeclarative5-dialogs-plugin
- sudo apt-get install qtdeclarative5-qtquick2-plugin qtdeclarative5-controls-plugin qtdeclarative5-quicklayouts-plugin

Installing PluggableCura dependencies on Windows
-------------
- Install and build SIP according to the instructions on http://pyqt.sourceforge.net/Docs/sip4/installation.html
- Install the PyQt5 package from http://www.riverbankcomputing.com/software/pyqt/download5

Run
---
1. navigate to PluggableCura
2. execute
PYTHONPATH=../libArcus/python:. python3 printer/printer.py # that is, we include libArcus and the current directy in the searchpath
