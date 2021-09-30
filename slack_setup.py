# encoding: utf-8

import sys
from workflow import Workflow, ICON_WARNING, ICON_INFO, web, Variables
import os
import datetime
import calendar
import argparse
import requests

log = None

from workflow.notify import notify
from workflow import  PasswordNotFound


def main(wf):
    log = wf.logger
    parser = argparse.ArgumentParser()
    parser.add_argument('token', nargs="?")
    parser.add_argument('--clear', dest='clear', default=False,
                        action='store_true')
    parser.add_argument('--echo', dest='echo', default=False,
                        action='store_true')
    args = parser.parse_args(wf.args)
    if args.clear:
        try:
            wf.delete_password('slack_token')
        except PasswordNotFound :
            pass
        notify('Deleted.', 'Token deleted')

        return 0
    elif args.token:
            wf.save_password('slack_token', args.token)
            notify('Saved.',
                   'Token saved')
            return 0
    elif args.echo:
        log.debug(wf.get_password('slack_token'))
    else:
        notify('Problem in saving the token.',
               'Please use slacksetup to set your Slack API key. Received %s' % args.token)
        return 0

if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
