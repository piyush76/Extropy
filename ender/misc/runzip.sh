#!/bin/sh
export PYTHONPATH=$0
exec env python2.5 -c "
import sys
sys.argv = sys.argv[1:]
import ender
ender.main()
" $0 $*
# THE END

