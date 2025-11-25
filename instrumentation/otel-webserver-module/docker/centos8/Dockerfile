# ========================================================================
# Base: CentOS Stream 9 + GCC 13 + glibc 2.34
# ========================================================================
FROM quay.io/centos/centos:stream9

ARG BUILD_NUMBER
LABEL NAME="apm/build-image-nginx-otel-centos9-x64" VERSION=$BUILD_NUMBER

# ------------------------------------------------------------------------
# Environment
# ------------------------------------------------------------------------
ENV LANG=C.UTF-8
ENV PATH="/opt/rh/gcc-toolset-13/root/usr/bin:${PATH}"

ARG NGINX_VERSION="1.29.3"
ARG OPENTELEMETRY_VERSION="1.23.0"
ARG BOOST_VERSION="1.75.0"
ARG BOOST_FILENAME="boost_1_75_0"
ARG PYTHON_VERSION="2.7.18"

# ------------------------------------------------------------------------
# Install system tools & build chain
# ------------------------------------------------------------------------
RUN dnf -y update && \
    dnf install -y \
        gcc-toolset-13 git make wget tar xz unzip which cmake3 \
        zlib-devel openssl-devel pcre-devel bzip2-devel \
        java-17-openjdk java-17-openjdk-devel \
        perl m4 autoconf automake libtool && \
    dnf clean all


# ------------------------------------------------------------------------
# Build Python 2.7 from source (for GYP)
# ------------------------------------------------------------------------
RUN mkdir /tmp/python2 && cd /tmp/python2 && \
    wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz && \
    tar -xf Python-${PYTHON_VERSION}.tar.xz && cd Python-${PYTHON_VERSION} && \
    ./configure --prefix=/usr/local --enable-optimizations && \
    make -j$(nproc) && make altinstall && \
    ln -sf /usr/local/bin/python2.7 /usr/bin/python && \
    python --version && \
    cd / && rm -rf /tmp/python2

# ------------------------------------------------------------------------
# Build dependency directories
# ------------------------------------------------------------------------
RUN mkdir -p /dependencies /build-dependencies

# ------------------------------------------------------------------------
# Install Boost (1.75.0)
# ------------------------------------------------------------------------
RUN wget https://archives.boost.io/release/${BOOST_VERSION}/source/${BOOST_FILENAME}.tar.gz && \
    tar -xvf ${BOOST_FILENAME}.tar.gz && \
    cd ${BOOST_FILENAME} && \
    ./bootstrap.sh --with-libraries=filesystem,system --prefix=/dependencies/boost/${BOOST_VERSION} && \
    ./b2 install define=BOOST_ERROR_CODE_HEADER_ONLY link=static threading=multi \
        cxxflags="-fvisibility=hidden -fPIC" cflags="-fvisibility=hidden -fPIC" && \
    cd .. && rm -rf ${BOOST_FILENAME}*

# ------------------------------------------------------------------------
# Install OpenTelemetry C++ (v1.23.0)
# ------------------------------------------------------------------------
RUN mkdir -p dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/{lib,include} && \
    git clone https://github.com/open-telemetry/opentelemetry-cpp && \
    cd opentelemetry-cpp && \
    git checkout tags/v${OPENTELEMETRY_VERSION} -b v${OPENTELEMETRY_VERSION} && \
    git submodule update --init --recursive && \
    mkdir build && cd build && \
    cmake .. \
        -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
        -DBUILD_TESTING=OFF \
        -DBUILD_SHARED_LIBS=ON \
        -DWITH_OTLP=ON \
        -DCMAKE_INSTALL_PREFIX=/dependencies/opentelemetry/${OPENTELEMETRY_VERSION} && \
    cmake --build . --target all -j$(nproc) && \
    cd .. && \
    find . -name "*.so" -type f -exec cp {} /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/ \; && \
    if [ -f build/libopentelemetry_proto.a ]; then \
         cp build/libopentelemetry_proto.a /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/; \
     else \
         echo "⚠️  libopentelemetry_proto.a not found — continuing"; \
     fi && \
    cp -r api/include/ /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/ && \
    for dir in exporters/*; do \
        if [ -d "$dir/include" ]; then \
            cp -rf "$dir/include" /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/; \
        fi; \
    done && \
    cp -r sdk/include/ /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/ && \
    mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry/proto && \
    cp -r build/generated/third_party/opentelemetry-proto/opentelemetry/proto/ \
        /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry/ || true && \
    cd .. && rm -rf opentelemetry-cpp

# ------------------------------------------------------------------------
# Download Nginx sources (for header inclusion during build)
# ------------------------------------------------------------------------
RUN wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz && \
    tar -xvf nginx-${NGINX_VERSION}.tar.gz -C /build-dependencies && \
    rm -f nginx-${NGINX_VERSION}.tar.gz

# ------------------------------------------------------------------------
# Build OTel module with Gradle
# ------------------------------------------------------------------------
COPY . /otel-webserver-module
RUN cp -r /dependencies /otel-webserver-module/ && \
    cp -r /build-dependencies /otel-webserver-module/ && \
    cd /otel-webserver-module && ./gradlew assembleWebServerModule

# ------------------------------------------------------------------------
# Install Nginx 1.29.3 (binary)
# ------------------------------------------------------------------------
RUN echo "[nginx]" > /etc/yum.repos.d/nginx.repo && \
    echo "name=nginx repo" >> /etc/yum.repos.d/nginx.repo && \
    echo "baseurl=https://nginx.org/packages/mainline/centos/9/x86_64/" >> /etc/yum.repos.d/nginx.repo && \
    echo "gpgcheck=1" >> /etc/yum.repos.d/nginx.repo && \
    echo "enabled=1" >> /etc/yum.repos.d/nginx.repo && \
    rpm --import https://nginx.org/keys/nginx_signing.key && \
    wget https://nginx.org/packages/mainline/centos/9/x86_64/RPMS/nginx-${NGINX_VERSION}-1.el9.ngx.x86_64.rpm && \
    dnf install -y ./nginx-${NGINX_VERSION}-1.el9.ngx.x86_64.rpm && \
    rm -f nginx-${NGINX_VERSION}-1.el9.ngx.x86_64.rpm && \
    dnf clean all

# ------------------------------------------------------------------------
# Configure Nginx with OpenTelemetry module
# ------------------------------------------------------------------------
RUN cd /otel-webserver-module/build && \
    tar -xf opentelemetry-webserver-sdk-x64-linux.tgz && \
    mv -f opentelemetry-webserver-sdk /opt/ && \
    cd / && \
    cp /otel-webserver-module/conf/nginx/opentelemetry_module.conf /opt/ && \
    sed -i "8i load_module /opt/opentelemetry-webserver-sdk/WebServerModule/Nginx/${NGINX_VERSION}/ngx_http_opentelemetry_module.so;" /etc/nginx/nginx.conf && \
    sed -i "33i include /opt/opentelemetry_module.conf;" /etc/nginx/nginx.conf

# ------------------------------------------------------------------------
# Clean up build artifacts
# ------------------------------------------------------------------------
RUN rm -rf /grpc /cmake-* /autoconf-* /automake-* /libtool-* /Python-* \
    && rm -rf /var/cache/dnf/* /tmp/*

COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]
