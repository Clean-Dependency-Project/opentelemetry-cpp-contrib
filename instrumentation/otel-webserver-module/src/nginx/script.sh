#!/bin/bash
set -e

fileName="$1"

SDK_LIB="-L/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib"
SDK_LINK="-lopentelemetry_webserver_sdk"
SDK_RPATH="-Wl,-rpath,/otel-webserver-module/build/linux-x64/opentelemetry-webserver-sdk/sdk_lib/lib"

# 1️⃣ Append SDK flags to ngx_module_link (preferred)
sed -i "/^ngx_module_link *=/ s|\$| ${SDK_LIB} ${SDK_LINK} ${SDK_RPATH}|" "$fileName"

# 2️⃣ Fallback: append to LINK if ngx_module_link does not exist
sed -i "/^LINK *=/ s|\$| ${SDK_LIB} ${SDK_LINK} ${SDK_RPATH}|" "$fileName"