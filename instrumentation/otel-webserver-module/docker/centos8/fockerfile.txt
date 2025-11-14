FROM centos:8

ARG BUILD_NUMBER

LABEL NAME=apm/build-image-webserver-agent-centos6-x64 VERSION=$BUILD_NUMBER

ENV GOSU_ARCH amd64
ENV JDK_ARCH x64

ARG PYTHON_VERSION="2.7.8"
ARG CMAKE_VERSION="3.26"
ARG CMAKE_0VERSION="3.26.5"
ARG GRPC_VERSION="1.36.4"
ARG OPENTELEMETRY_VERSION="1.23.0"
ARG BOOST_VERSION="1.75.0"
ARG BOOST_FILENAME="boost_1_75_0"
ARG APR_VERSION="1.7.0"
ARG EXPAT_VERSION="2.3.0"
ARG EXPAT_RVERSION="R_2_3_0"
ARG APRUTIL_VERSION="1.6.1"
ARG AUTOCONF_VERSION="2.68"
ARG LIBTOOL_VERSION="2.4.6"
ARG LOG4CXX_VERSION="0.11.0"
ARG GTEST_VERSION="1.10.0"
ARG AUTOMAKE_VERSION="1.16.3"
ARG PERL_VERSION="5.20.2"
ARG PERL_CPANVERSION="5.0"
ARG PCRE_VERSION="8.44"
ARG NGINX_VERSION="1.29.3"

# create default non-root user
RUN groupadd -r swuser && useradd -u 1000 -g swuser -m -s /sbin/nologin -c "default non-root user" swuser

RUN chmod -R 777 /opt

# RUN curl https://www.getpagespeed.com/files/centos6-eol.repo --output /etc/yum.repos.d/CentOS-Base.repo

RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* && \
    sed -i 's|# *baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

# install required packages
RUN yum update -y \
    && yum install -y \
    yum  wget -y \
    yum  -y zlib-devel \
    yum  -y openssl-devel \
    yum  java-1.8.0-openjdk -y \
    yum  java-1.8.0-openjdk-devel \
    yum  pcre-devel -y \
    yum  xz -y \
    yum  httpd -y \
    && yum clean all

# install lcov package
RUN yum install -y epel-release && \
    yum install -y lcov && \
    yum clean all


# install devtoolset toolchain
RUN dnf install -y gcc-toolset-9 && \
    dnf clean all

ENV PATH="/opt/rh/gcc-toolset-9/root/usr/bin:${PATH}"
# install git required for grpc
RUN yum install git -y \
  && yum clean all
# install opentelemetry

# Install OpenTelemetry C++ SDK
RUN mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib \
    && mkdir -p /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include \
    && git clone https://github.com/open-telemetry/opentelemetry-cpp \
    && cd opentelemetry-cpp \
    && git checkout tags/v${OPENTELEMETRY_VERSION} -b v${OPENTELEMETRY_VERSION} \
    && git submodule update --init --recursive \
    && mkdir build \
    && cd build \
    && cmake .. \
        -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
        -DBUILD_TESTING=OFF \
        -DBUILD_SHARED_LIBS=ON \
        -DWITH_OTLP=ON \
        -DCMAKE_INSTALL_PREFIX=/dependencies/opentelemetry/${OPENTELEMETRY_VERSION} \
    && cmake --build . --target all \
    && cmake --install . \
    && cd .. \
    # Copy shared libraries (.so)
    && find build -name "*.so" -type f -exec cp {} /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/ \; \
    # Copy headers (already installed by cmake --install)
    && cp -r api/include/ /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/ \
    && for dir in exporters/*; do if [ -d "$dir" ]; then cp -rf "$dir/include" /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/; fi; done \
    && cp -r sdk/include/ /dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/ \
    && cd .. && rm -rf opentelemetry-cpp


# install googletest
RUN mkdir -p dependencies/googletest/${GTEST_VERSION}/ \
    && wget https://github.com/google/googletest/archive/refs/tags/release-${GTEST_VERSION}.tar.gz --no-check-certificate \
    && tar -xf release-${GTEST_VERSION}.tar.gz \
    && cd googletest-release-${GTEST_VERSION}/  \
    && mkdir build && cd build \
    && cmake .. -DCMAKE_INSTALL_PREFIX=/dependencies/googletest/${GTEST_VERSION}/ \
    && make \
    && make install \
    && cd ../.. && rm -rf release-${GTEST_VERSION}.tar.gz && rm -rf googletest-release-${GTEST_VERSION}/

# install pcre
RUN mkdir -p dependencies/pcre/${PCRE_VERSION}/ \
    && wget https://ftp.exim.org/pub/pcre/pcre-${PCRE_VERSION}.tar.gz --no-check-certificate \
    && tar -xvf pcre-${PCRE_VERSION}.tar.gz \
    && cd pcre-${PCRE_VERSION} \
    && ./configure --prefix=/dependencies/pcre/${PCRE_VERSION} --enable-jit \
    && make && make install \
    && cd .. && rm -rf ${PCRE_VERSION}.tar.gz && rm -rf pcre-${PCRE_VERSION}

#Installing Apache and apr source code
RUN mkdir build-dependencies \
    && wget --no-check-certificate https://archive.apache.org/dist/apr/apr-${APR_VERSION}.tar.gz \
    && tar -xf apr-${APR_VERSION}.tar.gz \
    && mv -f apr-${APR_VERSION} build-dependencies \
    && wget --no-check-certificate https://archive.apache.org/dist/apr/apr-util-${APRUTIL_VERSION}.tar.gz \
    && tar -xf apr-util-${APRUTIL_VERSION}.tar.gz \
    && mv -f apr-util-${APRUTIL_VERSION} build-dependencies \
    && wget --no-check-certificate http://archive.apache.org/dist/httpd/httpd-2.2.31.tar.gz \
    && tar -xf httpd-2.2.31.tar.gz \
    && mv -f httpd-2.2.31 build-dependencies \
    && wget --no-check-certificate http://archive.apache.org/dist/httpd/httpd-2.4.23.tar.gz \
    && tar -xf httpd-2.4.23.tar.gz \
    && mv -f httpd-2.4.23 build-dependencies

# install nginx
RUN wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz \
    && tar -xvf nginx-${NGINX_VERSION}.tar.gz -C /build-dependencies \
    && rm -rf nginx-${NGINX_VERSION}.tar.gz

# Build Webserver Module
COPY . /otel-webserver-module

RUN cp -r /dependencies /otel-webserver-module/ \
    && cp -r /build-dependencies /otel-webserver-module/ \
    && cd otel-webserver-module \
    && ./gradlew assembleWebServerModule 

# Add the Nginx repository
RUN echo "[nginx]" > /etc/yum.repos.d/nginx.repo && \
    echo "name=nginx repo" >> /etc/yum.repos.d/nginx.repo && \
    echo "baseurl=https://nginx.org/packages/mainline/centos/8/x86_64/" >> /etc/yum.repos.d/nginx.repo && \
    echo "gpgcheck=1" >> /etc/yum.repos.d/nginx.repo && \
    echo "enabled=1" >> /etc/yum.repos.d/nginx.repo && \
    rpm --import https://nginx.org/keys/nginx_signing.key

# Install necessary tools
RUN dnf install -y wget && dnf clean all

# Download and install Nginx 1.29.3 from the correct path
RUN wget https://nginx.org/packages/mainline/centos/8/x86_64/RPMS/nginx-1.29.3-1.el8.ngx.x86_64.rpm && \
    dnf install -y ./nginx-1.29.3-1.el8.ngx.x86_64.rpm && \
    rm -f nginx-1.29.3-1.el8.ngx.x86_64.rpm && \
    dnf clean all


RUN cd /otel-webserver-module/build \
    && tar -xf opentelemetry-webserver-sdk-x64-linux.tgz \
    && mv -f opentelemetry-webserver-sdk /opt/ \
    && cd ../ \
    && cp opentelemetry_module.conf /etc/httpd/conf/ \
    && sed -i "s/libmod_apache_otel22.so/libmod_apache_otel.so/g" /etc/httpd/conf/opentelemetry_module.conf \
    && echo 'Include conf/opentelemetry_module.conf' >> /etc/httpd/conf/httpd.conf \
    && cd /opt/opentelemetry-webserver-sdk \
    && ./install.sh \
    && cd /

RUN cp /otel-webserver-module/conf/nginx/opentelemetry_module.conf /opt/ \
    && sed -i '8i load_module /opt/opentelemetry-webserver-sdk/WebServerModule/Nginx/1.29.3/ngx_http_opentelemetry_module.so;' /etc/nginx/nginx.conf \
    && sed -i '33i include /opt/opentelemetry_module.conf;' /etc/nginx/nginx.conf \ 
    && cd /

# Remove unwanted files


COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]