#! /usr/bin/env bash
THISDIR=$(dirname $(realpath $0))
BASEDIR=$(dirname $THISDIR)
PYTHONDIR="$BASEDIR/function"
TESTDIR="$BASEDIR/tests"
export PYTHONPATH=$PYTHONDIR
pytest --import-mode importlib -vv --cov-report term --cov-report html:htmlcov --cov=$PYTHONDIR --ignore=$TESTDIR $TESTDIR
