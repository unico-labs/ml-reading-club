#!/bin/bash

VIEWS="winners voters clear"

for view in $VIEWS; do
    echo "Testing view $view"
    ./bin/helper --view $view && {
        echo "View $view passed!" || echo "View $view failed!"
        printf "\n"
    }
done
