import os
import shutil

"""
Plugin project generator
"""

here = os.path.dirname(__file__)
demo_root = os.path.abspath(os.path.join(here, 'demo_project'))


class PluginProjectBuilder:

    def build(self, path=None):
        if not path:
            path = os.path.abspath('./demo')
        if os.path.exists(path):
            for demo_item in os.listdir(demo_root):
                src = os.path.abspath(os.path.join(demo_root, demo_item))
                dst = os.path.abspath(os.path.join(path, demo_item))
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
        else:
            shutil.copytree(demo_root, path)
