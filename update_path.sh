#!/bin/bash

BASE_DIR="$HOME/.scripts"

for dir in "$BASE_DIR"/*/.; do
  if [ -d "$dir" ]; then
    export PATH="$dir:$PATH"
  fi
done

echo "New Path: $PATH"

