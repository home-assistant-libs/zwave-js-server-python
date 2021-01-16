my_str = "appdirs-1.4.4 astroid-2.4.2 black-20.8b1 coverage-5.3.1 distlib-0.3.1 filelock-3.0.12 flake8-3.8.4 iniconfig-1.1.1 isort-5.7.0 lazy-object-proxy-1.4.3 mccabe-0.6.1 mypy-0.790 mypy-extensions-0.4.3 packaging-20.8 pathspec-0.8.1 pluggy-0.13.1 py-1.10.0 pycodestyle-2.6.0 pydocstyle-5.1.1 pyflakes-2.2.0 pylint-2.6.0 pyparsing-2.4.7 pytest-6.2.1 pytest-aiohttp-0.3.0 pytest-cov-2.10.1 pytest-timeout-1.4.2 regex-2020.11.13 snowballstemmer-2.0.0 toml-0.10.2 tox-3.21.0 typed-ast-1.4.2 virtualenv-20.3.1 wrapt-1.12.1 zwave-js-server-python"
pkgs = my_str.split(" ")

print(" ".join(["-".join(pkg.split("-")[:-1]) for pkg in pkgs]))
