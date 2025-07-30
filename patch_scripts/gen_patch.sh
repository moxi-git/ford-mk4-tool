#!/bin/bash
# Regenerate patch file from modified source
diff -u main.py main_patched.py >patches/0001-fix-diagnostics.patch
