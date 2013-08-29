#!/bin/bash
. lib.sh
[[ $(get_distro) == "arch" ]] || ( echo "Unexpected distro"; exit 1 )
require vagrant "packer -S vagrant" 
require fab "sudo pacman -S python2-fabric"
require /usr/lib/python2.7/site-packages/jinja2/__init__.py "sudo pacman -S python2-jinja"
require /usr/lib/python2.7/site-packages/cuisine.py "packer -S python2-cuisine-git"

echo "Run:"
echo "  vagrant up && fab staging deploy"
echo "  fab staging test"
