
#!/usr/bin/gnuplot
#
# Plot of a Klein bottle
#
# AUTHOR: Hagen Wierstorf

reset

# wxt
set terminal wxt size 350,262 enhanced font 'Verdana,10' persist
# png
#set terminal pngcairo size 350,262 enhanced font 'Verdana,10'
#set output 'klein_bottle1.png'
# svg
#set terminal svg size 350,262 fname 'Verdana, Helvetica, Arial, sans-serif' \
#fsize '10'
#set output 'klein_bottle1.svg'

# color definitions
set style line 1 lc rgb '#157545' lt 1 lw 1 # --- green

set tmargin at screen 0.99
set bmargin at screen 0.01
set lmargin at screen 0
set rmargin at screen 0.9
#set palette rgb 9,9,3
unset colorbox
unset key
unset border
unset tics
set ticslevel 0
set view 60,60
set isosamples 50
set xrange[-8:10]
set yrange[-8:8]
set hidden3d
set view equal xyz

#splot "mesh.csv" w pm3d
splot "mesh.csv" w lines
