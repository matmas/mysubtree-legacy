#!/bin/bash
if [ -f /etc/arch-release ]; then 
        distro="arch" 
elif [ -f /etc/lsb-release ]; then 
        distro="ubuntu" 
else 
        echo "Unexpected distro"; exit 1 
fi

if [ "$distro" == "arch" ]; then
    if [ -z "`pidof mysqld`" ]; then
        sudo /etc/rc.d/mysqld start
    fi
fi

clear
~/.venv/bin/python src/main_profiling.py $@
#gprof2dot -f pstats --skew=.1 mysubtree.profile | dot -Tpng -omysubtree.png
runsnake mysubtree.profile
