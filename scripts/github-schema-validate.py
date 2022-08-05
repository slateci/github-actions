#!/usr/bin/env python

"""
This is a script to validate the schemas for the GitHub action and workflow YAML files.

This script uses the following system environmental variables as inputs:

* ``GITHUB_YAML_PATH``: specified by the GitHub workflow.
"""

import glob
import logging
import json
import jsonschema
import os
import requests
import yaml

# Set up logging:
if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'TRUE':
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(logging.INFO)


def find_files(path) -> list:
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

    response = requests.get(
        'https://raw.githubusercontent.com/SchemaStore/schemastore/master/src/schemas/json/github-action.json')
    result = json.loads(response.text)
    logging.debug(f"Found the GitHub action JSON schema:\n{result}")
    return result


def get_jsonschema_workflow() -> json:
    """
    Get the JSON schema for GitHub workflow files.
    :return: the schema as a json object
    """

    response = requests.get(
        'https://raw.githubusercontent.com/SchemaStore/schemastore/master/src/schemas/json/github-workflow.json')
    result = json.loads(response.text)
    logging.debug(f"Found the GitHub workflow JSON schema:\n{result}")
    return result


# Main:
if __name__ == '__main__':
    github_yaml_path = os.environ.get('GITHUB_YAML_PATH')
    logging.info(f"Beginning search for GitHub YAML files at: {github_yaml_path}")

    # Action files:
    action_files = find_files(os.path.join(github_yaml_path, "actions", "**", "*.yml"))
    logging.info(f"Found the GitHub action files:\n{action_files}")

    action_schema = get_jsonschema_action()
    for action_file in action_files:
        with open(action_file) as stream:
            logging.debug(f"Checking GitHub action schema for: {action_file}")
            try:
                data_loaded = yaml.safe_load(stream)
            except yaml.YAMLError as ex:
                raise ex
            jsonschema.validate(data_loaded, action_schema)

    # Workflow files:
    workflow_files = find_files(os.path.join(github_yaml_path, "workflows", "*.yml"))
    logging.info(f"Found the GitHub workflow files:\n{workflow_files}")

    workflow_schema = get_jsonschema_workflow()
    for workflow_file in workflow_files:
        with open(workflow_file) as stream:
            logging.debug(f"Checking GitHub workflow schema for: {workflow_file}")
            try:
                data_loaded = yaml.safe_load(stream)
            except yaml.YAMLError as ex:
                raise ex
            jsonschema.validate(data_loaded, workflow_schema)
