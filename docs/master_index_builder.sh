SRC_DIR="./api"
content=""

echo "Collecting module-rst files"
for file in "$SRC_DIR"/*.rst; do
    if [ -f "$file" ]; then
        if [ "$(basename "$file")" = "index.rst" ]; then
            continue
        fi
        filename=$(basename "$file" .rst)
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
   _modules/index
${content}
   
EOF

echo "Successfully created index.rst"