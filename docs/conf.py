# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

project = "blentom"
copyright = "2024, Dominik Brandstetter"
author = "Dominik Brandstetter"
release = "0.1"

# -- General configuration ---------------------------------------------------

extensions = []

templates_path = ["source/_templates"]
exclude_patterns = []

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# -- Options for HTML output -------------------------------------------------

html_theme = "alabaster"
html_static_path = ["source/_static"]
