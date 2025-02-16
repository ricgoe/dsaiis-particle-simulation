# -- Project information -----------------------------------------------------
# Conf.py file required for Sphinx documentation builder
# Used to specify project information on authors, version, release, etc.

#To ensure correct encoding: 
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath('../src')) #add path to source code, so that Sphinx can find it
if "src" in sys.modules:
    del sys.modules["src"]

project = "DSAIIS Particle Simulation"
author = "Richard Bihlmeier, Jannis Bollien, Jochen Hartlieb, Marcel Hilgers, Emil Ötting"
copyright = "2025"
version =  "0.0.1"
release = "0.0.1"

extensions = [
    "sphinx.ext.autodoc",      #automatically document all modules, classes, functions, etc.
    "sphinx.ext.viewcode",     #add links to the source code -> view source code of any object
    "sphinx.ext.autosummary",  #automatically generate summaries for module
    "sphinx.ext.napoleon",     #support for NumPy and Google style docstrings
    "sphinx_rtd_theme"         #readthedocs theme
    ]     

autosummary_generate = True     #automatically generate summaries for module
templates_path = ["_templates"] #folder for custom templates
html_theme = "sphinx_rtd_theme" #default theme
html_static_path = ['_static']  #Specifies the folder for static files (e.g.images) to be copied into the HTML output. Not yet used, useful for later implementation of images
html_theme_options = {          #options for the theme
    'collapse_navigation': False,
    'navigation_depth': 4,
}