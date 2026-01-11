#!/bin/bash
set -e

file="$1"

SDK_LINES="\\
\t-L/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib \\
\t-lopentelemetry_webserver_sdk \\
\t-Wl,-rpath,/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib"

echo "Patching nginx module link rule in $file"

# Patch the actual link command (expanded form)
if grep -q "cc -o objs/ngx_http_opentelemetry_module.so" "$file"; then
  sed -i "/cc -o objs\\/ngx_http_opentelemetry_module.so/ a ${SDK_LINES}" "$file"
else
  echo "WARN: module link rule not found yet, skipping patch"
fi

# Non-fatal verification
grep -n "lopentelemetry_webserver_sdk" "$file" || \
  echo "WARN: SDK flags not visible in Makefile yet"
