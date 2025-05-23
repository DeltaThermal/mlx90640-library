#!/usr/bin/env python
"""
Alternative setup.py for virtual environment installation.
This version links against the local library instead of system-installed one.
"""

import os
import sys

from setuptools import setup, Extension
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist
from distutils.spawn import find_executable
from glob import glob

# Get the path to the parent directory (where the C++ library is built)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

sources = ['mlx90640-python.cpp']
# If we have swig, use it.  Otherwise, use the pre-generated
# wrapper from the source distribution.
if find_executable('swig'):
    sources += ['MLX90640.i']
elif os.path.exists('MLX90640_wrap.cxx'):
    sources += ['MLX90640_wrap.cxx']
elif os.path.exists('MLX90640_wrap.c'):
    sources += ['MLX90640_wrap.c']
else:
    print("Error:  Building this module requires either that swig is installed\n"
          "        (e.g., 'sudo apt install swig') or that MLX90640_wrap.c is available.\n")
    sys.exit(1)

# Fix so that build_ext runs before build_py
class build_py_ext_first(build_py):
    def run(self):
        self.run_command("build_ext")
        return build_py.run(self)


# Make sure MLX90640_wrap.c is available for the source dist, also.
class sdist_ext_first(sdist):
    def run(self):
        self.run_command("build_ext")
        return sdist.run(self)

classifiers = ['Development Status :: 4 - Beta',
               'Operating System :: POSIX :: Linux',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.6',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: System :: Hardware']

_MLX90640 = Extension(
    '_MLX90640',
    include_dirs=[os.path.join(parent_dir, 'headers')],
    sources=sources,
    swig_opts=['-threads', '-c++', f'-I{os.path.join(parent_dir, "headers")}'],
    library_dirs=[parent_dir],
    libraries=['MLX90640_API'],
    runtime_library_dirs=[parent_dir],  # Add rpath for finding the library at runtime
)

setup(
    name = 'MLX90640',
    version = '0.0.2',
    classifiers = classifiers,
    ext_modules = [ _MLX90640 ],
    py_modules = ["MLX90640"],
    install_requires=[],
    cmdclass = {'build_py' : build_py_ext_first, 'sdist' : sdist_ext_first},
)