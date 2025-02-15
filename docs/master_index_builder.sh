
echo "Creating index.rst for Sphinx documentation builder"
cat << EOF > ./index.rst

Welcome to DSAIIS Particle Simulation's documentation
=====================================================
.. toctree::
   :maxdepth: 6
   :caption: Contents:

   modules
   
EOF

echo "Successfully created index.rst"