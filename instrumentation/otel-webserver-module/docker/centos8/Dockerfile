# ========================================================================
# Base: CentOS Stream 9 + GCC 13 + glibc 2.34
# ========================================================================
FROM quay.io/centos/centos:stream9

ARG BUILD_NUMBER
LABEL NAME="apm/build-image-nginx-otel-centos9-x64" VERSION=$BUILD_NUMBER

ENV LANG=C.UTF-8
ENV PATH="/opt/rh/gcc-toolset-13/root/usr/bin:${PATH}"

ARG NGINX_VERSION="1.29.3"
ARG OPENTELEMETRY_VERSION="1.23.0"
ARG BOOST_VERSION="1.75.0"
ARG BOOST_FILENAME="boost_1_75_0"
ARG LOG4CXX_VERSION="0.11.0"
ARG APR_VERSION="1.7.0"
ARG APRUTIL_VERSION="1.6.1"
ARG EXPAT_VERSION="2.3.0"
ARG EXPAT_RVERSION="R_2_3_0"
ARG PYTHON_VERSION="2.7.8"

# ========================================================================
# System basic deps
# ========================================================================
RUN dnf -y update && \
    dnf install -y \
        gcc-toolset-13 git make wget tar xz unzip which cmake3 \
        zlib-devel openssl-devel pcre-devel bzip2-devel \
        java-17-openjdk java-17-openjdk-devel \
        perl m4 autoconf automake libtool && \
    dnf clean all

# ========================================================================
# Enable CRB + EPEL + EPEL-next
# ========================================================================
RUN dnf install -y epel-release epel-next-release && \
    dnf config-manager --set-enabled crb && \
    dnf makecache

# ========================================================================
# Install system gRPC, Protobuf, Abseil, re2, c-ares
# ========================================================================
RUN dnf install -y \
       grpc \
       grpc-devel \
       protobuf \
       protobuf-devel \
       abseil-cpp \
       abseil-cpp-devel \
       re2 \
       re2-devel \
       c-ares \
       c-ares-devel \
    && dnf clean all

# ========================================================================
# Python 2.7 for GYP
# ========================================================================
RUN wget http://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz \
    && unxz Python-${PYTHON_VERSION}.tar.xz \
    && tar -xf Python-${PYTHON_VERSION}.tar \
    && cd Python-${PYTHON_VERSION} && ./configure --prefix=/usr/local && make && make install \
    && cd .. && rm -rf Python-${PYTHON_VERSION}*

# ========================================================================
# Dependency dirs
# ========================================================================
RUN mkdir -p /dependencies /build-dependencies

# ========================================================================
# BOOST 1.75.0
# ========================================================================
ADD https://archives.boost.io/release/${BOOST_VERSION}/source/${BOOST_FILENAME}.tar.gz /tmp/

RUN cd /tmp && tar -xvf ${BOOST_FILENAME}.tar.gz && \
    cd ${BOOST_FILENAME} && \
    ./bootstrap.sh --with-libraries=filesystem,system \
       --prefix=/dependencies/boost/${BOOST_VERSION} && \
    ./b2 install link=static threading=multi \
       cxxflags="-fvisibility=hidden -fPIC" \
       cflags="-fvisibility=hidden -fPIC" && \
    rm -rf /tmp/${BOOST_FILENAME}*

# ========================================================================
# APR
# ========================================================================
ADD https://archive.apache.org/dist/apr/apr-${APR_VERSION}.tar.gz /tmp/

RUN cd /tmp && tar -xf apr-${APR_VERSION}.tar.gz && \
    cd apr-${APR_VERSION} && \
    ./configure --prefix=/dependencies/apr/${APR_VERSION} \
        --enable-static=yes --enable-shared=no --with-pic && \
    make -j$(nproc) && make install && \
    rm -rf /tmp/apr-${APR_VERSION}*

# ========================================================================
# EXPAT
# ========================================================================
ADD https://github.com/libexpat/libexpat/releases/download/${EXPAT_RVERSION}/expat-${EXPAT_VERSION}.tar.gz /tmp/

RUN cd /tmp && tar -xf expat-${EXPAT_VERSION}.tar.gz && \
    cd expat-${EXPAT_VERSION} && \
    ./configure --prefix=/dependencies/expat/${EXPAT_VERSION} \
        --enable-static=yes --enable-shared=no --with-pic && \
    make -j$(nproc) && make install && \
    rm -rf /tmp/expat-${EXPAT_VERSION}*

# ========================================================================
# APR-util
# ========================================================================
ADD https://archive.apache.org/dist/apr/apr-util-${APRUTIL_VERSION}.tar.gz /tmp/

RUN cd /tmp && tar -xf apr-util-${APRUTIL_VERSION}.tar.gz && \
    cd apr-util-${APRUTIL_VERSION} && \
    ./configure \
        --prefix=/dependencies/apr-util/${APRUTIL_VERSION} \
        --enable-static=yes --enable-shared=no --with-pic \
        --with-apr=/dependencies/apr/${APR_VERSION} \
        --with-expat=/dependencies/expat/${EXPAT_VERSION} && \
    make -j$(nproc) && make install && \
    rm -rf /tmp/apr-util-${APRUTIL_VERSION}*

# ========================================================================
# LOG4CXX (FIXED BUILD: autoreconf first)
# ========================================================================
ADD https://archive.apache.org/dist/logging/log4cxx/${LOG4CXX_VERSION}/apache-log4cxx-${LOG4CXX_VERSION}.tar.gz /tmp/

RUN cd /tmp && \
    tar -xf apache-log4cxx-${LOG4CXX_VERSION}.tar.gz && \
    cd apache-log4cxx-${LOG4CXX_VERSION} && \
    autoreconf -fi && \
    ./configure \
        --prefix=/dependencies/apache-log4cxx/${LOG4CXX_VERSION} \
        --enable-static=yes \
        --enable-shared=no \
        --with-pic \
        --with-apr=/dependencies/apr/${APR_VERSION} \
        --with-apr-util=/dependencies/apr-util/${APRUTIL_VERSION} && \
    make -j$(nproc) && \
    make install && \
    cd /tmp && rm -rf apache-log4cxx-${LOG4CXX_VERSION}*

# ========================================================================
# OpenTelemetry C++ SDK (Correct include copy — no double nesting)
# ========================================================================
RUN git clone --depth=1 --branch v${OPENTELEMETRY_VERSION} https://github.com/open-telemetry/opentelemetry-cpp /tmp/opentelemetry-cpp && \
    cd /tmp/opentelemetry-cpp && git submodule update --init --recursive && \
    mkdir build && cd build && \
    cmake .. \
      -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
      -DBUILD_TESTING=OFF \
      -DBUILD_SHARED_LIBS=ON \
      -DWITH_OTLP=ON \
      -DWITH_OTLP_GRPC=ON \
      -DWITH_OTLP_HTTP=ON \
      -DProtobuf_PROTOC_EXECUTABLE=/usr/bin/protoc \
      -DCMAKE_INSTALL_PREFIX=/dependencies/opentelemetry/${OPENTELEMETRY_VERSION} && \
    make -j$(nproc) && make install && cd .. && \
    mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include && \
    cp -r api/include/* /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/ && \
    cp -r sdk/include/* /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/ && \
    cp -r exporters/include/* /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/ && \
    cp -r ext/include/* /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/ || true && \
    rm -rf /tmp/opentelemetry-cpp

# ========================================================================
# Download NGINX source
# ========================================================================
ADD http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz /tmp/

RUN tar -xvf /tmp/nginx-${NGINX_VERSION}.tar.gz -C /build-dependencies && \
    rm -rf /tmp/nginx-${NGINX_VERSION}.tar.gz

# ========================================================================
# Build WebServer Module (Gradle)
# ========================================================================
COPY . /otel-webserver-module

RUN cp -r /dependencies /otel-webserver-module/ && \
    cp -r /build-dependencies /otel-webserver-module/ && \
    cd /otel-webserver-module && ./gradlew assembleWebServerModule

# ========================================================================
# Install Nginx and OpenTelemetry Module
# ========================================================================
RUN echo "[nginx]" > /etc/yum.repos.d/nginx.repo && \
    echo "name=nginx repo" >> /etc/yum.repos.d/nginx.repo && \
    echo "baseurl=https://nginx.org/packages/mainline/centos/9/x86_64/" >> /etc/yum.repos.d/nginx.repo && \
    echo "gpgcheck=1" >> /etc/yum.repos.d/nginx.repo && \
    echo "enabled=1" >> /etc/yum.repos.d/nginx.repo && \
    rpm --import https://nginx.org/keys/nginx_signing.key && \
    wget https://nginx.org/packages/mainline/centos/9/x86_64/RPMS/nginx-${NGINX_VERSION}-1.el9.ngx.x86_64.rpm && \
    dnf install -y ./nginx-${NGINX_VERSION}-1.el9.ngx.x86_64.rpm && \
    rm nginx-${NGINX_VERSION}-1.el9.ngx.x86_64.rpm && dnf clean all

RUN cd /otel-webserver-module/build && \
    tar -xf opentelemetry-webserver-sdk-x64-linux.tgz && \
    mv opentelemetry-webserver-sdk /opt/ && \
    cp /otel-webserver-module/conf/nginx/opentelemetry_module.conf /opt/ && \
    sed -i "8i load_module /opt/opentelemetry-webserver-sdk/WebServerModule/Nginx/${NGINX_VERSION}/ngx_http_opentelemetry_module.so;" /etc/nginx/nginx.conf && \
    sed -i "33i include /opt/opentelemetry_module.conf;" /etc/nginx/nginx.conf

# ========================================================================
# Cleanup
# ========================================================================
RUN rm -rf /var/cache/dnf/* /tmp/*

COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]
