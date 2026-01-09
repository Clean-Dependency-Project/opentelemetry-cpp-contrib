#!/bin/bash
set -eux

file="$1"

SDK="-L/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib \
-lopentelemetry_webserver_sdk \
-Wl,-rpath,/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib"

# Patch the exact module link command
sed -i "/ngx_http_opentelemetry_module.so/ s|\$| ${SDK}|" "$file"