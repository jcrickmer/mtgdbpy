#!/bin/sh

find ./ -name '*.py' -print -exec autopep8 --in-place --aggressive --aggressive --max-line-length 140 {} \;
