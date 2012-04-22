entrypoint2 is an easy to use command-line interface for python modules, fork of `entrypoint <http://pypi.python.org/pypi/entrypoint/>`_ 


Links:
 * home: https://github.com/ponty/entrypoint2
 * documentation: http://ponty.github.com/entrypoint2


Background
============

There are tons of command-line handling modules 
but none of them can generate a CLI interface 
for a very simple function like this 
without duplicating the existing code and 
without making the function from other modules unusable::
	
	def add(one, two=4, three=False): 
		''' description
		one: description
		two: description
		three: description
		'''
		
Best solution I could find is entrypoint_,
but there is no link to development site,
so I forked the project.
The only big disadvantage of entrypoint_:
it destroys the function signature, therefore 
the function can not be called from other modules. 

Goals
================
 - the decorated function should have the same behavior as without the entrypoint2 decorator
 - generate CLI parameters from function signature 
 - generate CLI documentation from python documentation 
 - boolean parameters should be toggle flags
 - generate short flags from long flags: ``--long -> -l``
 - automatic --version flag

Similar projects
================

 * `entrypoint <http://pypi.python.org/pypi/entrypoint/>`_
 * `plac  <http://micheles.googlecode.com/hg/plac/doc/plac.html>`_
 * `baker <http://bitbucket.org/mchaput/baker>`_   
 * `argh <http://packages.python.org/argh/>`_
 * `opster <http://pypi.python.org/pypi/opster/>`_
 * `commandline <http://pypi.python.org/pypi/commandline>`_
 * `optfunc <https://github.com/simonw/optfunc>`_: it has the same concept
 * `commando (1) <http://freshmeat.net/projects/commando>`_
 * `commando (2) <https://github.com/lakshmivyas/commando>`_
 
Features
============

Additional features over original entrypoint_:
 - function signature is preserved so it can be called both from command-line and external module
 - function name, doc and module are preserved so it can be used with sphinx autodoc_
 - sphinx autodoc_ documentation style is supported: ``:param x: this is x``
 - automatic ``--version`` flag, which prints version variable from the current module
   (``__version__``, ``VERSION``, ..) 
 - automatic ``--debug`` flag, which turns on logging 
 - short flags are generated automatically (e.g. ``--parameter`` -> ``-p``) 
 - unit tests
 - supported python versions: 2.5, 2.6, 2.7, 3.1, 3.2, PyPy
 
Known problems:
 - there are more decorators in the module inherited from original entrypoint_,
   but only @entrypoint  is tested. 

Basic usage
============

Example::

	from entrypoint2 import entrypoint
	
	__version__ = '3.2'
	
	@entrypoint
	def add(one, two=4, three=False): 
	    ''' This function adds three numbers.
	    
	    one: first number to add
	    two: second number to add
	    '''

Generated help::

	$ python -m entrypoint2.examples.hello --help
	usage: hello.py [-h] [-t TWO] [--three] [--version] [--debug] one
	
	This function adds two number.
	
	positional arguments:
	  one                first number to add
	
	optional arguments:
	  -h, --help         show this help message and exit
	  -t TWO, --two TWO  second number to add
	  --three
	  --version          show program's version number and exit
	  --debug            set logging level to DEBUG

Printing version::

	$ python -m entrypoint2.examples.hello --version
	3.2


Installation
============

General
--------

 * install pip_
 * install the program::

    # as root
    pip install entrypoint2

Ubuntu
----------
::

    sudo apt-get install python-pip
    sudo pip install entrypoint2

Uninstall
----------
::

    # as root
    pip uninstall entrypoint2


.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _pip: http://pip.openplans.org/
.. _entrypoint: http://pypi.python.org/pypi/entrypoint/
.. _autodoc: http://sphinx.pocoo.org/ext/autodoc.html