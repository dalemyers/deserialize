#!/bin/bash

pushd "${VIRTUAL_ENV}/.." > /dev/null

source "${VIRTUAL_ENV}/bin/activate"

python -m black --line-length 100 deserialize tests

python -m pylint --rcfile=pylintrc deserialize tests

python -m mypy --ignore-missing-imports deserialize/ tests/

popd > /dev/null

