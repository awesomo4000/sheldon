#!/usr/bin/env python3
"""
Test runner for Seldon tests
Imports just the Seldon class without running main()
"""

import os
import sys
import unittest

# Read seldon file and extract just the class definition
with open('./seldon', 'r') as f:
    content = f.read()
    
# Find where main() starts and cut off there
main_index = content.find('def main():')
if main_index > 0:
    # Get everything before main()
    class_content = content[:main_index]
    
    # Execute just the imports and class definition
    exec(class_content, globals())
else:
    print("Could not find main() in seldon file")
    sys.exit(1)

# Now import and run the tests
from test_seldon_features import *

if __name__ == '__main__':
    unittest.main(argv=['run_tests.py'] + sys.argv[1:])