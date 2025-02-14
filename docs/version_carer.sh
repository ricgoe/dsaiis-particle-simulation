echo "Updating Docs-Version"
current_version=$(cat ../version.txt)

echo "Current Version: $curret_version"

current_major_version=${current_version%.*}
current_minor_version=${current_version##*.}

new_minor_version=$((current_minor_version + 1))

: > version.txt #Clear version.txt by replace current content with empty input

new_version = "$current_major_version.$new_minor_version"
echo "$new_version" > version.txt

echo "Successfully updated version.txt"
echo "Version updated from $current_version to $new_version"