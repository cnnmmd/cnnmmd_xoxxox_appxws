#!/bin/bash

usrapp="${1}"
envapp="${2}"
script="${3}"

export DISPLAY=":$(ls /tmp/.X11-unix | sed 's/^X//')"
export XAUTHORITY='/home/usrrdp/.Xauthority'

endprc() {
  kill -TERM "${prc}"
  wait "${prc}"
}

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -X ${usrapp}@${envapp} "${script}" &
prc=$!
trap endprc TERM
wait "${prc}"
