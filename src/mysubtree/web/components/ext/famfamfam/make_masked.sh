#!/bin/bash

indir=icons
outdir=masked/icons
mkdir -p $outdir

cd $indir
files=`ls *.png`
cd -
for filename in $files; do
    src=$indir/$filename
    out=$outdir/$filename

    convert -colorspace Gray $src $out
#     convert -colorspace HSB  -channel B -separate $src $out

    convert $out -gamma 0.4 $out # better contrast

    convert $out -background white -flatten $out # replace transparency with white background

    convert $out -background white -alpha shape $out
#     convert $out -alpha copy $out
#     convert $out   +level-colors red,   $out
#     convert  $out  -fill red  -tint 40 $out
    # convert $out -background green -flatten $out
done