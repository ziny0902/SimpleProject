#!/usr/bin/bash
cat $1 | ./matrix.sh -csv |  ./inverse
