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
ARG GRPC_VERSION="1.57.0"
ARG LOG4CXX_VERSION="0.11.0"
ARG APR_VERSION="1.7.0"
ARG EXPAT_VERSION="2.3.0"
ARG EXPAT_RVERSION="R_2_3_0"
ARG LIBTOOL_VERSION="2.4.6"
ARG APRUTIL_VERSION="1.6.1"
ARG BOOST_FILENAME="boost_1_75_0"
ARG PYTHON_VERSION="2.7.8"

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
# Build Python 2.7 (for GYP)
# ------------------------------------------------------------------------
RUN wget http://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz \
    && unxz Python-${PYTHON_VERSION}.tar.xz \
    && tar -xf Python-${PYTHON_VERSION}.tar \
    && cd Python-${PYTHON_VERSION} && ./configure --prefix=/usr/local && make && make install \
    && cd .. && rm -rf Python-${PYTHON_VERSION}.tar Python-${PYTHON_VERSION}.tar.xz

# ------------------------------------------------------------------------
# Directory prep
# ------------------------------------------------------------------------
RUN mkdir -p dependencies

# ------------------------------------------------------------------------
# Install Boost
# ------------------------------------------------------------------------
RUN wget https://archives.boost.io/release/${BOOST_VERSION}/source/${BOOST_FILENAME}.tar.gz && \
    tar -xvf ${BOOST_FILENAME}.tar.gz && \
    cd ${BOOST_FILENAME} && \
    ./bootstrap.sh --with-libraries=filesystem,system --prefix=/dependencies/boost/${BOOST_VERSION} && \
    ./b2 install define=BOOST_ERROR_CODE_HEADER_ONLY link=static threading=multi \
        cxxflags="-fvisibility=hidden -fPIC" cflags="-fvisibility=hidden -fPIC" && \
    cd .. && rm -rf ${BOOST_FILENAME}*

# ------------------------------------------------------------------------
# Build gRPC from source
# ------------------------------------------------------------------------
# RUN git clone https://github.com/grpc/grpc \
#   && cd grpc \
#   && git checkout tags/v${GRPC_VERSION} -b v${GRPC_VERSION} \
#   && git submodule update --init \
#   && sed -i "s/target_link_libraries(bssl ssl crypto)/target_link_libraries(bssl ssl crypto rt)/g" third_party/boringssl-with-bazel/CMakeLists.txt \
#   && mkdir -p cmake/build \
#   && cd cmake/build \
#   && cmake ../.. -DgRPC_INSTALL=ON -DCMAKE_BUILD_TYPE=Release \
#         -DgRPC_ABSL_PROVIDER=module -DgRPC_CARES_PROVIDER=module \
#         -DgRPC_PROTOBUF_PROVIDER=module -DgRPC_RE2_PROVIDER=module \
#         -DgRPC_SSL_PROVIDER=module -DgRPC_ZLIB_PROVIDER=module \
#   && make -j$(nproc) && make install \
#   && cd ../../.. && rm -rf grpc

RUN dnf install -y epel-release epel-next-release && \
    dnf config-manager --set-enabled crb && \
    dnf makecache && \
    dnf install -y \
        grpc grpc-devel \
        protobuf protobuf-devel \
        abseil-cpp abseil-cpp-devel \
        re2 re2-devel \
        c-ares c-ares-devel \
        zlib zlib-devel openssl openssl-devel && \
    dnf clean all

# ------------------------------------------------------------------------
# APR, expat, APR-util
# ------------------------------------------------------------------------
RUN mkdir -p dependencies/apr/${APR_VERSION} \
    && wget https://archive.apache.org/dist/apr/apr-${APR_VERSION}.tar.gz --no-check-certificate \
    && tar -xf apr-${APR_VERSION}.tar.gz \
    && cd apr-${APR_VERSION} \
    && ./configure --prefix=/dependencies/apr/${APR_VERSION} --enable-static=yes --enable-shared=no --with-pic \
    && make -j$(nproc) && make install \
    && cd .. && rm -rf apr-${APR_VERSION}*

RUN mkdir -p dependencies/expat/${EXPAT_VERSION} \
    && wget https://github.com/libexpat/libexpat/releases/download/${EXPAT_RVERSION}/expat-${EXPAT_VERSION}.tar.gz --no-check-certificate \
    && tar -xf expat-${EXPAT_VERSION}.tar.gz \
    && cd expat-${EXPAT_VERSION} \
    && ./configure --prefix=/dependencies/expat/${EXPAT_VERSION} --enable-static=yes --enable-shared=no --with-pic \
    && make -j$(nproc) && make install \
    && cd .. && rm -rf expat-${EXPAT_VERSION}*

RUN mkdir -p dependencies/apr-util/${APRUTIL_VERSION} \
    && wget https://archive.apache.org/dist/apr/apr-util-${APRUTIL_VERSION}.tar.gz --no-check-certificate \
    && tar -xf apr-util-${APRUTIL_VERSION}.tar.gz \
    && cd apr-util-${APRUTIL_VERSION} \
    && ./configure --prefix=/dependencies/apr-util/${APRUTIL_VERSION} \
        --enable-static=yes --enable-shared=no --with-pic \
        --with-apr=/dependencies/apr/${APR_VERSION} \
        --with-expat=/dependencies/expat/${EXPAT_VERSION} \
    && make -j$(nproc) && make install \
    && cd .. && rm -rf apr-util-${APRUTIL_VERSION}*

RUN wget --no-check-certificate https://ftpmirror.gnu.org/libtool/libtool-${LIBTOOL_VERSION}.tar.gz \
    && tar xzf libtool-${LIBTOOL_VERSION}.tar.gz \
    && cd libtool-${LIBTOOL_VERSION} \
    && ./configure --prefix=/usr \
    && make -j 6 \
    && make install \
    && libtool --version \
    && cd .. && rm -rf libtool--${LIBTOOL_VERSION}.tar.gz


#install log4cxx
RUN mkdir -p dependencies/apache-log4cxx/${LOG4CXX_VERSION} \
    && wget https://archive.apache.org/dist/logging/log4cxx/${LOG4CXX_VERSION}/apache-log4cxx-${LOG4CXX_VERSION}.tar.gz --no-check-certificate \
    && tar -xf apache-log4cxx-${LOG4CXX_VERSION}.tar.gz \
    && cd apache-log4cxx-${LOG4CXX_VERSION} \
    && ./configure --prefix=/dependencies/apache-log4cxx/${LOG4CXX_VERSION}/ --enable-static=yes --enable-shared=no --with-pic --with-apr=/dependencies/apr/${APR_VERSION}/ --with-apr-util=/dependencies/apr-util/${APRUTIL_VERSION}/ && echo $? \
    && make -j 6 ; echo 0 \
    && automake --add-missing \
    && make install \
    && cd .. && rm -rf apache-log4cxx-${LOG4CXX_VERSION}.tar.gz && rm -rf apache-log4cxx-${LOG4CXX_VERSION}

# ------------------------------------------------------------------------
# Build OpenTelemetry C++ SDK
# ------------------------------------------------------------------------
RUN mkdir -p dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib \
    && mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include \
    && git clone https://github.com/open-telemetry/opentelemetry-cpp \
    && cd opentelemetry-cpp/ \
    && git checkout tags/v${OPENTELEMETRY_VERSION} -b v${OPENTELEMETRY_VERSION} \
    && git submodule update --init --recursive \
    && mkdir build \
    && cd build \
    && cmake .. \
        -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
        -DBUILD_TESTING=OFF \
        -DBUILD_SHARED_LIBS=ON \
        -DWITH_OTLP=ON \
        -DWITH_OTLP_GRPC=ON \
        -DWITH_OTLP_HTTP=ON \
        -DCMAKE_CXX_STANDARD=14 \
        -DCMAKE_CXX_STANDARD_REQUIRED=ON \
        -DCMAKE_PREFIX_PATH="/usr" \
        -DProtobuf_INCLUDE_DIR=/usr/include \
        -DgRPC_DIR=/usr/lib64/cmake/grpc \
        -Dabsl_DIR=/usr/lib64/cmake/absl \
        -DCMAKE_INSTALL_PREFIX=/dependencies/opentelemetry/${OPENTELEMETRY_VERSION} \
    && cmake --build . --target all -j$(nproc) \
    && cmake --install . \
    && cd .. \
    && find . -name "*.so" -type f -exec cp {} /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/ \; \
    && cp -r build/* /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib \
    && cp -r api/include/ /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/ \
    && for dir in exporters/*; do if [ -d "$dir" ]; then cp -rf "$dir/include" /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/; fi; done \
    && cp -r sdk/include/ /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/ \
    && cp -r ext/include/ /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/ || true \
    && cp -r build/generated/third_party/opentelemetry-proto/opentelemetry/proto/ /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry/ \
    && cd .. && rm -rf opentelemetry-cpp

# ------------------------------------------------------------------------
# Download Nginx source (needed by build)
# ------------------------------------------------------------------------
RUN mkdir build-dependencies \
    && wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz  \
    && tar -xvf nginx-${NGINX_VERSION}.tar.gz -C /build-dependencies  \
    && rm -f nginx-${NGINX_VERSION}.tar.gz



# ------------------------------------------------------------------------
# COPY CODE + CRITICAL FIX
# ------------------------------------------------------------------------
COPY . /otel-webserver-module
RUN cp -r /dependencies /otel-webserver-module/ \
    && cp -r /build-dependencies /otel-webserver-module/ \
    && cd otel-webserver-module \
    && ./gradlew assembleWebServerModule 

# ------------------------------------------------------------------------
# Install Nginx binary
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
# Configure Nginx to load module
# ------------------------------------------------------------------------
RUN cd /otel-webserver-module/build && \
    tar -xf opentelemetry-webserver-sdk-x64-linux.tgz && \
    mv -f opentelemetry-webserver-sdk /opt/ && \
    cd / && \
    cp /otel-webserver-module/conf/nginx/opentelemetry_module.conf /opt/ && \
    sed -i "8i load_module /opt/opentelemetry-webserver-sdk/WebServerModule/Nginx/${NGINX_VERSION}/ngx_http_opentelemetry_module.so;" /etc/nginx/nginx.conf && \
    sed -i "33i include /opt/opentelemetry_module.conf;" /etc/nginx/nginx.conf

COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]