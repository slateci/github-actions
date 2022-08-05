#!/usr/bin/env python

"""
This is a script to validate the schemas for the GitHub action and workflow YAML files and uses
the YAML 1.2 compliant ``ruamel.yaml`` package (necessary to prevent ``on:`` from being converted to
``True:``, etc.).

This script uses the following system environmental variables as inputs:

* ``GITHUB_YAML_PATH``: specified by the GitHub workflow.
"""

import glob
import logging
import json
import jsonschema
import os
import requests

from ruamel.yaml import YAML

# Set up logging:
if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'TRUE':
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(logging.INFO)


def find_files(path: str) -> list:
    """
    Find the list of files given a path pattern.
    :param path: the path to search
    :return: a list of file paths
    """

    return glob.glob(pathname=path)


def get_jsonschema_action() -> json:
    """
    Get the JSON schema for GitHub action files.
    :return: the schema as a json object
    """

    response = requests.get('https://json.schemastore.org/github-action.json')
    result = json.loads(response.text)
    logging.info("Found the GitHub action JSON schema.")
    return result


def get_jsonschema_workflow() -> json:
    """
    Get the JSON schema for GitHub workflow files.
    :return: the schema as a json object
    """

    response = requests.get('https://json.schemastore.org/github-workflow.json')
    result = json.loads(response.text)
    logging.info("Found the GitHub workflow JSON schema.")
    return result


def validate_schemas(pathpattern: str, schema: dict) -> None:
    """
    Validates the schemas for the found YAML files
    :param pathpattern: the path to search
    :param schema: the schema
    :return: None
    """
    files = find_files(pathpattern)
    logging.info(f"Found the GitHub files:\n{files}")

    for file in files:
        with open(file) as stream:
            logging.info(f"Checking GitHub schema for: {file}")
            yaml = YAML(typ='safe')
            data_loaded = yaml.load(stream)
            logging.debug(f"Data loaded:\n{data_loaded}")
            jsonschema.validate(data_loaded, schema)


# Main:
if __name__ == '__main__':
    github_yaml_path = os.environ.get('GITHUB_YAML_PATH')

    # Action files:
    action_schema = get_jsonschema_action()
    action_path = os.path.join(github_yaml_path, "actions", "**", "*.yml")
    logging.info(f"Validating GitHub action files at: {action_path}")
    validate_schemas(action_path, action_schema)

    # Workflow files:
    workflow_schema = get_jsonschema_workflow()
    workflow_path = os.path.join(github_yaml_path, "workflows", "*.yml")
    logging.info(f"Validating GitHub action files at: {workflow_path}")
    validate_schemas(workflow_path, workflow_schema)

    logging.info("SUCCESS!")
