#!/bin/bash

indir=icons
outdir=20x20/icons
mkdir -p $outdir

cd $indir
files=`ls *.png`
cd -
for filename in $files; do
    src=$indir/$filename
    out=$outdir/$filename
    convert $src -background 'rgba(0, 0, 0, 0.0)' -gravity center -extent 20x20 $out
done