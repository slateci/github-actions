#!/usr/bin/env python

"""
Python script to send out emails using mailgun, looks at the environment for the
following parameters:

MAILGUN_SUBJECT: SLATE GitOps Change Summary
MAILGUN_BODY: body of text
MAILGUN_API_KEY: mailgun api key
MAILGUN_DOMAIN: slateci.io
MAILGUN_FROM: GitOps Notification <noreply@slateci.io>
MAILGUN_SEND_TO: comma separated list of recipients

Originally written by Suchandra Thapa
"""
import os
import sys

import requests


def verify_env() -> bool:
    """
    Verify environment to make sure variables above are present and valid
    :return: True if environment okay, False otherwise
    """
    mailgun_vars = {'MAILGUN_SUBJECT',
                    'MAILGUN_API_KEY',
                    'MAILGUN_DOMAIN',
                    'MAILGUN_FROM',
                    'MAILGUN_SEND_TO'}
    env_vars = set(os.environ.keys())
    if not mailgun_vars <= env_vars:
        difference = mailgun_vars - env_vars
        sys.stderr.write(f"Not all mailgun variables set, missing: {difference}\n")
        return False
    return True


def send_mail() -> None:
    """
    Send out a message using mailgun
    :return: None
    """
    mailgun_domain = os.environ['MAILGUN_DOMAIN']
    mailgun_url = f"https://api.mailgun.net/v3/{mailgun_domain}/messages"
    text_body = open('text_body').read()
    html_body = open('html_body').read()
    if len(text_body) == 0 and len(html_body) == 0:
        text_body = "Could not retrieve changes for this update"
    r = requests.post(mailgun_url,
                      auth=("api", os.environ['MAILGUN_API_KEY']),
                      data={"from": os.environ['MAILGUN_FROM'],
                            "to": os.environ['MAILGUN_SEND_TO'],
                            "subject": os.environ['MAILGUN_SUBJECT'],
                            "text": text_body,
                            "html": html_body})
    if r.status_code != requests.codes.ok:
        sys.stderr.write(f"Can't send email got HTTP code {r.status_code}: {r.text}\n")
        sys.exit(1)
    else:
        sys.stdout.write("Sent email through mailgun\n")
        sys.exit(0)


if __name__ == "__main__":
    if not verify_env():
        sys.stderr.write("Missing mailgun variables, exiting\n")
        sys.exit(1)
    send_mail()
