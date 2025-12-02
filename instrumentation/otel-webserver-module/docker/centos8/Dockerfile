# ============================================================
# Base: Debian 12 (matches Debian-built Nginx you are using)
# GCC 14.2.0 is available and ABI compatible
# ============================================================
FROM debian:12-slim

ARG BUILD_NUMBER
LABEL NAME="apm/build-image-nginx-otel-debian12-x64" VERSION=$BUILD_NUMBER

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

ARG NGINX_VERSION="1.29.3"
ARG OPENTELEMETRY_VERSION="1.23.0"
ARG BOOST_VERSION="1.75.0"
ARG BOOST_FILENAME="boost_1_75_0"
ARG APR_VERSION="1.7.0"
ARG APRUTIL_VERSION="1.6.1"
ARG EXPAT_VERSION="2.3.0"
ARG EXPAT_RVERSION="R_2_3_0"
ARG LOG4CXX_VERSION="0.11.0"
ARG PYTHON_VERSION="2.7.8"

# ============================================================
# Install compilers & build tools
# GCC 14.2.0 is default on Debian 12
# ============================================================
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc g++ \
    cmake \
    git wget curl tar xz-utils unzip \
    zlib1g-dev libssl-dev libpcre3-dev bzip2 \
    autoconf automake libtool pkg-config \
    libprotobuf-dev protobuf-compiler \
    libgrpc-dev libabsl-dev libre2-dev libc-ares-dev \
    openjdk-17-jdk \
    python3 python3-distutils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ============================================================
# Build Python 2.7.8 (required by GYP — exact version as required)
# ============================================================
RUN wget http://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz \
    && tar -xf Python-${PYTHON_VERSION}.tar.xz \
    && cd Python-${PYTHON_VERSION} \
    && ./configure --prefix=/usr/local --enable-shared \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf Python-${PYTHON_VERSION} Python-${PYTHON_VERSION}.tar.xz

# ============================================================
# Create dependency directory
# ============================================================
RUN mkdir -p /dependencies

# ============================================================
# BOOST
# ============================================================
RUN wget https://archives.boost.io/release/${BOOST_VERSION}/source/${BOOST_FILENAME}.tar.gz \
    && tar -xvf ${BOOST_FILENAME}.tar.gz \
    && cd ${BOOST_FILENAME} \
    && ./bootstrap.sh --with-libraries=filesystem,system --prefix=/dependencies/boost/${BOOST_VERSION} \
    && ./b2 install -j$(nproc) cxxflags="-fPIC" cflags="-fPIC" \
    && cd .. && rm -rf ${BOOST_FILENAME}*

# ============================================================
# APR
# ============================================================
RUN wget https://archive.apache.org/dist/apr/apr-${APR_VERSION}.tar.gz \
    && tar -xf apr-${APR_VERSION}.tar.gz \
    && cd apr-${APR_VERSION} \
    && ./configure --prefix=/dependencies/apr/${APR_VERSION} --enable-static --disable-shared --with-pic \
    && make -j$(nproc) && make install \
    && cd .. && rm -rf apr-${APR_VERSION}*

# ============================================================
# EXPAT
# ============================================================
RUN wget https://github.com/libexpat/libexpat/releases/download/${EXPAT_RVERSION}/expat-${EXPAT_VERSION}.tar.gz \
    && tar -xf expat-${EXPAT_VERSION}.tar.gz \
    && cd expat-${EXPAT_VERSION} \
    && ./configure --prefix=/dependencies/expat/${EXPAT_VERSION} --enable-static --disable-shared --with-pic \
    && make -j$(nproc) && make install \
    && cd .. && rm -rf expat-${EXPAT_VERSION}*

# ============================================================
# APR-UTIL
# ============================================================
RUN wget https://archive.apache.org/dist/apr/apr-util-${APRUTIL_VERSION}.tar.gz \
    && tar -xf apr-util-${APRUTIL_VERSION}.tar.gz \
    && cd apr-util-${APRUTIL_VERSION} \
    && ./configure \
        --prefix=/dependencies/apr-util/${APRUTIL_VERSION} \
        --enable-static --disable-shared --with-pic \
        --with-apr=/dependencies/apr/${APR_VERSION} \
        --with-expat=/dependencies/expat/${EXPAT_VERSION} \
    && make -j$(nproc) && make install \
    && cd .. && rm -rf apr-util-${APRUTIL_VERSION}*

# ============================================================
# LOG4CXX
# ============================================================
RUN wget https://archive.apache.org/dist/logging/log4cxx/${LOG4CXX_VERSION}/apache-log4cxx-${LOG4CXX_VERSION}.tar.gz \
    && tar -xf apache-log4cxx-${LOG4CXX_VERSION}.tar.gz \
    && cd apache-log4cxx-${LOG4CXX_VERSION} \
    && ./configure \
        --prefix=/dependencies/apache-log4cxx/${LOG4CXX_VERSION} \
        --enable-static --disable-shared --with-pic \
        --with-apr=/dependencies/apr/${APR_VERSION} \
        --with-apr-util=/dependencies/apr-util/${APRUTIL_VERSION} \
    && make -j$(nproc) && make install \
    && cd .. && rm -rf apache-log4cxx-${LOG4CXX_VERSION}*

# ============================================================
# OpenTelemetry C++ SDK
# ============================================================
RUN mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib \
    && git clone https://github.com/open-telemetry/opentelemetry-cpp \
    && cd opentelemetry-cpp \
    && git checkout tags/v${OPENTELEMETRY_VERSION} -b v${OPENTELEMETERY_VERSION} \
    && git submodule update --init --recursive \
    && mkdir build && cd build \
    && cmake .. \
        -DCMAKE_CXX_STANDARD=14 \
        -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
        -DBUILD_TESTING=OFF \
        -DBUILD_SHARED_LIBS=ON \
        -DWITH_OTLP=ON \
        -DWITH_OTLP_HTTP=ON \
        -DWITH_OTLP_GRPC=ON \
        -DCMAKE_INSTALL_PREFIX=/dependencies/opentelemetry/${OPENTELEMETRY_VERSION} \
    && cmake --build . -j$(nproc) \
    && cmake --install . \
    && cd ../.. && rm -rf opentelemetry-cpp

# ============================================================
# Download Nginx source for module build
# ============================================================
RUN mkdir /build-dependencies \
    && wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz \
    && tar -xvf nginx-${NGINX_VERSION}.tar.gz -C /build-dependencies \
    && rm -f nginx-${NGINX_VERSION}.tar.gz

# ============================================================
# Copy module source
# ============================================================
COPY . /otel-webserver-module

RUN cp -r /dependencies /otel-webserver-module \
    && cp -r /build-dependencies /otel-webserver-module \
    && cd /otel-webserver-module \
    && ./gradlew assembleWebServerModule

# ============================================================
# Install Nginx from nginx.org Debian repo
# (compatible with Debian ABI)
# ============================================================
RUN apt-get update \
    && apt-get install -y gnupg2 lsb-release ca-certificates \
    && curl -o /usr/share/keyrings/nginx-keyring.gpg \
        https://nginx.org/keys/nginx_signing.key \
    && echo "deb [signed-by=/usr/share/keyrings/nginx-keyring.gpg] \
        http://nginx.org/packages/mainline/debian `lsb_release -cs` nginx" \
        > /etc/apt/sources.list.d/nginx.list \
    && apt-get update \
    && apt-get install -y nginx=${NGINX_VERSION}-1~`lsb_release -cs` \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ============================================================
# Configure Nginx to load module
# ============================================================
RUN cd /otel-webserver-module/build \
    && tar -xf opentelemetry-webserver-sdk-x64-linux.tgz \
    && mv -f opentelemetry-webserver-sdk /opt/ \
    && cp /otel-webserver-module/conf/nginx/opentelemetry_module.conf /opt/ \
    && sed -i "8i load_module /opt/opentelemetry-webserver-sdk/WebServerModule/Nginx/${NGINX_VERSION}/ngx_http_opentelemetry_module.so;" /etc/nginx/nginx.conf \
    && sed -i "33i include /opt/opentelemetry_module.conf;" /etc/nginx/nginx.conf

COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]