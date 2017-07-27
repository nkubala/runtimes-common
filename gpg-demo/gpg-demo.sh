#!/bin/bash

set -ex

# Pull down authorized public keys and add them as trusted
users=(${AUTHORIZED_USERS})

ls $KOKORO_GFILE_DIR

for user in ${users[@]}
do
  echo $user
  cat $KOKORO_GFILE_DIR/$user.asc
done

cd github/runtimes-common

git verify-commit HEAD
