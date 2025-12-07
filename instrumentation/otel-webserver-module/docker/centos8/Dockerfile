
# syntax=docker/dockerfile:1.4

# ===============================
# Stage 1: BUILD on Debian 12
# ===============================
FROM debian:12-slim AS builder
ARG BUILD_NUMBER
LABEL NAME="apm/build-image-nginx-otel-debian12-x64" VERSION=${BUILD_NUMBER}

# ---- Versions ----
ARG NGINX_VERSION="1.29.3"
ARG OPENTELEMETRY_VERSION="1.23.0"
ARG BOOST_VERSION="1.75.0"
ARG LOG4CXX_VERSION="0.11.0"
ARG APR_VERSION="1.7.0"
ARG EXPAT_VERSION="2.3.0"
ARG EXPAT_RVERSION="R_2_3_0"
ARG LIBTOOL_VERSION="2.4.6"
ARG APRUTIL_VERSION="1.6.1"
ARG BOOST_FILENAME="boost_1_75_0"
ARG PYTHON_VERSION="2.7.8"   # remove if not needed

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# ---- Toolchain & build deps ----
RUN set -eux; \
  apt-get update; \
  apt-get install -y --no-install-recommends \
    build-essential git make wget curl ca-certificates xz-utils tar unzip which \
    cmake pkg-config ninja-build \
    zlib1g-dev libssl-dev libpcre3-dev \
    openjdk-17-jdk \
    perl m4 autoconf automake libtool \
    libabsl-dev libre2-dev \
    libc-ares-dev \
    libgrpc-dev libgrpc++-dev libgrpc++1 \
    libprotobuf-dev protobuf-compiler \
    protobuf-compiler-grpc \
    file gnupg patchelf; \
  rm -rf /var/lib/apt/lists/*

# ---- (Optional) Build Python 2.7 ----
RUN set -eux; \
  wget http://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz; \
  unxz Python-${PYTHON_VERSION}.tar.xz; \
  tar -xf Python-${PYTHON_VERSION}.tar; \
  cd Python-${PYTHON_VERSION}; \
  ./configure --prefix=/usr/local; \
  make -j"$(nproc)"; \
  make install; \
  cd ..; \
  rm -rf Python-${PYTHON_VERSION}.tar Python-${PYTHON_VERSION}

# ---- Directory prep ----
RUN mkdir -p /dependencies

# ---- Build Boost (filesystem, system) static with PIC ----
RUN set -eux; \
  wget https://archives.boost.io/release/${BOOST_VERSION}/source/${BOOST_FILENAME}.tar.gz; \
  tar -xvf ${BOOST_FILENAME}.tar.gz; \
  cd ${BOOST_FILENAME}; \
  ./bootstrap.sh --with-libraries=filesystem,system --prefix=/dependencies/boost/${BOOST_VERSION}; \
  ./b2 install define=BOOST_ERROR_CODE_HEADER_ONLY link=static threading=multi \
    cxxflags="-fvisibility=hidden -fPIC" cflags="-fvisibility=hidden -fPIC"; \
  cd ..; \
  rm -rf ${BOOST_FILENAME}*

# ---- Build APR (static) ----
RUN set -eux; \
  mkdir -p /dependencies/apr/${APR_VERSION}; \
  wget https://archive.apache.org/dist/apr/apr-${APR_VERSION}.tar.gz --no-check-certificate; \
  tar -xf apr-${APR_VERSION}.tar.gz; \
  cd apr-${APR_VERSION}; \
  ./configure --prefix=/dependencies/apr/${APR_VERSION} --enable-static=yes --enable-shared=no --with-pic; \
  make -j"$(nproc)"; make install; \
  cd ..; rm -rf apr-${APR_VERSION}*

# ---- Build Expat (static) ----
RUN set -eux; \
  mkdir -p /dependencies/expat/${EXPAT_VERSION}; \
  wget https://github.com/libexpat/libexpat/releases/download/${EXPAT_RVERSION}/expat-${EXPAT_VERSION}.tar.gz --no-check-certificate; \
  tar -xf expat-${EXPAT_VERSION}.tar.gz; \
  cd expat-${EXPAT_VERSION}; \
  ./configure --prefix=/dependencies/expat/${EXPAT_VERSION} --enable-static=yes --enable-shared=no --with-pic; \
  make -j"$(nproc)"; make install; \
  cd ..; rm -rf expat-${EXPAT_VERSION}*

# ---- Build APR-util (static) ----
RUN set -eux; \
  mkdir -p /dependencies/apr-util/${APRUTIL_VERSION}; \
  wget https://archive.apache.org/dist/apr/apr-util-${APRUTIL_VERSION}.tar.gz --no-check-certificate; \
  tar -xf apr-util-${APRUTIL_VERSION}.tar.gz; \
  cd apr-util-${APRUTIL_VERSION}; \
  ./configure --prefix=/dependencies/apr-util/${APRUTIL_VERSION} \
    --enable-static=yes --enable-shared=no --with-pic \
    --with-apr=/dependencies/apr/${APR_VERSION} \
    --with-expat=/dependencies/expat/${EXPAT_VERSION}; \
  make -j"$(nproc)"; make install; \
  cd ..; rm -rf apr-util-${APRUTIL_VERSION}*

# ---- Build libtool (host) ----
RUN set -eux; \
  wget --no-check-certificate https://ftpmirror.gnu.org/libtool/libtool-${LIBTOOL_VERSION}.tar.gz; \
  tar xzf libtool-${LIBTOOL_VERSION}.tar.gz; \
  cd libtool-${LIBTOOL_VERSION}; \
  ./configure --prefix=/usr; \
  make -j"$(nproc)"; make install; \
  libtool --version; \
  cd ..; rm -rf libtool-${LIBTOOL_VERSION}.tar.gz libtool-${LIBTOOL_VERSION}

# ---- Build log4cxx (static) ----
RUN set -eux; \
  mkdir -p /dependencies/apache-log4cxx/${LOG4CXX_VERSION}; \
  wget https://archive.apache.org/dist/logging/log4cxx/${LOG4CXX_VERSION}/apache-log4cxx-${LOG4CXX_VERSION}.tar.gz --no-check-certificate; \
  tar -xf apache-log4cxx-${LOG4CXX_VERSION}.tar.gz; \
  cd apache-log4cxx-${LOG4CXX_VERSION}; \
  autoreconf -fi; \
  ./configure --prefix=/dependencies/apache-log4cxx/${LOG4CXX_VERSION}/ \
    --enable-static=yes --enable-shared=no --with-pic \
    --with-apr=/dependencies/apr/${APR_VERSION}/ \
    --with-apr-util=/dependencies/apr-util/${APRUTIL_VERSION}/; \
  make -j"$(nproc)"; make install; \
  cd ..; rm -rf apache-log4cxx-${LOG4CXX_VERSION}* apache-log4cxx-${LOG4CXX_VERSION}.tar.gz

# ---- Build OpenTelemetry C++ SDK (shared libs) ----
RUN set -eux; \
  mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib; \
  mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include; \
  git clone https://github.com/open-telemetry/opentelemetry-cpp; \
  cd opentelemetry-cpp; \
  git checkout "tags/v${OPENTELEMETRY_VERSION}" -b "v${OPENTELEMETRY_VERSION}"; \
  git submodule update --init --recursive; \
  mkdir build; cd build; \
  cmake .. \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    -DBUILD_TESTING=OFF \
    -DBUILD_SHARED_LIBS=ON \
    -DWITH_OTLP=ON \
    -DWITH_OTLP_GRPC=ON \
    -DWITH_OTLP_HTTP=ON \
    -DWITH_ABSEIL=ON \
    -DCMAKE_CXX_STANDARD=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED=ON \
    -DCMAKE_PREFIX_PATH="/usr" \
    -DProtobuf_DIR="/usr/lib/x86_64-linux-gnu/cmake/protobuf" \
    -DProtobuf_INCLUDE_DIR="/usr/include" \
    -DgRPC_DIR="/usr/lib/x86_64-linux-gnu/cmake/grpc" \
    -Dabsl_DIR="/usr/lib/x86_64-linux-gnu/cmake/absl"; \
  cmake --build . --target all -j"$(nproc)"; \
  cmake --install .; \
  find . -type f -name "*.so" -exec cp -v {} /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/ \; ; \
  PROTO_ROOT_DIR="$( \
    find . -type f -path '*/opentelemetry/proto/*/*.pb.h' -printf '%h\n' \
      | sed -E 's#^(.*opentelemetry/proto).*#\1#' | head -n 1 \
  )"; \
  if [ -n "${PROTO_ROOT_DIR}" ] && [ -d "${PROTO_ROOT_DIR}" ]; then \
    echo "Discovered proto root: ${PROTO_ROOT_DIR}"; \
    mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry/; \
    cp -r "${PROTO_ROOT_DIR}" /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry/; \
  else \
    echo "ERROR: Could not locate generated opentelemetry/proto/*.pb.h in build tree." >&2; \
    find . -type f -name '*.pb.h' | sed 's/^/  /'; \
    exit 1; \
  fi; \
  test -f /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry/proto/trace/v1/trace.pb.h; \
  cd ../..; rm -rf opentelemetry-cpp

# ---- Download NGINX source (headers for module build) ----
RUN set -eux; \
  mkdir /build-dependencies; \
  wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz; \
  tar -xvf nginx-${NGINX_VERSION}.tar.gz -C /build-dependencies; \
  rm -f nginx-${NGINX_VERSION}.tar.gz

# ---- Copy module sources and run Gradle build ----
COPY . /otel-webserver-module
RUN set -eux; \
  cp -r /dependencies /otel-webserver-module/; \
  cp -r /build-dependencies /otel-webserver-module/; \
  cd /otel-webserver-module; \
  chmod +x ./gradlew; \
  ./gradlew assembleWebServerModule

# ---- Unpack SDK, augment libs (exclude core + OpenSSL), set RPATH, re-pack ----
RUN set -eux; \
  cd /otel-webserver-module/build; \
  tar -xf opentelemetry-webserver-sdk-x64-linux.tgz; \
  SDK_ROOT="/opt/opentelemetry-webserver-sdk"; \
  rm -rf "${SDK_ROOT}"; \
  mv -f opentelemetry-webserver-sdk "${SDK_ROOT}"; \
  mkdir -p "${SDK_ROOT}/sdk_lib/lib" "${SDK_ROOT}/third_party/lib"; \
  SDK_LIB_DIR="${SDK_ROOT}/sdk_lib/lib"; \
  TP_LIB_DIR="${SDK_ROOT}/third_party/lib"; \
  \
  # 1) Copy OTel libs into sdk_lib/lib
  cp -v /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/libopentelemetry_*.so "${SDK_LIB_DIR}/" || true; \
  cp -v /usr/local/lib/libopentelemetry_*.so "${SDK_LIB_DIR}/" || true; \
  \
  # 2) Copy ONLY non-core, non-OpenSSL transitive deps into third_party/lib
  mkdir -p "${TP_LIB_DIR}"; \
  for LIB in \
    "${SDK_LIB_DIR}/libopentelemetry_exporter_otlp_grpc_client.so" \
    "${SDK_LIB_DIR}/libopentelemetry_exporter_otlp_grpc.so" \
    "${SDK_LIB_DIR}/libopentelemetry_proto.so" \
    "${SDK_LIB_DIR}/libopentelemetry_logs.so" \
    "${SDK_LIB_DIR}/libopentelemetry_metrics.so" \
  ; do \
    if [ -f "${LIB}" ]; then \
      echo "Resolving transitive deps for: ${LIB}"; \
      ldd "${LIB}" \
        | awk '/=>/ && $3 ~ /^\// {print $3} !/=>/ {for(i=1;i<=NF;i++) if($i ~ /^\//) print $i}' \
        | sort -u \
        | grep -Ev '/ld-linux-x86-64\.so\.2$|/libc\.so\.6$|/libm\.so\.6$|/libpthread\.so\.[0-9]+$|/libdl\.so\.[0-9]+$|/librt\.so\.[0-9]+$|/libresolv\.so\.[0-9]+$|/libnsl\.so\.[0-9]+$|/libgcc_s\.so\.[0-9]+$|/libstdc\+\+\.so\.[0-9]+$|/libssl\.so\.[0-9]+$|/libcrypto\.so\.[0-9]+$' \
        | xargs -r -I{} cp -v {} "${TP_LIB_DIR}/"; \
    fi; \
  done; \
  \
  # 3) Soname symlinks (common variants)
  if [ -f "${TP_LIB_DIR}/libgrpc++.so.1.51.1" ] && [ ! -f "${TP_LIB_DIR}/libgrpc++.so.1.51" ]; then \
    ln -sv "${TP_LIB_DIR}/libgrpc++.so.1.51.1" "${TP_LIB_DIR}/libgrpc++.so.1.51"; \
  fi; \
  if ls "${TP_LIB_DIR}"/libprotobuf.so.32* > /dev/null 2>&1; then \
    [ -f "${TP_LIB_DIR}/libprotobuf.so.32" ] || ln -sv "$(ls -1 ${TP_LIB_DIR}/libprotobuf.so.32* | head -n1)" "${TP_LIB_DIR}/libprotobuf.so.32"; \
  fi; \
  \
  # 4) Installer script (NO global ldconfig)
  cat > "${SDK_ROOT}/install.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
# No global ldconfig; module relies on $ORIGIN-based RPATH.
echo "OpenTelemetry Webserver SDK installed."
EOF
  chmod +x "${SDK_ROOT}/install.sh"; \
  \
  # 5) Module-local RPATH
  patchelf --set-rpath '$ORIGIN/../sdk_lib/lib:$ORIGIN/../third_party/lib' \
    "${SDK_ROOT}/WebServerModule/Nginx/${NGINX_VERSION}/ngx_http_opentelemetry_module.so"; \
  patchelf --print-rpath \
    "${SDK_ROOT}/WebServerModule/Nginx/${NGINX_VERSION}/ngx_http_opentelemetry_module.so"; \
  \
  # 6) Sanity: critical exporter client lib exists
  test -f "${SDK_LIB_DIR}/libopentelemetry_exporter_otlp_grpc_client.so" \
    || (echo "ERROR: missing libopentelemetry_exporter_otlp_grpc_client.so in ${SDK_LIB_DIR}" && ls -l "${SDK_LIB_DIR}" && exit 1); \
  \
  # 7) Re-pack augmented SDK tarball
  cd "${SDK_ROOT}/.."; \
  mkdir -p /otel-webserver-module/build; \
  tar -czf /otel-webserver-module/build/opentelemetry-webserver-sdk-x64-linux.tgz \
    opentelemetry-webserver-sdk; \
  echo "=== Bundled SDK libs (sdk_lib/lib) ==="; \
  ls -l "${SDK_LIB_DIR}" | sed 's/^/  /' || true; \
  echo "=== Bundled third-party libs (third_party/lib) ==="; \
  ls -l "${TP_LIB_DIR}" | sed 's/^/  /' || true

# ---- (Optional) ldd module check ----
RUN set -eux; \
  echo "==== ldd check (NGINX OTEL module) ===="; \
  ldd "/opt/opentelemetry-webserver-sdk/WebServerModule/Nginx/${NGINX_VERSION}/ngx_http_opentelemetry_module.so" || true

# ---- Entrypoint (builder stage only) ----
COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]
