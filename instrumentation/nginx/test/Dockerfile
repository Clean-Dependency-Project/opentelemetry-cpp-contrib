
ARG image=debian:trixie
FROM $image AS build

ARG otel_cpp_version=1.17.0
ARG nginx_version=1.29.3

# Update and install build dependencies (Debian 13 changes applied)
RUN set -eux; \
    apt-get update; \
    apt-get install --no-install-recommends --no-install-suggests -y \
      build-essential \
      autoconf \
      libtool \
      pkg-config \
      ca-certificates \
      gcc \
      g++ \
      git \
      cmake \
      curl \
      zlib1g-dev \
      libprotobuf-dev \
      protobuf-compiler \
      libcurl4-openssl-dev \
      libpcre2-dev \
    ; \
    rm -rf /var/lib/apt/lists/*

# Build OpenTelemetry C++ (static libs installed under /opentelemetry-cpp/install)
RUN git clone --shallow-submodules --depth 1 --recurse-submodules -b v$otel_cpp_version \
      https://github.com/open-telemetry/opentelemetry-cpp.git \
  && cd opentelemetry-cpp \
  && mkdir build \
  && cd build \
  && cmake -DCMAKE_BUILD_TYPE=Release \
           -DWITH_OTLP_HTTP=ON \
           -DWITH_OTLP_GRPC=OFF \
           -DWITH_PROMETHEUS=OFF \
           -DWITH_ELASTICSEARCH=OFF \
           -DBUILD_TESTING=OFF \
           -DWITH_EXAMPLES=OFF \
           -DWITH_FUNC_TESTS=OFF \
           -DOPENTELEMETRY_INSTALL=ON \
           -DCMAKE_CXX_STANDARD=17 \
           -DBUILD_SHARED_LIBS=OFF \
           -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
           .. \
  && cmake --build . --target all -j "$(nproc)" \
  && cmake --install . --prefix /opentelemetry-cpp/install

# Build your NGINX module against the installed OTel C++ libs
RUN mkdir -p /otel-nginx/build /otel-nginx/src
COPY src /otel-nginx/src/
COPY CMakeLists.txt nginx.cmake /otel-nginx/
RUN cd /otel-nginx/build \
  && cmake -DCMAKE_BUILD_TYPE=Release \
           -DNGINX_VERSION="$nginx_version" \
           -DCMAKE_PREFIX_PATH=/opentelemetry-cpp/install \
           -DCMAKE_INSTALL_PREFIX=/otel-nginx/install \
           .. \
  && make -j"$(nproc)" \
  && make install

# Export the built module
FROM scratch AS export
COPY --from=build /otel-nginx/install/otel_ngx_module.so .

# Build and run NGINX from source with --with-compat so the module can be loaded
FROM debian:13 AS run

ARG nginx_version=1.29.3

# Minimal runtime deps for starting NGINX and fetching sources

RUN set -eux; \
    apt-get update; \
    apt-get install --no-install-recommends --no-install-suggests -y \
      ca-certificates \
      curl \
      build-essential \
      zlib1g-dev \
      libpcre2-dev \
      libprotobuf32t64 \
    ; \
    rm -rf /var/lib/apt/lists/*


COPY --from=build /otel-nginx/install/otel_ngx_module.so /otel-nginx/otel_ngx_module.so
COPY test/conf/nginx.conf /otel-nginx/nginx.conf

# Build and install NGINX with compat
RUN curl -fsSLO "https://nginx.org/download/nginx-${nginx_version}.tar.gz" \
  && tar xf "nginx-${nginx_version}.tar.gz" \
  && cd "nginx-${nginx_version}" \
  && ./configure --with-compat --prefix=/nginx \
  && make -j"$(nproc)" \
  && make install \
  && rm -rf "/nginx-${nginx_version}" "nginx-${nginx_version}.tar.gz"

CMD ["/nginx/sbin/nginx", "-c", "/otel-nginx/nginx.conf"]
