modified six.py
===============

[https://github.com/pabigot/pyxb pyxb] has its own extension of the Python 2 to 3 (six) compatibility module.  As is typical
in this sort of situation, the main [https://pypi.python.org/pypi/six/ six] module has diverged and cherrypy depends on some
incompatible changes.  You need to replace pyxb/pyxb/utils/six.py with the six.py in this directory in order for six and cherrypy to co-exist.
