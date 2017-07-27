#!/bin/bash

set -ex

# prefixes are of the form "pub   2048D/"
key_prefix_length=12
key_length=16

for keyfile in $KOKORO_GFILE_DIR/*.asc
do
  # Import the public key
  gpg --import $keyfile
  user=$(basename $keyfile .asc)

  # Add it to the set of trusted keys
  full_key_line=$(gpg --list-keys --keyid-format LONG $user | grep pub)
  key=${full_key_line:$key_prefix_length:$key_length}

  echo "trusted-key 0x${key}" >> ~/.gnupg/gpg.conf
done

cd github/runtimes-common

git verify-commit HEAD
