#!/bin/bash
TOOLS=`dirname $0`
VENV=$TOOLS/../.crawler-venv
source $VENV/bin/activate && $@
