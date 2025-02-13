echo "Creating index.rst for Sphinx documentation builder"
cat << EOF > ./index.rst

Welcome to DSAIIS Particle Simulation's documentation
=====================================================
.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   
EOF

echo "Successfully created index.rst"