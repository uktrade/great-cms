#!/bin/sh
DSM_URL="https://trade.invisionapp.com/dsm-export/department-for-international-trade/great"

# Fetching CSS variables
echo Fetching "$DSM_URL/_style-params.css?key=******"
curl "$DSM_URL/_style-params.css?key=$DSM_TOKENS_KEY" -o design-system/_style-params.css
echo 'CSS variables in design-system/_style-params.css has been updated\r\n\r\n'

# Fetching Icons
echo Fetching "$DSM_URL/icons.zip?key=******"
curl "$DSM_URL/icons.zip?key=$DSM_TOKENS_KEY" -o design-system/components/icon/icons/icons.zip
cd design-system/components/icon/icons
unzip -o -j icons.zip
rm -f icons.zip

# Optimising SVGs
if ! [ -x "$(command -v svgcleaner)" ]; then
    echo 'Warning: svgcleaner is not installed and the SVG icons have not been optimised and reduced in size.' >&2
    echo 'run "brew install svgcleaner" or check https://github.com/RazrFalcon/svgcleaner' >&2
    exit 1
fi;

for file in *.svg; 
    do svgcleaner --quiet --apply-transform-to-paths --copy-on-error --indent=4 "${file}" "${file}";
done;
