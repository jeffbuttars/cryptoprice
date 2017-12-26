Introduction
------------

A proof of concept project on building the basics for a fully asynchronous Python REST api with
`API Star <https://github.com/encode/apistar>`_.

This is an `asyncio <https://docs.python.org/3/library/asyncio.html>`_ based API Star project
created with the command:

.. sourcecode:: bash

    $ apistar new . --framework asyncio


Packaging / Pip
--------------------------

This project is built and managed with `Pipenv <https://docs.pipenv.org>`_.
Make sure you have `Pipenv <https://docs.pipenv.org>`_ installed on your system.

To create a virtualenv and install the project packages, from the proejct root directory:

For a production build environment:

.. sourcecode:: bash

    $ pipenv install


For a development build environment:

.. sourcecode:: bash

    $ pipenv install --dev


