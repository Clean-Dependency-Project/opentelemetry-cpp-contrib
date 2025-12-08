
#!/usr/bin/env python3
# Copyright (c) 2009 Google Inc. All rights reserved.
# BSD-style license; see LICENSE

import sys

try:
    # gyp-next exposes a 'gyp' module with the same entrypoint name
    import gyp
except ImportError as e:
    # Fallback to local 'pylib' only if you know it's Python 3 compatible.
    import os.path
    sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), 'pylib'))
    import gyp

if __name__ == '__main__':
    sys.exit(gyp.script_main())
