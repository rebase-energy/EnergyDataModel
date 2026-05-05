# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = "EnergyDataModel"
copyright = "2023, rebase.energy"
author = "rebase.energy"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# Add these lines at the top of conf.py to import the necessary modules
import os
import sys

# Add the path to your project to the sys.path list (if not already present)
sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("../energydatamodel"))


# Add 'sphinx.ext.autodoc' to the list of extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.viewcode",
    "nbsphinx",
]

# Set the autodoc default flags
autodoc_default_options = {
    "members": True,  # Include class and instance methods
    "undoc-members": False,  # Include members without docstrings
    "show-inheritance": True,  # Show inheritance links
}
autodoc_member_order = "bysource"

intersphinx_mapping = {
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
}

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_ivar = True


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom CSS — widen the class_hierarchy page so the Cytoscape iframe
# has room to breathe.
html_css_files = [
    "css/class-hierarchy.css",
]


# -- Notebook copy step ------------------------------------------------------
# nbsphinx resolves notebook paths relative to the docs source directory, so
# example notebooks under ../examples/ are copied into docs/notebooks/ at build
# time. Keep build outputs out of git (docs/notebooks/ is gitignored).


def _copy_notebooks(app):
    import glob
    import os
    import shutil

    docs_dir = os.path.dirname(os.path.abspath(__file__))
    examples_src = os.path.join(docs_dir, "..", "examples")
    notebooks_dir = os.path.join(docs_dir, "notebooks")

    os.makedirs(notebooks_dir, exist_ok=True)
    for nb_file in glob.glob(os.path.join(examples_src, "*.ipynb")):
        dest = os.path.join(notebooks_dir, os.path.basename(nb_file))
        if not os.path.exists(dest) or os.path.getmtime(nb_file) > os.path.getmtime(dest):
            shutil.copy2(nb_file, dest)


# nbsphinx — don't re-execute notebooks during the build (they're checked in
# with their cell outputs).
nbsphinx_execute = "never"
nbsphinx_allow_errors = True


# -- Class-explorer regeneration ---------------------------------------------
# Regenerate edm-explorer.html (the Cytoscape class graph) before each build,
# so the iframe served from _static/ is always in sync with the live class
# hierarchy. Runs locally and on Read-the-Docs.


def _build_class_explorer(app):
    import subprocess
    import sys
    from pathlib import Path

    script = Path(__file__).parent.parent / "build_class_explorer.py"
    subprocess.run([sys.executable, str(script)], check=True)


def setup(app):
    app.connect("builder-inited", _copy_notebooks)
    app.connect("builder-inited", _build_class_explorer)
