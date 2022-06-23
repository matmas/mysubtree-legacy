#!/bin/bash
python src/main_profiling.py $@
#gprof2dot -f pstats --skew=.1 mysubtree.profile | dot -Tpng -omysubtree.png
runsnake mysubtree.profile
