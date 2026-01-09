#!/bin/bash
set -euo pipefail

file="$1"

SDK_FLAGS="-L/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib \
-lopentelemetry_webserver_sdk \
-Wl,-rpath,/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib"

# Patch the exact shared-module link line
sed -i "/ngx_http_opentelemetry_module.so/ s|\$| ${SDK_FLAGS}|" "$file"