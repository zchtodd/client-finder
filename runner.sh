#!/bin/bash
set +e

declare -a arr=(
    "cheap plumber orlando",
    "plumbing companies in orlando",
    "best plumbers orlando",
    "orlando plumber",
    "commercial plumbing orlando",
    "plumber orlando fl",
    "best roofers in orlando",
    "roofing companies orlando"
)

for i in "${arr[@]}"
do
    node index.js "$i" >> place_names.csv
done
