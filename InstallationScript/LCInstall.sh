#!/bin/bash

USER_HOME=$(eval echo ~${SUDO_USER})

mkdir $USER_HOME/.lc

touch $USER_HOME/.lc/LegionController.ini

cd Module

make

cp LegionController.ko $USER_HOME/.lc

cd ..

cp LegionController /usr/bin

rm -r $PWD