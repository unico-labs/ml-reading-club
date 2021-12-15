#!/bin/bash

# not testing clear view because repository is not mocked
VIEWS="winners voters"

for view in $VIEWS; do
    echo "Testing view $view"
    ./bin/helper --view $view && {
        echo "View $view passed!" || echo "View $view failed!"
        printf "\n"
    }
done
