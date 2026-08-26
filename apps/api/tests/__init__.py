"""Marks ``tests`` as a package.

Present so that pytest's prepend import mode resolves this directory's modules as
``tests.*`` rather than as top-level names. Without it, ``conftest.py`` is imported
once by pytest as ``conftest`` and again by ``from tests.conftest import ...`` as a
separate module object -- two copies of the same helpers, with fixtures defined on
one and classes imported from the other.
"""
