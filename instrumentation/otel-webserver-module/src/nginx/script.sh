#!/bin/bash
set -e

file="$1"

SDK_LIBS="-L/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib \
-lopentelemetry_webserver_sdk \
-Wl,-rpath,/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib"

echo "Patching ngx_module_libs in $file"

# Append SDK libs to ngx_module_libs (the only safe hook)
if grep -q "^ngx_module_libs *=" "$file"; then
  sed -i "/^ngx_module_libs *=/ s|\$| ${SDK_LIBS}|" "$file"
else
  echo "ERROR: ngx_module_libs not found in Makefile"
  exit 1
fi

# Verify
grep -n "lopentelemetry_webserver_sdk" "$file" || {
  echo "ERROR: SDK libs not injected"
  exit 1
}
