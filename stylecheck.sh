#!/bin/bash

pushd "${VIRTUAL_ENV}" > /dev/null

python -m black deserialize
python -m black tests

python -m pylint --rcfile=pylintrc deserialize
python -m mypy --ignore-missing-imports deserialize/

python -m pylint --rcfile=pylintrc tests
python -m mypy --ignore-missing-imports tests/

popd > /dev/null

