#! /usr/bin/env bash
THISDIR=$(dirname $(realpath $0))
PYTHONDIR=$(dirname $THISDIR)
TESTDIR="$PYTHONDIR/tests"
export PYTHONPATH=$PYTHONDIR
pytest --import-mode importlib -vv --cov-report term --cov-report html:htmlcov --cov=$PYTHONDIR --ignore=$TESTDIR $TESTDIR