
# ===============================
# Stage 1: BUILD on Debian 12
# ===============================
FROM debian:12-slim AS builder

ARG BUILD_NUMBER
LABEL NAME="apm/build-image-nginx-otel-debian12-x64" VERSION=${BUILD_NUMBER}

# Keep your version ARGs as-is for alignment
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
ARG PYTHON_VERSION="2.7.8"           # you built Python 2.7 for GYP before  [1](https://fnma-my.sharepoint.com/personal/s9ubfm_fanniemae_com/Documents/Microsoft%20Copilot%20Chat%20Files/Dockerfile123.txt)

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# --- System toolchain & build deps (Debian) ---


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
    file gnupg; \
  rm -rf /var/lib/apt/lists/*

# --- Build Python 2.7 (for legacy GYP workflows you carried) ---
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

# --- Directory prep ---
RUN mkdir -p /dependencies

# --- Build Boost (filesystem, system) as static with PIC (like your flow) ---
RUN set -eux; \
    wget https://archives.boost.io/release/${BOOST_VERSION}/source/${BOOST_FILENAME}.tar.gz; \
    tar -xvf ${BOOST_FILENAME}.tar.gz; \
    cd ${BOOST_FILENAME}; \
    ./bootstrap.sh --with-libraries=filesystem,system --prefix=/dependencies/boost/${BOOST_VERSION}; \
    ./b2 install define=BOOST_ERROR_CODE_HEADER_ONLY link=static threading=multi \
         cxxflags="-fvisibility=hidden -fPIC" cflags="-fvisibility=hidden -fPIC"; \
    cd ..; \
    rm -rf ${BOOST_FILENAME}*

# --- Build APR, Expat, APR-util (static) ---
RUN set -eux; \
    mkdir -p /dependencies/apr/${APR_VERSION}; \
    wget https://archive.apache.org/dist/apr/apr-${APR_VERSION}.tar.gz --no-check-certificate; \
    tar -xf apr-${APR_VERSION}.tar.gz; \
    cd apr-${APR_VERSION}; \
    ./configure --prefix=/dependencies/apr/${APR_VERSION} --enable-static=yes --enable-shared=no --with-pic; \
    make -j"$(nproc)"; make install; \
    cd ..; \
    rm -rf apr-${APR_VERSION}*

RUN set -eux; \
    mkdir -p /dependencies/expat/${EXPAT_VERSION}; \
    wget https://github.com/libexpat/libexpat/releases/download/${EXPAT_RVERSION}/expat-${EXPAT_VERSION}.tar.gz --no-check-certificate; \
    tar -xf expat-${EXPAT_VERSION}.tar.gz; \
    cd expat-${EXPAT_VERSION}; \
    ./configure --prefix=/dependencies/expat/${EXPAT_VERSION} --enable-static=yes --enable-shared=no --with-pic; \
    make -j"$(nproc)"; make install; \
    cd ..; \
    rm -rf expat-${EXPAT_VERSION}*

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
    cd ..; \
    rm -rf apr-util-${APRUTIL_VERSION}*

# --- Build libtool (matching your flow) ---
RUN set -eux; \
    wget --no-check-certificate https://ftpmirror.gnu.org/libtool/libtool-${LIBTOOL_VERSION}.tar.gz; \
    tar xzf libtool-${LIBTOOL_VERSION}.tar.gz; \
    cd libtool-${LIBTOOL_VERSION}; \
    ./configure --prefix=/usr; \
    make -j"$(nproc)"; \
    make install; \
    libtool --version; \
    cd ..; \
    rm -rf libtool-${LIBTOOL_VERSION}.tar.gz libtool-${LIBTOOL_VERSION}

# --- Build Apache log4cxx (static, with APR / APR-util) ---

# Build log4cxx
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
    make -j"$(nproc)"; \
    make install; \
    cd ..; \
    rm -rf apache-log4cxx-${LOG4CXX_VERSION}* apache-log4cxx-${LOG4CXX_VERSION}.tar.gz

# Build OpenTelemetry C++ SDK
RUN set -eux; \
    mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib; \
    mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include; \
    git clone https://github.com/open-telemetry/opentelemetry-cpp; \
    cd opentelemetry-cpp; \
    git checkout tags/v${OPENTELEMETRY_VERSION} -b v${OPENTELEMETRY_VERSION}; \
    git submodule update --init --recursive; \
    mkdir build; cd build; \
    cmake .. \
      -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
      -DBUILD_TESTING=OFF \
      -DBUILD_SHARED_LIBS=ON \
      -DWITH_OTLP=ON \
      -DWITH_OTLP_GRPC=ON \
      -DWITH_OTLP_HTTP=ON \
      -DCMAKE_CXX_STANDARD=14 \
      -DCMAKE_CXX_STANDARD_REQUIRED=ON \
      -DCMAKE_PREFIX_PATH="/usr" \
      -DProtobuf_DIR="/usr/lib/x86_64-linux-gnu/cmake/protobuf" \
      -DProtobuf_INCLUDE_DIR="/usr/include" \
      -DgRPC_DIR="/usr/lib/x86_64-linux-gnu/cmake/grpc" \
      -Dabsl_DIR="/usr/lib/x86_64-linux-gnu/cmake/absl"; \
    cmake --build . --target all -j"$(nproc)"; \
    cmake --install .; \
    # copy any .so artifacts (no stray '; ;')
    find . -name "*.so" -type f -exec cp -v {} /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/ \; ; \
    # stage generated proto headers
    FOUND_PB_HEADER="$(find . -type f -name '*.pb.h' | head -n 1)"; \
    if [ -n "$FOUND_PB_HEADER" ]; then \
        PROTO_ROOT="$(echo "$FOUND_PB_HEADER" | sed -E 's#^(.*opentelemetry/proto).*#\1#')"; \
        echo "Discovered proto headers at: $PROTO_ROOT"; \
        mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry/; \
        cp -r "$PROTO_ROOT" /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry/; \
    else \
        echo "ERROR: Could not locate any generated *.pb.h in build tree." >&2; \
        exit 1; \
    fi; \
    test -f /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry/proto/trace/v1/trace.pb.h; \
    cd ../..; \
    rm -rf opentelemetry-cpp


# --- Download NGINX source (headers used by Gradle build) ---
RUN set -eux; \
    mkdir /build-dependencies; \
    wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz; \
    tar -xvf nginx-${NGINX_VERSION}.tar.gz -C /build-dependencies; \
    rm -f nginx-${NGINX_VERSION}.tar.gz

# --- Copy your module code and run Gradle task (as in your file) ---
#     (I mirror your approach: copy /dependencies and /build-dependencies into the module tree, then run ./gradlew)
COPY . /otel-webserver-module
RUN set -eux; \
    cp -r /dependencies /otel-webserver-module/; \
    cp -r /build-dependencies /otel-webserver-module/; \
    cd /otel-webserver-module; \
    chmod +x ./gradlew; \
    ./gradlew assembleWebServerModule

# --- Unpack the produced SDK tarball and patch runtime deps into its lib dir ---
RUN set -eux; \
    cd /otel-webserver-module/build; \
    tar -xf opentelemetry-webserver-sdk-x64-linux.tgz; \
    mv -f opentelemetry-webserver-sdk /opt/; \
    cd /; \
    # Make sdk_lib/lib discoverable and copy OTel libs we built (if any missing)
    echo "/opt/opentelemetry-webserver-sdk/sdk_lib/lib" > /etc/ld.so.conf.d/opentelemetry-webserver-sdk.conf; \
    ldconfig; \
    cp -v /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/libopentelemetry_*.so \
          /opt/opentelemetry-webserver-sdk/sdk_lib/lib/ || true; \
    # Resolve and copy transitive libs for core OTLP exporters
    SDK_LIB_DIR="/opt/opentelemetry-webserver-sdk/sdk_lib/lib"; \
    mkdir -p "${SDK_LIB_DIR}"; \
    for LIB in \
      /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/libopentelemetry_exporter_otlp_grpc.so \
      /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/libopentelemetry_exporter_otlp_grpc_client.so \
      /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/libopentelemetry_proto.so \
    ; do \
      if [ -f "${LIB}" ]; then \
        echo "Resolving transitive deps for: ${LIB}"; \
        ldd "${LIB}" \
          | awk '/=>/ && $3 ~ /^\// {print $3} !/=>/ {for(i=1;i<=NF;i++) if($i ~ /^\//) print $i}' \
          | sort -u \
          | xargs -r -I{} cp -v {} "${SDK_LIB_DIR}/"; \
      fi; \
    done; \
    ldconfig

# Validate module linkage in the builder image
RUN set -eux; \
    echo "==== ldd check (NGINX OTEL module) ===="; \
    ldd /opt/opentelemetry-webserver-sdk/WebServerModule/Nginx/${NGINX_VERSION}/ngx_http_opentelemetry_module.so || true \
    echo "==== nginx -t ====" \
    nginx -t

# Entrypoint
COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]