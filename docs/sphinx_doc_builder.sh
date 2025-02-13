echo "Creating Python-file conf.py for Sphinx documentation builder"

#Check current version from version.txt, if not existing, create version.txt with version 0.1.0
if [ ! -f version.txt ]; then
  echo "0.1" > version.txt    #starting version
fi

#Read version from version.txt, show current version
version=$(cat version.txt)
echo "Current version: $version"

#Split version into major and minor
IFS='.' read -r major minor <<< "$version"

#Increment minor version by 1 until project is handed in
minor=$((minor+1))

#Put together updated major and minor version
version_update="$major.$minor"

#Write updated version into version.txt
echo "$version_update" > version.txt


cat << EOF > conf.py #Following content until 'EOF' is written into conf.py file, implementing shell-variables is possible with $variable

# -- Project information -----------------------------------------------------
# Conf.py file required for Sphinx documentation builder
# Used to specify project information on authors, version, release, etc.

#To ensure correct encoding: 
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath('../src')) #add path to source code, so that Sphinx can find it

project = "DSAIIS Particle Simulation"
author = "Richard Bihlmeier, Jannis Bollien, Jochen Hartlieb, Marcel Hilgers, Emil Ötting"
copyright = "2025"
version =  "$version_update"
release = "$version_update"

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
EOF
