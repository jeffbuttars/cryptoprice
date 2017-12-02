#!/bin/bash

shopt -s nullglob

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$THIS_DIR";

SCRIPTS=$(ls -1 *.sql | sort)
# echo "$SCRIPTS"
# echo ""

cd "$THIS_DIR/../"
# echo "PWD: $(pwd)"
# echo ""

for script in ${SCRIPTS} ; do
    echo "${script}:"
    cat ${THIS_DIR}/${script}
    cat ${THIS_DIR}/${script} | apistar dbshell
done
