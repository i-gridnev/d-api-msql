#!/bin/sh
if [ -f .env ]
then
  export $(grep -v '^#' .env | xargs -d '\n')
fi