#! /usr/bin/env bash
# Install test requirements
echo -e "Installing test dependencies"
pip install -r tests/requirements-test.txt --quiet
echo -e "Done"
echo -e "Run tests"

PYTHONDIR="function"
export PYTHONPATH=$PYTHONDIR

pytest tests/                   \
--cov-config .coveragerc        \
--cov=function                  \
--cov-report html               \
--cov-report term               \
--cov-report xml                \
--no-cov-on-fail                \
--cov-fail-under=100            \
$@

passed=$?

if [ $passed -eq 0 ]
then
    echo -e "\nTo view the HTML coverage report: open htmlcov/index.html\n"
fi

exit $passed
