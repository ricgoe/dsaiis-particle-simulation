SRC_DIR="./api"
content=""

echo "Collecting module-rst files"
for file in "$SRC_DIR"/*.rst; do
    if [ -f "$file" ]; then
        if [ $/basename $file = "index.rst" ]; then             #skip index.rst if created automatically
            continue
        fi
        filename=$(basename $file)
        echo "Adding $filename to index.rst"
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

   api/index
${content}
   
EOF

echo "Successfully created index.rst"