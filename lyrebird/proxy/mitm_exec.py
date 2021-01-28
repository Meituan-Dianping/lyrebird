import re
import sys
from mitmproxy.tools.main import mitmdump

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(mitmdump())
