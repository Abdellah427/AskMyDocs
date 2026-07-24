import os
import sys

# Make the project root importable so `import src.*` works from the tests.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
