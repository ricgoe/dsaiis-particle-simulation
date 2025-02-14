SRC_DIR="../src"
content=""

echo "Collecting module-rst files"
for file in "$SRC_DIR"/*.rst; do
    if [ -f "$file" ]; then
        echo "Adding $file to index.rst"
        content+=$'   '"${filename}"$'\n'
    fi
done

echo "Creating index.rst for Sphinx documentation builder"
cat << EOF > ./index.rst

Welcome to DSAIIS Particle Simulation's documentation
=====================================================
.. toctree::
   :maxdepth: 2
   :caption: Contents:

    modules
${content}
   
EOF

echo "Successfully created index.rst"