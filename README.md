# fastapi-login

[![Build status](https://ci.appveyor.com/api/projects/status/kb5w847l3wgtfqmw?svg=true)](https://ci.appveyor.com/project/parsd/fastapi-login)
[![Code coverage](https://codecov.io/gh/parsd/fastapi-login/branch/master/graph/badge.svg)](https://codecov.io/gh/parsd/fastapi-login)

My users route for logging in and out of a FastAPI app.

## Development

If not done, yet, [install Poetry](https://github.com/python-poetry/poetry#installation).

1. Create virtual environment:

    ```bash
    python3 -m venv venv
    ```

    or if on Windows and not using the Windows Store installer:

    ```cmd
    python -m venv venv
    ```

2. Activate the environment

    ```bash
    . venv/Scripts/activate
    ```

    or on Windows _cmd_:

    ```cmd
    venv\Scripts\acivate.bat
    ```

    or _PowerShell_:

    ```ps
    venv\Scripts\Acivate.ps1
    ```

3. Install development dependencies

    ```bash
    poetry install --no-root
    ```

## License

This project is licensed under the terms of the MIT license.
