
from setuptools import Extension, setup
from Cython.Build import cythonize


extensions = [
    Extension(
        name="engine.book_core",
        sources=["engine/book_core.pyx"],
    )
]

setup(
    name="chronosmatch-core",
    ext_modules=cythonize(
        extensions,
        compiler_directives={"language_level": "3"},
    ),
)
