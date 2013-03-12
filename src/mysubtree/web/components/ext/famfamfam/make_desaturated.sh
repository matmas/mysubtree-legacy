#!/bin/bash

indir=icons
outdir=desaturated/icons
mkdir -p $outdir

cd $indir
files=`ls *.png`
cd -
for filename in $files; do
    src=$indir/$filename
    out=$outdir/$filename
    convert $src -colorspace Gray $out
#     convert $out -gamma 1 $out
done