
fastapi-login
=============


.. image:: https://ci.appveyor.com/api/projects/status/kb5w847l3wgtfqmw?svg=true
   :target: https://ci.appveyor.com/project/parsd/fastapi-login
   :alt: Build status


.. image:: https://codecov.io/gh/parsd/fastapi-login/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/parsd/fastapi-login
   :alt: Code coverage


My users route for logging in and out of a FastAPI app.

Development
-----------

If not done, yet, `install Poetry <https://github.com/python-poetry/poetry#installation>`_.


#. 
   Create virtual environment:

   .. code-block:: bash

       python3 -m venv venv

    or if on Windows and not using the Windows Store installer:

   .. code-block:: cmd

       python -m venv venv

#. 
   Activate the environment

   .. code-block:: bash

       . venv/Scripts/activate

    or on Windows *cmd*\ :

   .. code-block:: cmd

       venv\Scripts\acivate.bat

    or *PowerShell*\ :

   .. code-block:: ps

       venv\Scripts\Acivate.ps1

#. 
   Install development dependencies

   .. code-block:: bash

       poetry install --no-root

License
-------

This project is licensed under the terms of the MIT license.
