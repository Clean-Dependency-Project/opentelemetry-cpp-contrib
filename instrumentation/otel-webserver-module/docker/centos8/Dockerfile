# ========================================================================
# Base: Debian 12 (Bookworm) + GCC 12 + glibc 2.36 + Python 2.7.8
# ========================================================================
FROM debian:12

ARG BUILD_NUMBER
LABEL NAME="apm/build-image-nginx-otel-debian12-x64" VERSION=$BUILD_NUMBER

ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

ARG NGINX_VERSION="1.29.3"
ARG OPENTELEMETRY_VERSION="1.23.0"
ARG BOOST_VERSION="1.75.0"
ARG GRPC_VERSION="1.57.0"
ARG LOG4CXX_VERSION="0.11.0"
ARG APR_VERSION="1.7.0"
ARG EXPAT_VERSION="2.3.0"
ARG EXPAT_RVERSION="R_2_3_0"
ARG APRUTIL_VERSION="1.6.1"
ARG LIBTOOL_VERSION="2.4.6"
ARG BOOST_FILENAME="boost_1_75_0"
ARG PYTHON_VERSION="2.7.8"

# ------------------------------------------------------------------------
# System dependencies
# ------------------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    build-essential gcc g++ make cmake git wget curl xz-utils unzip \
    zlib1g-dev libssl-dev libpcre3-dev bzip2 libbz2-dev \
    autoconf automake libtool pkg-config m4 perl \
    openjdk-17-jdk \
    libprotobuf-dev protobuf-compiler \
    libgrpc++-dev libgrpc-dev \
    libabsl-dev libc-ares-dev libzstd-dev libre2-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------------
# Python 2.7.8
# ------------------------------------------------------------------------
RUN wget http://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz \
    && tar -xf Python-${PYTHON_VERSION}.tar.xz \
    && cd Python-${PYTHON_VERSION} \
    && ./configure --prefix=/usr/local && make -j$(nproc) && make install \
    && cd .. && rm -rf Python-${PYTHON_VERSION}*

# ------------------------------------------------------------------------
# Directory prep
# ------------------------------------------------------------------------
RUN mkdir -p /dependencies

# ------------------------------------------------------------------------
# Boost
# ------------------------------------------------------------------------
RUN wget https://archives.boost.io/release/${BOOST_VERSION}/source/${BOOST_FILENAME}.tar.gz \
    && tar -xzf ${BOOST_FILENAME}.tar.gz \
    && cd ${BOOST_FILENAME} \
    && ./bootstrap.sh --with-libraries=filesystem,system --prefix=/dependencies/boost/${BOOST_VERSION} \
    && ./b2 install threading=multi link=static cxxflags="-fPIC" cflags="-fPIC" \
    && cd .. && rm -rf ${BOOST_FILENAME}*

# ------------------------------------------------------------------------
# gRPC (from source - correct for Debian)
# ------------------------------------------------------------------------
RUN git clone https://github.com/grpc/grpc \
    && cd grpc \
    && git checkout v${GRPC_VERSION} \
    && git submodule update --init --recursive \
    && mkdir -p build && cd build \
    && cmake .. \
        -DgRPC_INSTALL=ON \
        -DCMAKE_BUILD_TYPE=Release \
        -DgRPC_BUILD_TESTS=OFF \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd ../.. \
    && rm -rf grpc

# ------------------------------------------------------------------------
# APR
# ------------------------------------------------------------------------
RUN wget https://archive.apache.org/dist/apr/apr-${APR_VERSION}.tar.gz \
    && tar -xzf apr-${APR_VERSION}.tar.gz \
    && cd apr-${APR_VERSION} \
    && ./configure --prefix=/dependencies/apr/${APR_VERSION} --enable-static=yes --enable-shared=no --with-pic \
    && make -j$(nproc) && make install \
    && cd .. && rm -rf apr-${APR_VERSION}*

# ------------------------------------------------------------------------
# Expat
# ------------------------------------------------------------------------
RUN wget https://github.com/libexpat/libexpat/releases/download/${EXPAT_RVERSION}/expat-${EXPAT_VERSION}.tar.gz \
    && tar -xzf expat-${EXPAT_VERSION}.tar.gz \
    && cd expat-${EXPAT_VERSION} \
    && ./configure --prefix=/dependencies/expat/${EXPAT_VERSION} \
        --enable-shared=no --enable-static=yes --with-pic \
    && make -j$(nproc) && make install \
    && cd .. && rm -rf expat-${EXPAT_VERSION}*

# ------------------------------------------------------------------------
# APR-util
# ------------------------------------------------------------------------
RUN wget https://archive.apache.org/dist/apr/apr-util-${APRUTIL_VERSION}.tar.gz \
    && tar -xzf apr-util-${APRUTIL_VERSION}.tar.gz \
    && cd apr-util-${APRUTIL_VERSION} \
    && ./configure \
        --prefix=/dependencies/apr-util/${APRUTIL_VERSION} \
        --enable-shared=no --enable-static=yes --with-pic \
        --with-apr=/dependencies/apr/${APR_VERSION} \
        --with-expat=/dependencies/expat/${EXPAT_VERSION} \
    && make -j$(nproc) && make install \
    && cd .. && rm -rf apr-util-${APRUTIL_VERSION}*

# ------------------------------------------------------------------------
# libtool
# ------------------------------------------------------------------------
RUN wget https://ftpmirror.gnu.org/libtool/libtool-${LIBTOOL_VERSION}.tar.gz \
    && tar -xzf libtool-${LIBTOOL_VERSION}.tar.gz \
    && cd libtool-${LIBTOOL_VERSION} \
    && ./configure --prefix=/usr && make -j$(nproc) && make install \
    && cd .. && rm -rf libtool-${LIBTOOL_VERSION}*

# ------------------------------------------------------------------------
# log4cxx (Debian fix)
# ------------------------------------------------------------------------
RUN wget https://archive.apache.org/dist/logging/log4cxx/${LOG4CXX_VERSION}/apache-log4cxx-${LOG4CXX_VERSION}.tar.gz \
    && tar -xzf apache-log4cxx-${LOG4CXX_VERSION}.tar.gz \
    && cd apache-log4cxx-${LOG4CXX_VERSION} \
    && autoreconf -fi \
    && automake --add-missing --copy --force-missing \
    && ./configure --prefix=/dependencies/apache-log4cxx/${LOG4CXX_VERSION} \
        --enable-static=yes --enable-shared=no \
        --with-pic \
        --with-apr=/dependencies/apr/${APR_VERSION} \
        --with-apr-util=/dependencies/apr-util/${APRUTIL_VERSION} \
    && make -j$(nproc) && make install \
    && cd .. && rm -rf apache-log4cxx-${LOG4CXX_VERSION}*

# ------------------------------------------------------------------------
# OpenTelemetry C++ SDK (correct + complete)
# ------------------------------------------------------------------------
RUN mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib \
    && mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include \
    && git clone https://github.com/open-telemetry/opentelemetry-cpp \
    && cd opentelemetry-cpp \
    && git checkout v${OPENTELEMETRY_VERSION} \
    && git submodule update --init --recursive \
    && mkdir build && cd build \
    && cmake .. \
        -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
        -DBUILD_TESTING=OFF \
        -DBUILD_SHARED_LIBS=ON \
        -DWITH_OTLP=ON \
        -DWITH_OTLP_GRPC=ON \
        -DWITH_OTLP_HTTP=ON \
        -DCMAKE_CXX_STANDARD=14 \
        -DCMAKE_INSTALL_PREFIX=/dependencies/opentelemetry/${OPENTELEMETRY_VERSION} \
    && make -j$(nproc) \
    && make install \
    && cd .. \
    && cp -r api/include/ /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/ \
    && cp -r exporters/*/include /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/ || true \
    && cp -r sdk/include/ /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/ \
    && cp -r ext/include/ /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/ || true \
    && find . -name "*.so" -exec cp {} /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/ \; \
    && cd .. && rm -rf opentelemetry-cpp

# ------------------------------------------------------------------------
# Nginx source
# ------------------------------------------------------------------------
RUN mkdir /build-dependencies \
    && wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz \
    && tar -xzf nginx-${NGINX_VERSION}.tar.gz -C /build-dependencies \
    && rm nginx-${NGINX_VERSION}.tar.gz

# ------------------------------------------------------------------------
# Build module
# ------------------------------------------------------------------------
COPY . /otel-webserver-module
RUN cp -r /dependencies /otel-webserver-module/ \
    && cp -r /build-dependencies /otel-webserver-module/ \
    && cd /otel-webserver-module \
    && ./gradlew assembleWebServerModule

# ------------------------------------------------------------------------
# Install nginx
# ------------------------------------------------------------------------
RUN apt-get update && apt-get install -y nginx && apt-get clean

# ------------------------------------------------------------------------
# Configure nginx to load module
# ------------------------------------------------------------------------
RUN cd /otel-webserver-module/build \
    && tar -xzf opentelemetry-webserver-sdk-x64-linux.tgz \
    && mv opentelemetry-webserver-sdk /opt/ \
    && cp /otel-webserver-module/conf/nginx/opentelemetry_module.conf /opt/ \
    && sed -i "1iload_module /opt/opentelemetry-webserver-sdk/WebServerModule/Nginx/${NGINX_VERSION}/ngx_http_opentelemetry_module.so;" /etc/nginx/nginx.conf \
    && sed -i "33i include /opt/opentelemetry_module.conf;" /etc/nginx/nginx.conf

COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]
