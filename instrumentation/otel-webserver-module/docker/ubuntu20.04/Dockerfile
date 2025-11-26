FROM quay.io/centos/centos:stream9

ARG BUILD_NUMBER
LABEL NAME="apm/build-image-webserver-agent-centos9-x64" VERSION=$BUILD_NUMBER

# ------------------------------------------------------------------------
#  Base toolchain + dev utils
# ------------------------------------------------------------------------
RUN dnf -y update && \
    dnf install -y epel-release && \
    dnf install -y gcc-toolset-13 gcc-toolset-13-gcc-c++ git wget curl tar xz make cmake3 unzip which \
                   openssl-devel zlib-devel pcre-devel java-17-openjdk-devel perl m4 && \
    dnf clean all
ENV PATH="/opt/rh/gcc-toolset-13/root/usr/bin:${PATH}"

# ------------------------------------------------------------------------
#  Python 2.7 (for gyp)
# ------------------------------------------------------------------------
RUN dnf install -y python2 python2-libs python2-devel && ln -sf /usr/bin/python2 /usr/bin/python

# ------------------------------------------------------------------------
#  APR / Expat / APR-util
# ------------------------------------------------------------------------
ARG APR_VERSION=1.7.0
ARG APRUTIL_VERSION=1.6.1
ARG EXPAT_VERSION=2.3.0
ARG EXPAT_RVERSION=R_2_3_0

RUN mkdir -p /dependencies && cd /dependencies && \
    wget https://archive.apache.org/dist/apr/apr-${APR_VERSION}.tar.gz && \
    tar -xf apr-${APR_VERSION}.tar.gz && cd apr-${APR_VERSION} && \
    ./configure --prefix=/usr/local/apr --enable-static=yes --enable-shared=no --with-pic && make -j$(nproc) && make install && \
    cd .. && rm -rf apr-${APR_VERSION}*

RUN cd /dependencies && \
    wget https://github.com/libexpat/libexpat/releases/download/${EXPAT_RVERSION}/expat-${EXPAT_VERSION}.tar.gz && \
    tar -xf expat-${EXPAT_VERSION}.tar.gz && cd expat-${EXPAT_VERSION} && \
    ./configure --prefix=/usr/local/expat --enable-static=yes --enable-shared=no --with-pic && make -j$(nproc) && make install && \
    cd .. && rm -rf expat-${EXPAT_VERSION}*

RUN cd /dependencies && \
    wget https://archive.apache.org/dist/apr/apr-util-${APRUTIL_VERSION}.tar.gz && \
    tar -xf apr-util-${APRUTIL_VERSION}.tar.gz && cd apr-util-${APRUTIL_VERSION} && \
    ./configure --prefix=/usr/local/apr-util --enable-static=yes --enable-shared=no \
       --with-apr=/usr/local/apr --with-expat=/usr/local/expat --with-pic && \
    make -j$(nproc) && make install && cd .. && rm -rf apr-util-${APRUTIL_VERSION}*

# ------------------------------------------------------------------------
#  Log4cxx (static)
# ------------------------------------------------------------------------
ARG LOG4CXX_VERSION=0.11.0
RUN cd /dependencies && \
    wget https://archive.apache.org/dist/logging/log4cxx/${LOG4CXX_VERSION}/apache-log4cxx-${LOG4CXX_VERSION}.tar.gz && \
    tar -xf apache-log4cxx-${LOG4CXX_VERSION}.tar.gz && cd apache-log4cxx-${LOG4CXX_VERSION} && \
    ./configure --prefix=/usr/local/log4cxx --enable-static=yes --enable-shared=no \
        --with-apr=/usr/local/apr --with-apr-util=/usr/local/apr-util --with-pic && \
    make -j$(nproc) && make install && cd .. && rm -rf apache-log4cxx-${LOG4CXX_VERSION}*

# ------------------------------------------------------------------------
#  gRPC + protobuf (for OTel OTLP exporter)
# ------------------------------------------------------------------------
ARG GRPC_VERSION=1.62.0
RUN cd /dependencies && git clone -b v${GRPC_VERSION} --recurse-submodules --depth 1 https://github.com/grpc/grpc && \
    cd grpc && mkdir build && cd build && \
    cmake .. -DgRPC_INSTALL=ON -DgRPC_BUILD_TESTS=OFF -DCMAKE_INSTALL_PREFIX=/usr/local/grpc && \
    make -j$(nproc) && make install && cd / && rm -rf /dependencies/grpc

# ------------------------------------------------------------------------
#  OpenTelemetry C++ SDK 1.23.0
# ------------------------------------------------------------------------
ARG OPENTELEMETRY_VERSION=1.23.0
RUN mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/{lib,include} && \
    git clone --depth 1 --branch v${OPENTELEMETRY_VERSION} https://github.com/open-telemetry/opentelemetry-cpp.git && \
    cd opentelemetry-cpp && git submodule update --init --recursive && \
    mkdir build && cd build && \
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_SHARED_LIBS=ON \
        -DBUILD_TESTING=OFF \
        -DWITH_OTLP=ON \
        -DWITH_OTLP_GRPC=ON \
        -DWITH_OTLP_HTTP=ON \
        -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
        -DCMAKE_INSTALL_PREFIX=/usr/local/otel && \
    make -j$(nproc) && make install && \
    # Copy headers/libs for Gradle usage
    cp -r /usr/local/otel/include/opentelemetry /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/ && \
    cp -r /usr/local/otel/lib/* /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/ && \
    cd / && rm -rf opentelemetry-cpp

# ------------------------------------------------------------------------
#  Nginx 1.29.3
# ------------------------------------------------------------------------
ARG NGINX_VERSION=1.29.3
RUN wget https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz && \
    tar -xzf nginx-${NGINX_VERSION}.tar.gz && mv nginx-${NGINX_VERSION} /build-dependencies && \
    rm -f nginx-${NGINX_VERSION}.tar.gz

# ------------------------------------------------------------------------
#  Copy and build your OTel Webserver module
# ------------------------------------------------------------------------
WORKDIR /otel-webserver-module
COPY . /otel-webserver-module

RUN cp -r /dependencies /otel-webserver-module/ && \
    cp -r /build-dependencies /otel-webserver-module/ && \
    cd /otel-webserver-module && ./gradlew assembleWebServerModule --no-daemon

# ------------------------------------------------------------------------
#  Install Nginx runtime for verification (optional)
# ------------------------------------------------------------------------
RUN echo "[nginx]" > /etc/yum.repos.d/nginx.repo && \
    echo "name=nginx repo" >> /etc/yum.repos.d/nginx.repo && \
    echo "baseurl=https://nginx.org/packages/mainline/centos/9/x86_64/" >> /etc/yum.repos.d/nginx.repo && \
    echo "gpgcheck=1" >> /etc/yum.repos.d/nginx.repo && \
    echo "enabled=1" >> /etc/yum.repos.d/nginx.repo && \
    rpm --import https://nginx.org/keys/nginx_signing.key && \
    dnf install -y nginx && dnf clean all

ENTRYPOINT ["/bin/bash"]
