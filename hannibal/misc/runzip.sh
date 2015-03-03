#!/bin/sh
export PYTHONPATH=$0
exec env python2.5 -c "
import sys
sys.argv = sys.argv[1:]
import hannibal
hannibal.main()
" $0 $*
# THE END

