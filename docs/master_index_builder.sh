echo "Creating index.rst for Sphinx documentation builder"
echo << EOF > index.rst

Welcome to DSAIIS Particle Simulation's documentation
=====================================================
.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   index
EOF

echo "Successfully created index.rst"