import os
import runpy
import sys

root = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(root, 'src')
if src not in sys.path:
    sys.path.insert(0, src)

main_path = os.path.join(src, 'pc', 'main.py')
sys.argv = [main_path] + sys.argv[1:]
runpy.run_path(main_path, run_name='__main__')
