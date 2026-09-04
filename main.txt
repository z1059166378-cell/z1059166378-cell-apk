

import os
import sys

def main():
    os.environ['ANDROID'] = '1'
    import a9_script
    a9_script.main()

if __name__ == '__main__':
    main()