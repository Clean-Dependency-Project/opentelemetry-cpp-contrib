#!/bin/bash
set -e

file="$1"

SDK_FLAGS="-L/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib \
-lopentelemetry_webserver_sdk \
-Wl,-rpath,/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib"

echo "Patching link command in $file"

# Patch ONLY the link command (not the dependency list)
sed -i "/-shared .*ngx_http_opentelemetry_module.so/ s|\$| ${SDK_FLAGS}|" "$file"

# Safety check
if ! grep -q "lopentelemetry_webserver_sdk" "$file"; then
  echo "ERROR: SDK not linked into module"
  exit 1
fi
