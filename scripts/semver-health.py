#!/usr/bin/env python

import os
import logging
import subprocess
import semver
import yaml
from yaml.loader import SafeLoader

# Log all the things:
logging.getLogger().setLevel(logging.DEBUG)

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
        logging.debug(f"Raw result from Helm: {result}")
        data = yaml.load(result, Loader=SafeLoader)
        deployed_appversion = data[0]['app_version']
        logging.info(f"Found deployed appVersion: {deployed_appversion}")
    except subprocess.CalledProcessError as ex:
        raise ex

    logging.info("Discovering appVersion from source...")
    with open(chart_filepath) as stream:
        try:
            data_loaded = yaml.load(stream, Loader=SafeLoader)
            discovered_appversion = data_loaded['appVersion']
            logging.info(f"Found appVersion in Chart.yaml: {discovered_appversion}")
        except yaml.YAMLError as ex:
            raise ex

    logging.info("Verifying newer appVersion...")
    # deployed_appversion_parsed = semver.VersionInfo.parse(deployed_appversion)
    # discovered_appversion_parsed = semver.VersionInfo.parse(discovered_appversion)
    comparison = semver.compare(deployed_appversion, discovered_appversion)
    logging.debug(f"Raw semver comparison result: {comparison}")
    if semver.compare(discovered_appversion, deployed_appversion) < 1:
        raise Exception(
            f"The source appVersion \"{discovered_appversion}\" in Chart.yaml is not ahead" +
            f" of the deployed appVersion \"{deployed_appversion}\". Update the source and" +
            " try again."
        )
