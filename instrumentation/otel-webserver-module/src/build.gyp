
{
  'targets': [{
    'target_name': 'opentelemetry_webserver_sdk',
    'type': 'shared_library',

    # Common defines
    'defines': ['TIMER_USE_CGT'],

    # macOS/Xcode block retained for parity
    'xcode_settings': {
      'OTHER_CFLAGS': [
        '-std=c++14',
        '-g',
        '-Wno-deprecated-register',
        '-pthread -fPIC'
      ],
      'OTHER_LDFLAGS': ['-lpthread -ldl -lz -stdlib=libstdc++']
    },

    # Project sources
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

    'conditions': [
      # ============================
      # Linux
      # ============================
      ['OS=="linux"', {
        'defines': [
          'LOG4CXX_STATIC',   # static log4cxx build
        ],

        'cflags': [
          '$(COMPILER_FLAGS)',
          '-pthread',
          '-fPIC',
          '-std=c++14',
          '-g',
          '-O1',
          '-D_FORTIFY_SOURCE=1',
        ],

        # Headers
        'include_dirs': [
          '../linux-fixed-headers',
          '$(ANSDK_DIR)/apache-log4cxx/$(LOG4CXX_VERSION)/include',
          '../include/util',
          '../include/core',
          '$(ANSDK_DIR)/opentelemetry/$(CPP_SDK_VERSION)/include/',
          '$(BOOST_INCLUDE)',
        ],

        # Library search paths -> translated to -L...
        'library_dirs': [
          '$(ANSDK_DIR)/apache-log4cxx/$(LOG4CXX_VERSION)/lib',
          '$(ANSDK_DIR)/apr-util/$(APRUTIL_VERSION)/lib',
          '$(ANSDK_DIR)/apr/$(APR_VERSION)/lib',
          '$(ANSDK_DIR)/expat/$(EXPAT_VERSION)/lib',
        ],

        # Final link settings (order matters). Use -l names so -L dirs apply.
        'link_settings': {
          'libraries': [
            # Resolve static libs with grouping to handle mutual references
            '-Wl,--start-group',
            '-llog4cxx',
            '-laprutil-1',
            '-lapr-1',
            '-lexpat',
            '-Wl,--end-group',

            # Your existing Boost static libs and flags
            '$(BOOST_LIB)',
            '$(LINKER_FLAGS)',
            '$(LIBRARY_FLAGS)',
          ],
        },

        # Additional linker flags
        'ldflags': [
          '-Wl,--exclude-libs=ALL',
          '-Wl,--gc-sections',
          '-Wl,-z,defs',
        ],
      }],

      # ============================
      # Windows (unchanged from your file)
      # ============================
      ['OS=="win"', {
        'default_configuration': 'Debug_x64',
        'configurations': {
          'Debug': {
            'defines': ['DEBUG', '_DEBUG'],
            'msvs_settings': {
              'VCCLCompilerTool': {
                'RuntimeLibrary': 1,
                'Optimization': 0,
              },
              'VCLinkerTool': {
                'OptimizeReferences': 2,
                'EnableCOMDATFolding': 2,
                'LinkIncremental': 1,
                'GenerateDebugInformation': 'true'
              }
            }
          },

          'Release': {
            'defines': ['NDEBUG'],
            'msvs_settings': {
              'VCCLCompilerTool': {
                'RuntimeLibrary': '0',
                'Optimization': 3,
                'FavorSizeOrSpeed': 1,
                'InlineFunctionExpansion': 2,
                'WholeProgramOptimization': 'true',
                'OmitFramePointers': 'true',
                'EnableFunctionLevelLinking': 'true',
                'EnableIntrinsicFunctions': 'true'
              },
              'VCLinkerTool': {
                'OptimizeReferences': 2,
                'EnableCOMDATFolding': 2,
                'LinkIncremental': 1
              }
            }
          },

          'Debug_x64': {
            'inherit_from': ['Debug'],
            'msvs_configuration_platform': 'x64'
          },

          'Release_x64': {
            'inherit_from': ['Release'],
            'msvs_configuration_platform': 'x64'
          },

          'Debug_x86': {
            'inherit_from': ['Debug'],
            'msvs_configuration_platform': 'Win32'
          },

          'Release_x86': {
            'inherit_from': ['Release'],
            'msvs_configuration_platform': 'Win32'
          }
        },

        'libraries': [
          '$(ANSDK_DIR)/apr/1.4.5/lib/apr-1.lib',
          '$(ANSDK_DIR)/apr-util/1.3.12/lib/aprutil-1.lib',
          '$(ANSDK_DIR)/apr-util/1.3.12/lib/xml.lib',
          '$(ANSDK_DIR)/apache-log4cxx/0.10.0/lib/log4cxx.lib',
          '$(ANSDK_DIR)/zeromq/3.2.5/lib/libzmq.lib',
          '$(ANSDK_DIR)/protobuf/2.5.0/lib/libprotoc.lib',
          '$(ANSDK_DIR)/protobuf/2.5.0/lib/libprotobuf.lib',

          '$(ANSDK_DIR)/boost/1.55.0/lib/libboost_filesystem-vc120-$(OTEL_BOOST_LIB_FLAGS)-1_55.lib',
          '$(ANSDK_DIR)/boost/1.55.0/lib/libboost_atomic-vc120-$(OTEL_BOOST_LIB_FLAGS)-1_55.lib',
          '$(ANSDK_DIR)/boost/1.55.0/lib/libboost_system-vc120-$(OTEL_BOOST_LIB_FLAGS)-1_55.lib',
          '$(ANSDK_DIR)/boost/1.55.0/lib/libboost_thread-vc120-$(OTEL_BOOST_LIB_FLAGS)-1_55.lib',
          '$(ANSDK_DIR)/boost/1.55.0/lib/libboost_chrono-vc120-$(OTEL_BOOST_LIB_FLAGS)-1_55.lib',
          '$(ANSDK_DIR)/boost/1.55.0/lib/libboost_atomic-vc120-$(OTEL_BOOST_LIB_FLAGS)-1_55.lib',
          '$(ANSDK_DIR)/boost/1.55.0/lib/libboost_date_time-vc120-$(OTEL_BOOST_LIB_FLAGS)-1_55.lib',
          '$(ANSDK_DIR)/boost/1.55.0/lib/libboost_regex-vc120-$(OTEL_BOOST_LIB_FLAGS)-1_55.lib',

          'Ws2_32.lib',
          'advapi32.lib',
          'shell32.lib',
          'mswsock.lib',
          'odbc32.lib',
          'rpcrt4.lib'
        ],

        'defines': [
          'LOG4CXX_STATIC',
          'ZMQ_STATIC',
          'BOOST_NO_CXX11_TEMPLATE_ALIASES',
          'GOOGLE_PROTOBUF_NO_RTTI'
        ],

        'include_dirs': [
          '$(ANSDK_DIR)/apache-log4cxx/0.10.0/include',
          '$(ANSDK_DIR)/apr/1.4.5/include',
          '$(ANSDK_DIR)/apr-util/1.3.12/include',
          '$(ANSDK_DIR)/zeromq/3.2.5/include',
          '$(ANSDK_DIR)/protobuf/2.5.0/include',
          '$(ANSDK_DIR)/boost/1.55.0/include',
          '../include/util',
          '../include/core',
          'protos',
        ]
      }]
    ]
  }]
}
