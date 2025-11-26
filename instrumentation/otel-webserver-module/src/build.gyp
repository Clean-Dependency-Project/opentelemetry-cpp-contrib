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
        '-fPIC'
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
    # Linux configuration (MAIN FIX)
    # ======================================================================
    'conditions': [
      ['OS=="linux"', {
        'cflags': [
          '$(COMPILER_FLAGS)',     # MUST BE FIRST (so std=c++11 comes first)
          '-pthread',
          '-fPIC',
          '-g',
          '-O1',
          '-D_FORTIFY_SOURCE=1',

          # OVERRIDE ANY std=c++11 injected from Gradle
          '-std=c++14'
        ],

        'cflags_cc': [
          '$(COMPILER_FLAGS)',
          '-std=c++14'
        ],

        'include_dirs': [
          '../linux-fixed-headers',
          '$(ANSDK_DIR)/apache-log4cxx/0.11.0/include',
          '../include/util',
          '../include/core',
