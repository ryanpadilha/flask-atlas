#!/bin/bash
#
# This script stop python application using Gunicorn

echo "stop python application"

PID=$(cat /var/wplex/run/gunicorn-atlas.pid)
kill -9 $PID
