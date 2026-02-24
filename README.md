# tests

### Setup project

- Update the list of available packages on your system
    ```
    sudo apt update
    ```

- Create & activate virtual environment
    - Create & activate virtual environment in *nix systems
        ```
        python3 -m venv venv && source venv/bin/activate
        ```
    - Create & activate virtual environment in windows systems
        - CMD
            ```
            python -m venv venv && source venv\Scripts\activate
            ```
        - PWS
            ```
            python -m venv venv && source venv\Scripts\activate.ps1
            ```
            *If PowerShell complains about the execution policy, run it as administrator and allow scripts: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser*


- Upgrade pip & install dependecy
    - Upgrade pip & install dependecy in *nix systems
        ```
        python3 -m pip install -U pip && python3 -m pip install -r requirements.txt
        ```
    - Upgrade pip & install dependecy in windows
        - CMD
            ```
            python -m pip install -U pip && python -m pip install -r requirements.txt
            ```
        - PWS
            ```
            python -m pip install -U pip; python -m pip install -r requirements.txt
            ```


### Pre-commit
- Install Git hook
    ```
    pre-commit install
    ```
- Run check all files
    ```
    pre-commit run --all-files
    ```
- If u need can update version hook
    ```
    pre-commit autoupdate
    ```

### Currently in use .env is abolished, use tests/fcle/settings.py
#### ~~You need to create a .env file similar to example.env (do not delete example.env) management of constants in the project comes from .env as from a config file, also hide endpoints/keys/mail and other sensitive data.~~


### Script for *nix system for optimization and no need to copy-paste commands above
```
$ ./setup_env.sh
```

###  Script for *nix system for delete *.pyc and __pycache__ files.
```
$ ./remove_pycache.sh
```
