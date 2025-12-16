
ARG image=debian:trixie
FROM $image AS build

ARG otel_cpp_version=1.17.0
ARG nginx_version=1.29.3

RUN apt-get update && \
    apt-get install --no-install-recommends --no-install-suggests -y \
      git \
      cmake \
      build-essential \
      curl \
      ca-certificates \
      libcurl4-openssl-dev \
      protobuf-compiler \
      libprotobuf-dev \
      libpcre2-dev \
      libabsl-dev && \
    update-ca-certificates

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
    -DWITH_ABSEIL=ON \
    .. \
  && cmake --build . --target all -j $(nproc) \
  && cmake --install . --prefix /opentelemetry-cpp/install

RUN mkdir -p otel-nginx/build && mkdir -p otel-nginx/src
COPY src otel-nginx/src/
COPY CMakeLists.txt nginx.cmake otel-nginx/
RUN cd otel-nginx/build \
  && cmake -DCMAKE_BUILD_TYPE=Release \
    -DNGINX_VERSION=$nginx_version \
    -DWITH_ABSEIL=ON \
    -DCMAKE_PREFIX_PATH=/opentelemetry-cpp/install \
    -DCMAKE_INSTALL_PREFIX=/otel-nginx/install \
    .. \
  && make -j$(nproc) \
  && make install

FROM scratch AS export
COPY --from=build /otel-nginx/install/otel_ngx_module.so .

FROM build AS run

COPY test/conf/nginx.conf /otel-nginx/nginx.conf
RUN curl -O https://nginx.org/download/nginx-$nginx_version.tar.gz && tar xf nginx-$nginx_version.tar.gz
RUN cd nginx-$nginx_version && ./configure --with-compat --prefix=/nginx && make -j$(nproc) && make install

CMD ["/nginx/sbin/nginx", "-c", "/otel-nginx/nginx.conf"]
