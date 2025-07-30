FROM centos:6.9

ARG BUILD_NUMBER

LABEL NAME=apm/build-image-webserver-agent-centos6-x64 VERSION=$BUILD_NUMBER

ENV GOSU_ARCH amd64
ENV JDK_ARCH x64

ARG PYTHON_VERSION="2.7.8"
ARG CMAKE_VERSION="3.20"
ARG CMAKE_0VERSION="3.20.0"
ARG GRPC_VERSION="1.36.4"
ARG OPENTELEMETRY_VERSION="1.2.0"
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
ARG PCRE_VERSION="8.44"
ARG NGINX_VERSION="1.29.0"


# create default non-root user
RUN groupadd -r swuser && useradd -u 1000 -g swuser -m -s /sbin/nologin -c "default non-root user" swuser

RUN chmod -R 777 /opt

RUN curl https://www.getpagespeed.com/files/centos6-eol.repo --output /etc/yum.repos.d/CentOS-Base.repo

# install libtool
RUN wget --no-check-certificate https://ftp.gnu.org/gnu/libtool/libtool-${LIBTOOL_VERSION}.tar.gz \
    && tar xzf libtool-${LIBTOOL_VERSION}.tar.gz \
    && cd libtool-${LIBTOOL_VERSION} \
    && ./configure --prefix=/usr \
    && make -j 6 \
    && make install \
    && libtool --version \
    && cd .. && rm -rf libtool-${LIBTOOL_VERSION}.tar.gz