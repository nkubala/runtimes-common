#!/bin/bash

set -ex

# Pull down authorized public keys and add them as trusted
users=(${AUTHORIZED_USERS})

# prefixes are of the form "pub   2048D/"
key_prefix_length=12
key_length=16

for user in ${users[@]}
do
  # Import the public key
  gpg --import $KOKORO_GFILE_DIR/$user.asc

  # Add it to the set of trusted keys
  full_key_line=$(gpg --list-keys --keyid-format LONG $user | grep pub)
  key=${full_key_line:$key_prefix_length:$key_length}

  echo "trusted-key 0x${key}" >> ~/.gnupg/gpg.conf
done

cd github/runtimes-common

git verify-commit HEAD
