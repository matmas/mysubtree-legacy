#!/bin/bash

if [[ ! -d icons/ ]]; then
    URL="http://www.famfamfam.com/lab/icons/silk/famfamfam_silk_icons_v013.zip"
    wget -qO- -O tmp.zip $URL && unzip tmp.zip && rm tmp.zip
fi

mkdir -p companion

if [[ ! -d companion/icons/ ]]; then
    cd companion
    URL="http://download.damieng.com/iconography/SilkCompanion1.zip"
    wget -qO- -O tmp.zip $URL && unzip tmp.zip && rm tmp.zip
    cd ..
fi


if [[ ! -d 20x20/ ]]; then
    ./make_20x20.sh
fi

if [[ ! -d 20x20/desaturated ]]; then
    ./make_20x20_desaturated.sh
fi

if [[ ! -d desaturated ]]; then
    ./make_desaturated.sh
fi

if [[ ! -d companion/20x20/desaturated ]]; then
    cd companion
    ../make_20x20_desaturated.sh
    cd ..
fi
