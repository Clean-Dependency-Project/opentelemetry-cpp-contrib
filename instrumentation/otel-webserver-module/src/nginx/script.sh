#!/bin/bash
set -e

file="$1"

SDK_LINES="\\
\t-L/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib \\
\t-lopentelemetry_webserver_sdk \\
\t-Wl,-rpath,/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib"

echo "Patching module link rule in $file"

# Insert SDK flags as new continuation lines AFTER the object list
sed -i "/cc -o objs\\/ngx_http_opentelemetry_module.so/ a ${SDK_LINES}" "$file"

# Verify
grep -n "lopentelemetry_webserver_sdk" "$file" || {
  echo "ERROR: SDK flags not injected"
  exit 1
}
