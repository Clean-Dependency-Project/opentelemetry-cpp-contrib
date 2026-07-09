# syntax=docker/dockerfile:1.4
###############################################
# Stage: BUILD on Debian 13 (Trixie)
###############################################
FROM debian:trixie-slim AS builder
ARG BUILD_NUMBER
LABEL NAME="apm/build-image-nginx-otel-debian13-x64" VERSION=${BUILD_NUMBER}

# ---- Versions ----
ARG NGINX_VERSION="1.31.2"
ARG OPENTELEMETRY_VERSION="1.24.0"
ARG BOOST_VERSION="1.75.0"
ARG LOG4CXX_VERSION="0.11.0"
ARG APR_VERSION="1.7.6"
ARG APRUTIL_VERSION="1.6.1"
ARG EXPAT_VERSION="2.3.0"
ARG EXPAT_RVERSION="R_2_3_0"
ARG LIBTOOL_VERSION="2.4.6"
ARG BOOST_FILENAME="boost_1_75_0"
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# ---- Toolchain & base build deps ----
RUN set -eux; \
  apt-get update; \
  apt-get install -y --no-install-recommends \
    build-essential git make wget curl ca-certificates xz-utils tar unzip which \
    cmake pkg-config ninja-build \
    zlib1g-dev libssl-dev libpcre2-dev \
    default-jdk \
    perl m4 autoconf automake libtool \
    libabsl-dev libre2-dev libc-ares-dev \
    libgrpc-dev libgrpc++-dev libgrpc++1 \
    libprotobuf-dev protobuf-compiler protobuf-compiler-grpc \
    file gnupg patchelf \
    python3 python3-venv python3-pip; \
  rm -rf /var/lib/apt/lists/*

# ---- Python 3 + gyp-next in venv ----
RUN set -eux; \
  python3 -m venv /opt/gyp-venv; \
  /opt/gyp-venv/bin/pip install --no-cache-dir gyp-next; \
  /opt/gyp-venv/bin/python -c "import gyp; print('gyp module OK:', gyp.__file__)"

# ---- Directory prep ----
RUN mkdir -p /dependencies

# ---- Boost (filesystem, system) static with PIC ----
RUN set -eux; \
  wget https://archives.boost.io/release/${BOOST_VERSION}/source/${BOOST_FILENAME}.tar.gz; \
  tar -xvf ${BOOST_FILENAME}.tar.gz; \
  cd ${BOOST_FILENAME}; \
  ./bootstrap.sh --with-libraries=filesystem,system --prefix=/dependencies/boost/${BOOST_VERSION}; \
  ./b2 install define=BOOST_ERROR_CODE_HEADER_ONLY link=static threading=multi \
    cxxflags="-fvisibility=hidden -fPIC" cflags="-fvisibility=hidden -fPIC"; \
  cd ..; \
  rm -rf ${BOOST_FILENAME}*

# ---- APR (static) ----
RUN set -eux; \
  mkdir -p /dependencies/apr/${APR_VERSION}; \
  wget https://dlcdn.apache.org/apr/apr-${APR_VERSION}.tar.gz; \
  tar -xf apr-${APR_VERSION}.tar.gz; \
  cd apr-${APR_VERSION}; \
  ./configure --prefix=/dependencies/apr/${APR_VERSION} --enable-static=yes --enable-shared=no --with-pic; \
  make -j"$(nproc)"; \
  make install; \
  cd ..; rm -rf apr-${APR_VERSION}*

# ---- Expat (static) ----
RUN set -eux; \
  mkdir -p /dependencies/expat/${EXPAT_VERSION}; \
  wget https://github.com/libexpat/libexpat/releases/download/${EXPAT_RVERSION}/expat-${EXPAT_VERSION}.tar.gz --no-check-certificate; \
  tar -xf expat-${EXPAT_VERSION}.tar.gz; \
  cd expat-${EXPAT_VERSION}; \
  ./configure --prefix=/dependencies/expat/${EXPAT_VERSION} --enable-static=yes --enable-shared=no --with-pic; \
  make -j"$(nproc)"; make install; \
  cd ..; rm -rf expat-${EXPAT_VERSION}*

# ---- APR-util (static) ----
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

# ---- libtool (host) ----
RUN set -eux; \
  wget --no-check-certificate https://ftpmirror.gnu.org/libtool/libtool-${LIBTOOL_VERSION}.tar.gz; \
  tar xzf libtool-${LIBTOOL_VERSION}.tar.gz; \
  cd libtool-${LIBTOOL_VERSION}; \
  ./configure --prefix=/usr; \
  make -j"$(nproc)"; make install; \
  libtool --version; \
  cd ..; rm -rf libtool-${LIBTOOL_VERSION}*

# ---- Apache log4cxx (static) ----
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
  cd ..; rm -rf apache-log4cxx-${LOG4CXX_VERSION}*

# ---- OpenTelemetry C++ SDK (shared libs) ----
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
  find . -type f -name "*.so" -exec cp -v {} /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/ \;; \
  cd ../..; \
  PROTO_ROOT_DIR="$(find /opentelemetry-cpp -type f -path '*/opentelemetry/proto/*/*.pb.h' -printf '%h\n' \
    | sed -E 's#^(.*opentelemetry/proto).*#\1#' | head -n 1)"; \
  if [ -n "${PROTO_ROOT_DIR}" ] && [ -d "${PROTO_ROOT_DIR}" ]; then \
    echo "Discovered proto root: ${PROTO_ROOT_DIR}"; \
    mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry/; \
    cp -r "${PROTO_ROOT_DIR}" /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry/; \
  else \
    echo "ERROR: Could not locate generated opentelemetry/proto/*.pb.h in build tree." >&2; \
    find /opentelemetry-cpp -type f -name '*.pb.h' | sed 's/^/ /'; \
    exit 1; \
  fi; \
  test -f /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry/proto/trace/v1/trace.pb.h; \
  rm -rf /opentelemetry-cpp

# ---- NGINX source headers (for module build) ----
RUN set -eux; \
  mkdir /build-dependencies; \
  wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz; \
  tar -xvf nginx-${NGINX_VERSION}.tar.gz -C /build-dependencies; \
  rm -f nginx-${NGINX_VERSION}.tar.gz

# ---- Copy module sources ----
COPY . /otel-webserver-module

# ---- Shim bundled GYP runner to gyp-next console script ----
RUN set -eux; \
  mkdir -p /otel-webserver-module/scripts/gyp/r1919; \
  cat > /otel-webserver-module/scripts/gyp/r1919/gyp <<'EOF'
#!/usr/bin/env bash
# Run gyp-next console script from our isolated venv
exec /opt/gyp-venv/bin/gyp "$@"
EOF
RUN chmod +x /otel-webserver-module/scripts/gyp/r1919/gyp

# ---- Build (use venv; keep PATH consistent) ----
RUN set -eux; \
  cp -r /dependencies /otel-webserver-module/; \
  cp -r /build-dependencies /otel-webserver-module/; \
  cd /otel-webserver-module; \
  chmod +x ./gradlew; \
  export PATH="/opt/gyp-venv/bin:${PATH}"; \
  ./gradlew assembleWebServerModule --info

# ---- Unpack SDK & augment (exclude core + OpenSSL) ----
RUN set -eux; \
  cd /otel-webserver-module/build; \
  tar -xf opentelemetry-webserver-sdk-x64-linux.tgz; \
  SDK_ROOT="/opt/opentelemetry-webserver-sdk"; \
  rm -rf "${SDK_ROOT}"; \
  mv -f opentelemetry-webserver-sdk "${SDK_ROOT}"; \
  mkdir -p "${SDK_ROOT}/sdk_lib/lib" "${SDK_ROOT}/third_party/lib"; \
  SDK_LIB_DIR="${SDK_ROOT}/sdk_lib/lib"; \
  TP_LIB_DIR="${SDK_ROOT}/third_party/lib"; \
  cp -v /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/libopentelemetry_*.so "${SDK_LIB_DIR}/" || true; \
  cp -v /usr/local/lib/libopentelemetry_*.so "${SDK_LIB_DIR}/" || true; 

# ---- Bundle gRPC / Protobuf runtime deps ----
RUN set -eux; \
  SDK_LIB_DIR="/opt/opentelemetry-webserver-sdk/sdk_lib/lib"; \
  for lib in \
    libgrpc++.so* \
    libgrpc.so* \
    libprotobuf.so* \
    libabsl_*.so* \
    libc-ares.so* \
  ; do \
    find /usr/lib /lib -name "$lib" -exec cp -v {} "${SDK_LIB_DIR}/" \; || true; \
  done

COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]


