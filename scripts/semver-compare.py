#!/usr/bin/env python

"""
This is a script to return a GitHub output variable describing whether a deployed semantic version
is newer than its counterpart in the repository's ``Chart.yaml``, specifically the ``appVersion``
metadata.

This script uses the following system environmental variables as inputs:

* ``RELEASE_VERSION``: derived from the repository's ``Chart.yaml``, specifically the ``appVersion``
  metadata (calculated by the GitHub workflow).
* ``HELM_RELEASE_NAMESPACE``: specified as input to the GitHub workflow.
* ``HELM_RELEASE_NAMESPACE_SHORTHAND``: derived from ``HELM_RELEASE_NAMESPACE`` by the GitHub workflow.
* ``HELM_RELEASE_PREFIX``: specified as input to the GitHub workflow.

Additionally, the tools installed and configured by the GitHub composite action
``gcloud-helm-setup/action.yml`` are required.
"""

import logging
import os
import subprocess
import semver
import sys
import yaml
from yaml.loader import SafeLoader

# Set up logging:
if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'TRUE':
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(logging.INFO)

# Main:
if __name__ == '__main__':
    discovered_appversion = os.environ.get('RELEASE_VERSION')
    helm_release_namespace = os.environ.get('HELM_RELEASE_NAMESPACE')
    helm_release_namespace_shorthand = os.environ.get('HELM_RELEASE_NAMESPACE_SHORTHAND')
    helm_release_prefix = os.environ.get('HELM_RELEASE_PREFIX')

    command = [
        'helm', 'list',
        '-n', helm_release_namespace,
        '--filter', helm_release_prefix + '-' + helm_release_namespace_shorthand,
        '--output', 'yaml'
    ]

    logging.info(
        f"Discovering deployed appVersion for Helm release {helm_release_prefix}-{helm_release_namespace_shorthand}" +
        f" in the {helm_release_namespace} namespace..."
    )
    try:
        result = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                check=True,
                                text=True
                                ).stdout
        logging.debug(f"Raw result from Helm:\n{result}")
        data = yaml.load(result, Loader=SafeLoader)
        deployed_appversion = data[0]['app_version']
        logging.info(f"Found deployed appVersion: {deployed_appversion}")
    except subprocess.CalledProcessError as ex:
        raise ex

    logging.info("Discovering appVersion from source...")
    logging.info(f"Found appVersion from source: {discovered_appversion}")

    logging.info("Verifying newer appVersion...")
    comparison = semver.compare(deployed_appversion, discovered_appversion)
    logging.debug(f"Raw semver comparison result: {comparison}")

    if semver.compare(discovered_appversion, deployed_appversion) < 1:
        logging.info(
            f"The source appVersion \"{discovered_appversion}\" in Chart.yaml is not ahead" +
            f" of the deployed appVersion \"{deployed_appversion}\"."
        )
        sys.stdout.write("::set-output name=ahead::false\n")
    else:
        logging.info(
            f"The source appVersion \"{discovered_appversion}\" in Chart.yaml is ahead" +
            f" of the deployed appVersion \"{deployed_appversion}\"."
        )
        sys.stdout.write("::set-output name=ahead::true\n")
