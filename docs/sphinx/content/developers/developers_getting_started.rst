.. getting_started - developer introduction page
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 23/3/20

.. _developers_getting_started:

Getting Started
===============

Installation
------------

First clone the project repository from GitHub::

   $ git clone https://github.com/HYPERNETS/hypernets_processor.git

In your development python environment install the module in develop mode::

   $ pip install -e hypernets_processor/

This will allow you to edit and call the code where it is, avoiding having to re-install every time you make changes. Dependencies should automatically be installed by pip.

Contributing to Development
---------------------------

The software is defined by the following:

* The processing algorithm is defined in the :ref:`atbd` section.
* The software design is defined in the :ref:`software_design` section.

Tasks and issues are then organised in the GitHub `project board <https://github.com/HYPERNETS/hypernets_processor/projects/1>`_. Discuss how you can contribute to this with either Sam or Clémence :)

The following has some information and tips to help you make your contributions.

Version Control, Git and GitHub
+++++++++++++++++++++++++++++++

The code is hosted on `GitHub <https://github.com/HYPERNETS/hypernets_processor>`_. When you're working on a feature, work on it in a new branch:

.. parsed-literal::

   git branch new-branch
   git checkout new-branch

Then merge this into the master branch when you're done.

Documentation
+++++++++++++

The `docs/` directory contains the project's documentation. This includes the deliverable documents (ATBD, File Format Specifications) and, in the `sphinx/` directory, this documentation too. This is written in **reStructuredText** which is almost like writing in plain English, and built using Sphinx. The Sphinx Documentation has an `introduction to reST <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#inline-markup>`_. Sphinx also automatically generates the API documentation by parsing the contents of all the package's docstrings. To write parsable docstrings, see `this guide <https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html>`_.

You can build the documentation from the `docs/sphinx` directory with:

.. parsed-literal::

   make html

This documentation is hosted on `ReadTheDocs <https://readthedocs.org>`_. When there is a push the GitHub repository ReadTheDocs automatically rebuilds its copy of the documentation.

Unit testing
++++++++++++

Every package and subpackage should contain a subpackage called `tests/` for the relevant unit tests.

The GitHub repository is set up so that `Travis CI <https://travis-ci.com/>`_ automatically runs the projects tests when new code is pushed to it. Similarly `codecov <https://codecov.io/>`_ is set up to report the test coverage.

