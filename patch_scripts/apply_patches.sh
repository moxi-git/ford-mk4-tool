#!/bin/bash

PATCH_FILE="patches/0001-fix-diagnostics.patch"
TARGET_FILE="main.py"

if [ ! -f "$PATCH_FILE" ]; then
  echo "Error: Patch file '$PATCH_FILE' not found."
  exit 1
fi

echo "Applying patch $PATCH_FILE to $TARGET_FILE..."

patch -p1 <"$PATCH_FILE"

if [ $? -eq 0 ]; then
  echo "Patch applied successfully."
else
  echo "Failed to apply patch."
  exit 1
fi
