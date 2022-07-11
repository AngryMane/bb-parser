#!/usr/bin/env bash

YOCTO_VERS=(
kirkstone
honister
hardknott
gatesgarth
dunfell
)

for YOCTO_VER in ${YOCTO_VERS[@]}; do
  repo init -b ${YOCTO_VER} -u https://github.com/AngryMane/raspberrypi-yocto &> /dev/null 
  repo sync &> /dev/null 

  BB_FILES=(`find ./* -name *.bb`)
  for target in ${BB_FILES[@]}; do
    ./test_main.py ${target} > /dev/null
  done

  BBAPPEND_FILES=(`find ./* -name *.bbappend`)
  for target in ${BBAPPEND_FILES[@]}; do
    ./test_main.py ${target} > /dev/null
  done

  INC_FILES=(`find ./* -name *.inc`)
  for target in ${INC_FILES[@]}; do
    ./test_main.py ${target} > /dev/null
  done

  CONF_FILES=(`find ./* -name *.conf`)
  for target in ${CONF_FILES[@]}; do
    ./test_main.py ${target} > /dev/null
  done

  #rm -rf poky &> /dev/null
  #rm -rf .repo &> /dev/null
done
