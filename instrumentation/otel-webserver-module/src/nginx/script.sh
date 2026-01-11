#!/bin/bash
set -e

file="$1"

SDK_FLAGS="\
 -L/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib \
 -lopentelemetry_webserver_sdk \
 -Wl,-rpath,/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib"

echo "Patching module link command in $file"

sed -i "/\\$(LINK) -o objs\\/ngx_http_opentelemetry_module.so/ s|$|${SDK_FLAGS}|" "$file"

# hard verification
grep -n "lopentelemetry_webserver_sdk" "$file" || {
  echo "ERROR: SDK not linked into module"
  exit 1
}
