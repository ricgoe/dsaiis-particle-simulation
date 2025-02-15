
echo "Creating index.rst for Sphinx documentation builder"
cat << EOF > ./index.rst

Welcome to DSAIIS Particle Simulation's documentation
=====================================================
.. toctree::
   :maxdepth: 4
   :caption: Contents:

   modules/frontend
   modules/backend
   
EOF

echo "Successfully created index.rst"