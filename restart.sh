#!/usr/bin/env bash

rm log/* 
git checkout master
git branch -D tmp
python utils/main.py
