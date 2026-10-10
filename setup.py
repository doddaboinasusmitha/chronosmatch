from setuptools import setup
from Cython.Build import cythonize

setup(
    name="chronosmatch",
    ext_modules=cythonize(
        ["ipc/order_wrapper.pyx"],
        compiler_directives={"language_level": "3"},
    ),
)