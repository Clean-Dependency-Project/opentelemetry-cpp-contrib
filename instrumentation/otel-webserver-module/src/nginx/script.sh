#!/bin/bash
set -eux

file="$1"

echo "=== PATCHING FILE ==="
echo "$file"
echo "=== FIRST 40 LINES ==="
head -n 40 "$file"
echo "=== SEARCH RESULT ==="
grep -n "opentelemetry" "$file" || true
