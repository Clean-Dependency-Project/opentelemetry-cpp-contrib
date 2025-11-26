{
  'targets': [{
    'target_name': 'opentelemetry_webserver_sdk',
    'type': 'shared_library',

    'defines': ['TIMER_USE_CGT'],

    # ======================================================================
    # macOS / Xcode settings
    # ======================================================================
    'xcode_settings': {
      'OTHER_CFLAGS': [
        '-std=c++14',
        '-g',
        '-Wno-deprecated-register',
        '-pthread',
        '-fPIC',
      ],
      'OTHER_LDFLAGS': ['-lpthread', '-ldl', '-lz', '-stdlib=libstdc++']
    },

    # ======================================================================
    # Source files
    # ======================================================================
    'sources': [
      'core/api/WSAgent.cpp',
      'core/api/RequestProcessingEngine.cpp',
      'core/api/ApiUtils.cpp',
      'core/api/SpanNamer.cpp',
      'core/api/opentelemetry_ngx_api.cpp',

      'core/AgentLogger.cpp',
      'core/AgentCore.cpp',

      'core/sdkwrapper/SdkHelperFactory.cpp',
      'core/sdkwrapper/ScopedSpan.cpp',
      'core/sdkwrapper/ServerSpan.cpp',
      'core/sdkwrapper/SdkWrapper.cpp',

      'util/SpanNamingUtils.cpp',
      'util/RegexResolver.cpp'
    ],

    # ======================================================================
    # Linux Configuration (OUR MAIN FOCUS)
    # ======================================================================
    'conditions': [
      ['OS=="linux"', {
        'cflags': [
          '-std=c++14',                   # FORCE C++14 (fixes your error)
          '-pthread',
          '-fPIC',
          '-g',
          '-O1',
          '-D_FORTIFY_SOURCE=1',
        ],

        'cflags_cc': [
          '-std=c++14',                   # ensure for C++ compiler too
        ],

        'include_dirs': [
          '../linux-fixed-headers',
          '$(ANSDK_DIR)/apache-log4cxx/0.11.0/include',
          '../include/util',
          '../include/core',
          '$(ANSDK_DIR)/opentelemetry/$(CPP_SDK_VERSION)/include/',
          '$(BOOST_INCLUDE)',
        ],

        'libraries': [
          '$(ANSDK_DIR)/apr/1.7.0/lib/libapr-1.a',
          '$(ANSDK_DIR)/apr-util/1.6.1/lib/libaprutil-1.a',
          '$(ANSDK_DIR)/expat/2.3.0/lib/libexpat.a',
          '$(ANSDK_DIR)/apache-log4cxx/0.11.0/lib/liblog4cxx.a',

          # ------------------------------------------------------------------
          # OpenTelemetry libraries
          # ------------------------------------------------------------------
          '$(ANSDK_DIR)/opentelemetry/$(CPP_SDK_VERSION)/lib/libopentelemetry_common.so',
          '$(ANSDK_DIR)/opentelemetry/$(CPP_SDK_VERSION)/lib/libopentelemetry_resources.so',
          '$(ANSDK_DIR)/opentelemetry/$(CPP_SDK_VERSION)/lib/libopentelemetry_trace.so',
          '$(ANSDK_DIR)/opentelemetry/$(CPP_SDK_VERSION)/lib/libopentelemetry_otlp_recordable.so',
          '$(ANSDK_DIR)/opentelemetry/$(CPP_SDK_VERSION)/lib/libopentelemetry_exporter_ostream_span.so',
          '$(ANSDK_DIR)/opentelemetry/$(CPP_SDK_VERSION)/lib/libopentelemetry_exporter_otlp_grpc.so',

          # Boost static libs
          '$(BOOST_LIB)',

          # Extra linker settings from Gradle
          '$(LINKER_FLAGS)',
          '$(LIBRARY_FLAGS)',
        ],

        'ldflags': [
          '-Wl,--exclude-libs=ALL',
          '-Wl,--gc-sections',
          '-Wl,-z,defs',
        ]
      }],

      # ======================================================================
      # Windows fallback configs (left untouched)
      # ======================================================================
      ['OS=="win"', {
        'default_configuration': 'Debug_x64',
        'configurations': {
          'Debug': {
            'defines': ['DEBUG', '_DEBUG'],
          },
          'Release': {
            'defines': ['NDEBUG'],
          },
          'Debug_x64': {
            'inherit_from': ['Debug'],
            'msvs_configuration_platform': 'x64',
          },
          'Release_x64': {
            'inherit_from': ['Release'],
            'msvs_configuration_platform': 'x64',
          }
        },

        'libraries': [
          '$(ANSDK_DIR)/apr/1.4.5/lib/apr-1.lib',
          '$(ANSDK_DIR)/apr-util/1.3.12/lib/aprutil-1.lib',
