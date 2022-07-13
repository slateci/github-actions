#!/usr/bin/env python

"""
This is a script to return a GitHub output variable describing the bumped semantic version in the
repository's ``Chart.yaml``, specifically the ``appVersion`` metadata.

This script uses the following system environmental variables as inputs:

* ``RELEASE_VERSION``: derived from the repository's ``Chart.yaml``, specifically the ``appVersion``
  metadata (calculated by the GitHub workflow).
* ``HELM_RELEASE_NAMESPACE``: specified as input to the GitHub workflow.
* ``HELM_RELEASE_NAMESPACE_SHORTHAND``: derived from ``HELM_RELEASE_NAMESPACE`` by the GitHub workflow.
* ``HELM_RELEASE_PREFIX``: specified as input to the GitHub workflow.
* ``PRERELEASE_DATETIME_SUFFIX``: datetime object to apply as pre-release suffix

Additionally, the tools installed and configured by the GitHub composite action
``gcloud-helm-setup/action.yml`` are required.
"""

import logging
import os
import subprocess
import semver
import sys
import yaml

from datetime import datetime
from yaml.loader import SafeLoader

# Set up logging:
if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'TRUE':
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(logging.INFO)

# Main:
if __name__ == '__main__':
    helm_release_namespace = os.environ.get('HELM_RELEASE_NAMESPACE')
    helm_release_namespace_shorthand = os.environ.get('HELM_RELEASE_NAMESPACE_SHORTHAND')
    helm_release_prefix = os.environ.get('HELM_RELEASE_PREFIX')
    prerelease_datetime_suffix = os.environ.get('PRERELEASE_DATETIME_SUFFIX')

    if helm_release_namespace == 'production':
        raise Exception("This script is not appropriate for the production environment.")

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

    deployed_versioninfo = semver.VersionInfo.parse(deployed_appversion)

    if helm_release_namespace == 'development':
        new_versioninfo = deployed_versioninfo.finalize_version()
        if semver.compare(str(new_versioninfo), str(deployed_appversion)) == 0:
            new_versioninfo = deployed_versioninfo.finalize_version().bump_patch()

        now = datetime.now()
        date_time = now.strftime(prerelease_datetime_suffix)
        app_version = f"{str(new_versioninfo)}-pre.{date_time}"

        logging.info(f"New appVersion to apply: {app_version}")
        sys.stdout.write(f"::set-output name=version::{app_version}\n")
    else:
        new_versioninfo = deployed_versioninfo.finalize_version().bump_patch()
        app_version = f"{str(new_versioninfo)}"

        logging.info(f"New appVersion to apply: {app_version}")
        sys.stdout.write(f"::set-output name=version::{str(new_versioninfo)}\n")
