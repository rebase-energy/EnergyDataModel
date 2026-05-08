# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(".."))

# Copy notebook files from examples directory to docs/notebooks for nbsphinx
_docs_dir = os.path.dirname(os.path.abspath(__file__))
_examples_src = os.path.join(_docs_dir, "..", "examples")
_notebooks_dir = os.path.join(_docs_dir, "notebooks")

os.makedirs(_notebooks_dir, exist_ok=True)
for nb_file in glob.glob(os.path.join(_examples_src, "*.ipynb")):
    basename = os.path.basename(nb_file)
    dest = os.path.join(_notebooks_dir, basename)
    if not os.path.exists(dest) or os.path.getmtime(nb_file) > os.path.getmtime(dest):
        shutil.copy2(nb_file, dest)

# -- Project information -----------------------------------------------------

project = "EnergyDataModel"
copyright = "Rebase Energy"
author = "Rebase Energy"
release = "0.2.0"
version = "0.2.0"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "nbsphinx",
]

# nbsphinx: don't execute notebooks during the build (they're checked in with outputs)
nbsphinx_execute = "never"
nbsphinx_allow_errors = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_theme_options = {
    "navigation_depth": 2,
}

# Custom CSS — widens the class_hierarchy page so the Cytoscape iframe has room to breathe.
html_css_files = [
    "css/class-hierarchy.css",
]

# -- Extension configuration -------------------------------------------------

# Autodoc
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}
autodoc_member_order = "bysource"

# Napoleon settings for NumPy/Google style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_ivar = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
}

# sphinx-autodoc-typehints: evaluate `if TYPE_CHECKING:` blocks during doc generation
# so type-only imports (e.g. Carrier in bases.py — circular at runtime) resolve.
set_type_checking_flag = True
always_document_param_types = True


# -- Class-explorer regeneration ---------------------------------------------
# Regenerate edm-explorer.html (the Cytoscape class graph) before each build,
# so the iframe served from _static/ is always in sync with the live class
# hierarchy. Runs locally and on Read-the-Docs.


def _build_class_explorer(app):
    script = Path(__file__).parent.parent / "build_class_explorer.py"
    subprocess.run([sys.executable, str(script)], check=True)


def setup(app):
    app.connect("builder-inited", _build_class_explorer)
