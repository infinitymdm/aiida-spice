===============
Developer guide
===============

Running the tests
+++++++++++++++++

The following will discover and run all unit test::

    pip install --upgrade pip
    pip install -e .[tests]
    pytest -v

It is recommended to run tests every time you make a change. If you add
new features, you should write tests to validate those features.

Automatic coding style checks
+++++++++++++++++++++++++++++

Enable enable automatic checks of code sanity and coding style::

    pip install -e .[pre-commit]
    pre-commit install

After this, the `black <https://black.readthedocs.io>`_ formatter,
the `pylint <https://www.pylint.org/>`_ linter
and the `pylint <https://www.pylint.org/>`_ code analyzer will
run at every commit.

If you ever need to skip these pre-commit hooks, just use::

    git commit -n

You should also keep the pre-commit hooks up to date periodically, with::

    pre-commit autoupdate

Or consider using `pre-commit.ci <https://pre-commit.ci/>`_.

Continuous integration
++++++++++++++++++++++

``aiida-spice`` comes with a ``.github`` folder that contains continuous integration tests on every commit using `GitHub Actions <https://github.com/features/actions>`_. It will:

#. run all tests
#. build the documentation
#. check coding style and version number (not required to pass by default)

Building the documentation
++++++++++++++++++++++++++

 #. Install the ``docs`` extra::

        pip install -e .[docs]

 #. Edit the individual documentation pages::

        docs/source/index.rst
        docs/source/developer_guide/index.rst
        docs/source/user_guide/index.rst
        docs/source/user_guide/get_started.rst

 #. Use `Sphinx`_ to generate the html documentation::

        cd docs
        make

Check the result by opening ``build/html/index.html`` in your browser.

Documentation is automatically published alongside your code changes.
Make sure to update the relevant documents in docs/source.

.. _Sphinx: https://www.sphinx-doc.org/en/master/
