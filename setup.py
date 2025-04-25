# setup.py

import os
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

# List only the API plus the Linux I²C driver. 
# If you want the Raspberry-Pi bcm2835 driver instead, uncomment that line.
drivers = [
    os.path.join("functions", "MLX90640_API.cpp"),
    os.path.join("functions", "MLX90640_LINUX_I2C_Driver.cpp"),
    # os.path.join("functions", "MLX90640_RPI_I2C_Driver.cpp"),
]

ext_modules = [
    Pybind11Extension(
        "mlx90640._mlx90640",               # name of the resulting .so
        sources=drivers + ["mlx90640/bindings.cpp"],
        include_dirs=["headers"],
        language="c++",
        extra_compile_args=["-std=c++17"],
    ),
]

setup(
    name="mlx90640-library",
    version="0.1.0",
    author="Wesley Newman",
    author_email="chickens4wes@gmail.com",
    description="Python bindings for the MLX90640 thermal sensor",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    packages=["mlx90640"],
    install_requires=["pybind11"],
    setup_requires=["pybind11"],
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
