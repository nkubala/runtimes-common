#!/bin/bash

# Pull down authorized public keys and add them as trusted
users=(${AUTHORIZED_USERS})

for user in ${users[@]}
do
  echo $user
done

ls $KOKORO_GFILE_DIR
touch $KOKORO_GFILE_DIR/copy.bara.sky

cd github/runtimes-common

git verify-commit HEAD
