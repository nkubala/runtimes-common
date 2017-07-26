#!/bin/bash
sha=$(curl -X GET -H 'Accept: application/vnd.github.VERSION.sha' https://api.github.com/repos/nkubala/runtimes-common/commits/HEAD)
resp=$(curl -X GET -H 'Accept: application/vnd.github.cryptographer-preview' https://api.github.com/repos/nkubala/runtimes-common/commits/$sha)

echo $resp
