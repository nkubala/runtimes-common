"""TODO(nkubala): DO NOT SUBMIT without one-line documentation for cache_runner.

TODO(nkubala): DO NOT SUBMIT without a detailed description of cache_runner.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from google3.analysis.dremel.public.client import pywrapdremelclient

from absl import app
from absl import flags

import json
import logging
import os
import subprocess
import tempfile

from ftl.php import builder as ftl_php

FLAGS = flags.FLAGS

PHP = 'PHP'
LANGUAGES = [PHP]
LANGUAGE_CACHES = {
    PHP: 'php-package-lock-cache'
}

TOP_REQUESTED_PACKAGES_QUERY = """
SELECT
  FORMAT_TIME_USEC(event_id.time_usec) as event_time,
  request.docker_repository_name as repo,
  request.docker_tag_name as tag,
FROM
  gfstmp_cloud_containers.tmp_registry.last7days
WHERE
  request.gcs_bucket CONTAINS 'artifacts.ftl-global-cache.appspot.com' AND
  request.docker_repository_name = 'ftl-global-cache/{language_cache}' AND
  request.docker_tag_name != "" AND
  request.method = "HTTP_GET" AND
  -- response.http_status = 404 AND -- we want cache misses
  server_info.borg_job_name = "registry.server" -- PRODUCTION env.;
ORDER BY
  event_time desc
LIMIT
  {package_limit};
"""

ARGO_CACHE_LOGS_QUERY = """
SELECT
  label,
  text,
  timestamp
FROM
  argo.builds.last7days
WHERE
  project_id = 'gcp-runtimes' AND
  text LIKE '%[CACHE]%'
ORDER BY
  timestamp DESC;
"""

PACKAGE_LIMIT = 50
DREMEL_IO_TIMEOUT_SECONDS = 120
KEY_MAPPING_GCS_PATH = 'gs://ftl-global-cache/mapping.json'


def main(argv):
  del argv  # Unused.

  logging.getLogger().setLevel(logging.INFO)

  for language in LANGUAGES:
    populateCache(language)


def populateCache(language):
  # First, get the full list of image tags we're going to populate in the cache
  newEntries = runPackagesQuery(language)

  # Next, retrieve the existing mappings for image tags
  mappings = readMappings()
  print(mappings)

  existingEntries = retrieveCacheEntries(language)


def runPackagesQuery(language):
  dremel = pywrapdremelclient.DremelConnection.Connect()
  dremel.SetIOTimeout(float(DREMEL_IO_TIMEOUT_SECONDS))

  query = TOP_REQUESTED_PACKAGES_QUERY.format(
      package_limit=PACKAGE_LIMIT,
      language_cache=LANGUAGE_CACHES[language]
  )

  dremel.ExecuteQuery(query)
  results = dremel.itervalues()

  for (event_time, repo, tag) in results:
    print('[{time}] {repo}:{tag}'.format(
      time=event_time, repo=repo, tag=tag))
  return results


def readMappings():
  """read cache_key -> package tuple mappings from GCS config file
  return map of key to package, which we'll use as lookup when pushing images"""
  try:
    _, tmp = tempfile.mkstemp(text=True)
    command = ['gsutil', 'cp', KEY_MAPPING_GCS_PATH, tmp]
    subprocess.check_output(command, stderr=subprocess.STDOUT)
    with open(tmp, 'r') as f:
      return json.load(f)
  except subprocess.CalledProcessError as cpe:
    print('Error retrieving mapping file from GCS')
    print(cpe.output)
    # logging.error('Error retrieving mapping file from GCS')
    os.exit(1)
  finally:
    if tmp:
      os.remove(tmp)


if __name__ == '__main__':
  app.run(main)
