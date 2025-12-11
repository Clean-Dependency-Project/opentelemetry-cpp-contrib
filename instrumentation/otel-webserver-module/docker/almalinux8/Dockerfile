
# Base: Debian trixie (you said "texrie"; assuming trixie)
FROM debian:trixie-slim

ARG BUILD_NUMBER
LABEL NAME="apm/build-image-webserver-agent-debian-x64" VERSION=$BUILD_NUMBER

# ---- versions (kept from your file; you can update as needed) ----
ENV GOSU_ARCH=amd64
ENV JDK_ARCH=x64

ARG PYTHON_VERSION="2.7.18"
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
ARG PERL_VERSION="5.20.2"
ARG PERL_CPANVERSION="5.0"
ARG PCRE_VERSION="8.44"
# IMPORTANT: match SDK module directory (your conf loads 1.26.2)
ARG NGINX_VERSION="1.26.2"

# ---- create default non-root user; keep /opt writable for SDK ----
RUN groupadd -r swuser && useradd -u 1000 -g swuser -m -s /sbin/nologin -c "default non-root user" swuser \
 && chmod -R 777 /opt

# ---- apt packages (Debian equivalents of your dnf list) ----
ENV DEBIAN_FRONTEND=noninteractive
RUN set -eux; \
  apt-get update; \
  apt-get install -y --no-install-recommends \
    ca-certificates wget curl git \
    build-essential pkg-config \
    bzip2 xz-utils \
    libssl-dev libffi-dev zlib1g-dev \
    libpcre3-dev \
    # Java (Debian ships newer OpenJDK; 17 works for Gradle)
    openjdk-17-jdk \
    # Apache (Debian: apache2). If not needed, you can remove it.
    apache2 \
  ; \
  rm -rf /var/lib/apt/lists/*

# ---- Python 2.7.18 (from source, as in your original) ----
RUN set -eux; \
  wget "http://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz"; \
  unxz "Python-${PYTHON_VERSION}.tar.xz"; \
  tar -xf "Python-${PYTHON_VERSION}.tar"; \
  cd "Python-${PYTHON_VERSION}" && ./configure --prefix=/usr/local && make -j"$(nproc)" && make install; \
  cd .. && rm -rf "Python-${PYTHON_VERSION}.tar" "Python-${PYTHON_VERSION}"

# ---- gosu ----
ENV GOSU_VERSION=1.10
RUN curl -o /usr/bin/gosu -SL "https://github.com/tianon/gosu/releases/download/${GOSU_VERSION}/gosu-amd64" \
 && chmod +x /usr/bin/gosu \
 && gosu nobody true

# ---- CMake 3.20 (tarball install), as in your original ----
RUN set -eux; \
  wget "https://cmake.org/files/v${CMAKE_VERSION}/cmake-${CMAKE_0VERSION}-linux-x86_64.tar.gz"; \
  tar -xvf "cmake-${CMAKE_0VERSION}-linux-x86_64.tar.gz"; \
  cd "cmake-${CMAKE_0VERSION}-linux-x86_64" && cp -rf * /usr/local/; \
  cd .. && rm -rf "cmake-${CMAKE_0VERSION}-linux-x86_64.tar.gz" "cmake-${CMAKE_0VERSION}-linux-x86_64"

# ---- gRPC build (vendored deps) + Abseil patch for glibc 2.34+ ----
RUN set -eux; \
  git clone https://github.com/grpc/grpc; \
  cd grpc; \
  git checkout "tags/v${GRPC_VERSION}" -b "v${GRPC_VERSION}"; \
  git submodule update --init; \
  # BoringSSL tweak (your original change)
  sed -i 's/target_link_libraries(bssl ssl crypto)/target_link_libraries(bssl ssl crypto rt)/' \
      third_party/boringssl-with-bazel/CMakeLists.txt; \
  # Abseil failure_signal_handler fix for glibc >= 2.34 (SIGSTKSZ is long via sysconf)
  sed -E -i \
    's/std::max[[:space:]]*\([[:space:]]*SIGSTKSZ[[:space:]]*,[[:space:]]*65536[[:space:]]*\)/std::max<size_t>(static_cast<size_t>(SIGSTKSZ), size_t{65536})/' \
    third_party/abseil-cpp/absl/debugging/failure_signal_handler.cc; \
  mkdir -p cmake/build; \
  cd cmake/build; \
  cmake ../.. \
    -DgRPC_INSTALL=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DgRPC_ABSL_PROVIDER=module \
    -DgRPC_CARES_PROVIDER=module \
    -DgRPC_PROTOBUF_PROVIDER=module \
    -DgRPC_RE2_PROVIDER=module \
    -DgRPC_SSL_PROVIDER=module \
    -DgRPC_ZLIB_PROVIDER=module; \
  make -j"$(nproc)" && make install; \
  cd ../../..

# ---- dependencies folder (as before) ----
RUN mkdir -p dependencies

# ---- Boost 1.75.0 (final release tarball; no RC; cleanup) ----
RUN set -eux; \
  wget "https://archives.boost.io/release/${BOOST_VERSION}/source/${BOOST_FILENAME}.tar.gz"; \
  tar -xvf "${BOOST_FILENAME}.tar.gz"; \
  cd "${BOOST_FILENAME}"; \
  ./bootstrap.sh --with-libraries=filesystem,system --prefix="/dependencies/boost/${BOOST_VERSION}/"; \
  ./b2 install define=BOOST_ERROR_CODE_HEADER_ONLY link=static threading=multi \
      cxxflags="-fvisibility=hidden -fPIC" cflags="-fvisibility=hidden -fPIC"; \
  cd .. && rm -rf "${BOOST_FILENAME}" "${BOOST_FILENAME}.tar.gz"

# ---- APR ----
RUN set -eux; \
  mkdir -p "dependencies/apr/${APR_VERSION}"; \
  wget "https://archive.apache.org/dist/apr/apr-${APR_VERSION}.tar.gz" --no-check-certificate; \
  tar -xf "apr-${APR_VERSION}.tar.gz"; \
  cd "apr-${APR_VERSION}"; \
  ./configure --prefix="/dependencies/apr/${APR_VERSION}" --enable-static=yes --enable-shared=no --with-pic; \
  make -j"$(nproc)" && make install; \
  cd .. && rm -rf "apr-${APR_VERSION}" "apr-${APR_VERSION}.tar.gz"

# ---- Expat ----
RUN set -eux; \
  mkdir -p "dependencies/expat/${EXPAT_VERSION}"; \
  wget "https://github.com/libexpat/libexpat/releases/download/${EXPAT_RVERSION}/expat-${EXPAT_VERSION}.tar.gz" --no-check-certificate; \
  tar -xf "expat-${EXPAT_VERSION}.tar.gz"; \
  cd "expat-${EXPAT_VERSION}"; \
  ./configure --prefix="/dependencies/expat/${EXPAT_VERSION}" --enable-static=yes --enable-shared=no --with-pic; \
  make -j"$(nproc)" && make install; \
  cd .. && rm -rf "expat-${EXPAT_VERSION}" "expat-${EXPAT_VERSION}.tar.gz"

# ---- APR-util ----
RUN set -eux; \
  mkdir -p "dependencies/apr-util/${APRUTIL_VERSION}"; \
  wget "https://archive.apache.org/dist/apr/apr-util-${APRUTIL_VERSION}.tar.gz" --no-check-certificate; \
  tar -xf "apr-util-${APRUTIL_VERSION}.tar.gz"; \
  cd "apr-util-${APRUTIL_VERSION}"; \
  ./configure --prefix="/dependencies/apr-util/${APRUTIL_VERSION}" --enable-static=yes --enable-shared=no --with-pic \
              --with-apr="/dependencies/apr/${APR_VERSION}" --with-expat="/dependencies/expat/${EXPAT_VERSION}"; \
  make -j"$(nproc)" && make install; \
  cd .. && rm -rf "apr-util-${APRUTIL_VERSION}" "apr-util-${APRUTIL_VERSION}.tar.gz"

# ---- autoconf ----
RUN set -eux; \
  wget --no-check-certificate "https://ftp.gnu.org/gnu/autoconf/autoconf-${AUTOCONF_VERSION}.tar.gz"; \
  tar xzf "autoconf-${AUTOCONF_VERSION}.tar.gz"; \
  cd "autoconf-${AUTOCONF_VERSION}" && ./configure --prefix=/usr && make -j"$(nproc)" && make install && autoconf -V; \
  cd .. && rm -rf "autoconf-${AUTOCONF_VERSION}.tar.gz" "autoconf-${AUTOCONF_VERSION}"

# ---- automake ----
RUN set -eux; \
  wget --no-check-certificate "https://ftp.gnu.org/gnu/automake/automake-${AUTOMAKE_VERSION}.tar.gz"; \
  tar xzf "automake-${AUTOMAKE_VERSION}.tar.gz"; \
  cd "automake-${AUTOMAKE_VERSION}" && ./configure --prefix=/usr --libdir=/usr/lib64; \
  make -j"$(nproc)" && make install && automake --version; \
  cd .. && rm -rf "automake-${AUTOMAKE_VERSION}.tar.gz" "automake-${AUTOMAKE_VERSION}"

# ---- libtool ----
RUN set -eux; \
  wget --no-check-certificate "https://ftpmirror.gnu.org/libtool/libtool-${LIBTOOL_VERSION}.tar.gz"; \
  tar xzf "libtool-${LIBTOOL_VERSION}.tar.gz"; \
  cd "libtool-${LIBTOOL_VERSION}" && ./configure --prefix=/usr; \
  make -j"$(nproc)" && make install && libtool --version; \
  cd .. && rm -rf "libtool--${LIBTOOL_VERSION}.tar.gz" "libtool-${LIBTOOL_VERSION}"

# ---- log4cxx ----
RUN set -eux; \
  mkdir -p "dependencies/apache-log4cxx/${LOG4CXX_VERSION}"; \
  wget "https://archive.apache.org/dist/logging/log4cxx/${LOG4CXX_VERSION}/apache-log4cxx-${LOG4CXX_VERSION}.tar.gz" --no-check-certificate; \
  tar -xf "apache-log4cxx-${LOG4CXX_VERSION}.tar.gz"; \
  cd "apache-log4cxx-${LOG4CXX_VERSION}"; \
  ./configure --prefix="/dependencies/apache-log4cxx/${LOG4CXX_VERSION}/" --enable-static=yes --enable-shared=no --with-pic \
              --with-apr="/dependencies/apr/${APR_VERSION}/" --with-apr-util="/dependencies/apr-util/${APRUTIL_VERSION}/"; \
  make -j"$(nproc)" || true; \
  automake --add-missing || true; \
  make install; \
  cd .. && rm -rf "apache-log4cxx-${LOG4CXX_VERSION}.tar.gz" "apache-log4cxx-${LOG4CXX_VERSION}"

# ---- OpenTelemetry C++ ----
RUN set -eux; \
  mkdir -p "dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib"; \
  mkdir -p "dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include"; \
  git clone https://github.com/open-telemetry/opentelemetry-cpp; \
  cd opentelemetry-cpp; \
  git checkout "tags/v${OPENTELEMETRY_VERSION}" -b "v${OPENTELEMETRY_VERSION}"; \
  git submodule update --init --recursive; \
  mkdir build && cd build; \
  cmake .. -DCMAKE_POSITION_INDEPENDENT_CODE=ON -DBUILD_TESTING=OFF -DBUILD_SHARED_LIBS=ON -DWITH_OTLP=ON \
           -DCMAKE_INSTALL_PREFIX="/dependencies/opentelemetry/${OPENTELEMETRY_VERSION}"; \
  cmake --build . --target all; \
  cd ..; \
  find . -name "*.so" -type f -exec cp {} "/dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib/" \;; \
  cp build/libopentelemetry_proto.a "/dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/lib"; \
  cp -r api/include/ "/dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/"; \
  for dir in exporters/*; do if [ -d "$dir" ]; then cp -rf "$dir/include" "/dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/"; fi; done; \
  cp -r sdk/include/ "/dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/"; \
  mkdir -p "/dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry"; \
  cp -r build/generated/third_party/opentelemetry-proto/opentelemetry/proto/ \
        "/dependencies/opentelemetry/${OPENTELEMETRY_VERSION}/include/opentelemetry/"; \
  cd .. && rm -rf opentelemetry-cpp

# ---- Googletest ----
RUN set -eux; \
  mkdir -p "dependencies/googletest/${GTEST_VERSION}/"; \
  wget "https://github.com/google/googletest/archive/refs/tags/release-${GTEST_VERSION}.tar.gz" --no-check-certificate; \
  tar -xf "release-${GTEST_VERSION}.tar.gz"; \
  cd "googletest-release-${GTEST_VERSION}"; \
  mkdir build && cd build; \
  cmake .. -DCMAKE_INSTALL_PREFIX="/dependencies/googletest/${GTEST_VERSION}/"; \
  make -j"$(nproc)" && make install; \
  cd ../.. && rm -rf "release-${GTEST_VERSION}.tar.gz" "googletest-release-${GTEST_VERSION}"

# ---- PCRE (if you must build it; Debian already has libpcre3-dev) ----
RUN set -eux; \
  mkdir -p "dependencies/pcre/${PCRE_VERSION}/"; \
  wget "https://ftp.exim.org/pub/pcre/pcre-${PCRE_VERSION}.tar.gz" --no-check-certificate; \
  tar -xvf "pcre-${PCRE_VERSION}.tar.gz"; \
  cd "pcre-${PCRE_VERSION}"; \
  ./configure --prefix="/dependencies/pcre/${PCRE_VERSION}" --enable-jit; \
  make -j"$(nproc)" && make install; \
  cd .. && rm -rf "${PCRE_VERSION}.tar.gz" "pcre-${PCRE_VERSION}"

# ---- Build dependencies (Apache + NGINX sources), as in original ----
RUN set -eux; \
  mkdir build-dependencies; \
  wget --no-check-certificate "https://archive.apache.org/dist/apr/apr-${APR_VERSION}.tar.gz"; \
  tar -xf "apr-${APR_VERSION}.tar.gz" && mv -f "apr-${APR_VERSION}" build-dependencies; \
  wget --no-check-certificate "https://archive.apache.org/dist/apr/apr-util-${APRUTIL_VERSION}.tar.gz"; \
  tar -xf "apr-util-${APRUTIL_VERSION}.tar.gz" && mv -f "apr-util-${APRUTIL_VERSION}" build-dependencies; \
  wget --no-check-certificate "http://archive.apache.org/dist/httpd/httpd-2.2.31.tar.gz"; \
  tar -xf "httpd-2.2.31.tar.gz" && mv -f "httpd-2.2.31" build-dependencies; \
  wget --no-check-certificate "http://archive.apache.org/dist/httpd/httpd-2.4.23.tar.gz"; \
  tar -xf "httpd-2.4.23.tar.gz" && mv -f "httpd-2.4.23" build-dependencies

# ---- NGINX source (MATCH VERSION for module ABI) ----
RUN set -eux; \
  wget "http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz"; \
  tar -xvf "nginx-${NGINX_VERSION}.tar.gz" -C /build-dependencies; \
  rm -rf "nginx-${NGINX_VERSION}.tar.gz"

# ---- Build Webserver Module (gradle) ----
COPY . /otel-webserver-module
RUN set -eux; \
  cp -r /dependencies /otel-webserver-module/; \
  cp -r /build-dependencies /otel-webserver-module/; \
  cd /otel-webserver-module; \
  ./gradlew assembleWebServerModule

# ---- Install NGINX from source with Debian-like paths ----
# Use --with-compat so third-party dynamic modules are loadable; install to system dirs.
RUN set -eux; \
  cd "/build-dependencies/nginx-${NGINX_VERSION}"; \
  ./configure \
    --prefix=/etc/nginx \
    --conf-path=/etc/nginx/nginx.conf \
    --sbin-path=/usr/sbin/nginx \
    --modules-path=/etc/nginx/modules \
    --with-compat \
    --with-threads \
    --with-http_ssl_module \
    --with-http_v2_module \
    --with-pcre-jit; \
  make -j"$(nproc)" && make install

# ---- Deploy SDK & configure Apache/Nginx ----
RUN set -eux; \
  cd /otel-webserver-module/build; \
  tar -xf opentelemetry-webserver-sdk-x64-linux.tgz; \
  mv -f opentelemetry-webserver-sdk /opt/; \
  cd ..; \
  # Apache (Debian layout differs; if you truly need Apache, adapt here):
  # Copying your conf to Debian's apache2:
  cp opentelemetry_module.conf /etc/apache2/conf-available/opentelemetry_module.conf; \
  sed -i "s/libmod_apache_otel22.so/libmod_apache_otel.so/g" /etc/apache2/conf-available/opentelemetry_module.conf; \
  a2enconf opentelemetry_module || true; \
  # SDK installer:
  cd /opt/opentelemetry-webserver-sdk && ./install.sh; \
  cd /

# ---- NGINX: add load_module + include conf ----
RUN set -eux; \
  cp /otel-webserver-module/conf/nginx/opentelemetry_module.conf /opt/; \
  # Insert load_module early and include later in nginx.conf (line numbers may vary)
  sed -i '1iload_module /opt/opentelemetry-webserver-sdk/WebServerModule/Nginx/1.26.2/ngx_http_opentelemetry_module.so;' /etc/nginx/nginx.conf; \
  sed -i 's|http {|http {\n    include /opt/opentelemetry_module.conf;|g' /etc/nginx/nginx.conf

COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]
