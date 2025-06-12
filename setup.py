from setuptools import setup, Extension, Command
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
import os
import shutil

class CustomBuildExt(build_ext):
    def copy_extensions_to_source(self):
        # Create target directory if it doesn't exist
        for ext in self.extensions:
            fullname = self.get_ext_fullname(ext.name)
            filename = self.get_ext_filename(fullname)
            src_filename = os.path.join(self.build_lib, filename)
            
            # Add debug output
            print(f"Looking for: {src_filename}")
            print(f"File exists: {os.path.exists(src_filename)}")
            
            # Modify the destination to use pkg/backend/core instead of backend/core
            dest_path = os.path.join('pkg', filename)
            dest_dir = os.path.dirname(dest_path)
            
            print(f"Destination: {dest_path}")
            
            # Ensure the destination directory exists
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copy the file if it exists
            if os.path.exists(src_filename):
                shutil.copy(src_filename, dest_path)
                print(f"Copied: {src_filename} -> {dest_path}")
            else:
                print(f"ERROR: Source file not found: {src_filename}")

setup(
    ext_modules=cythonize("pkg/backend/core/*.py"),
    cmdclass={'build_ext': CustomBuildExt},
)