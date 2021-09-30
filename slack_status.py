# encoding: utf-8

import sys
from workflow import Workflow, ICON_WEB, ICON_WARNING, web, Variables, \
    PasswordNotFound
import os
import datetime
import calendar
import argparse
import requests
from workflow.notify import notify

log = None


def convert_minutes_to_epoch(mins):
    future = datetime.datetime.utcnow() + datetime.timedelta(minutes=mins+1)
    epoch = calendar.timegm(future.timetuple())
    return epoch


def main(wf):
    log = wf.logger

    parser = argparse.ArgumentParser()
    parser.add_argument('text')
    parser.add_argument('icon')
    parser.add_argument('minutes', type=int, nargs="?", const=0,
                        default=os.environ['default'])
    parser.add_argument('--dnd', dest='dnd', default=False,
                        action='store_true')
    parser.add_argument('--close', dest='close', default=False,
                        action='store_true')
    parser.add_argument('--reset', dest='reset', default=False,
                        action='store_true')

    # parse the script's arguments
    args = parser.parse_args(wf.args)
    data = {
        "profile": {
            "status_text": args.text,
            "status_emoji": args.icon
        }
    }
    # if 0 we go indefinitely
    if args.minutes:
        log.debug('setting mintues')
        # part of slack uses epoch
        epoch = convert_minutes_to_epoch(args.minutes)
        data['profile']["status_expiration"] = epoch
        # this should be converted in end time, needed?
        # data['profile']["status_text"] += " (back in %s m)"%args.minutes
    try:
        api_key = wf.get_password('slack_token')
    except PasswordNotFound:  # API key has not yet been set
        notify("No API key set.",
               'Please use `sssetup` to set your Slack token.')
        print(Variables(u'arg', FAILED=1))
        return 1
    auth = {'Authorization': 'Bearer %s' % wf.get_password('slack_token')}
    res = requests.post('https://slack.com/api/users.profile.set', json=data,
                        headers=auth)
    if not res.json()['ok']:
        notify("Error making the call for profile", res.text)
        log.debug(res.text)
        print(Variables(u'arg', FAILED=1))
        return 1
    v = None
    # dnd set reset and close slack
    if args.dnd:
        data = {"num_minutes": args.minutes}
        res = requests.get('https://slack.com/api/dnd.setSnooze', params=data,
                           headers=auth)
        if not res.json()['ok']:
            notify("Error making the call for snooze", res.text)
            log.debug(res.text)
            print(Variables(u'arg', FAILED=1))
            return 1
    if args.close:
        v = Variables(WF_CLOSE=1, WF_SECONDS=args.minutes * 60,
                      WF_MINUTES=args.minutes)
    # # awast rest but no close, too complex scenario, skipped.
    # if args.away:
    #     data = {"presence":"away", "token": wf.get_password('slack_token')}
    #     res=requests.post('https://slack.com/api/users.setPresence', params=data, headers=auth)
    #     v = Variables(u'arg', WF_RESET=1, WF_SECONDS_RESET=args.minutes*60,WF_MINUTES=args.minutes)

    if args.reset:
        data = {"presence": "auto"}
        res = requests.post('https://slack.com/api/users.setPresence',
                            params=data, headers=auth)
        v = Variables(u'arg', WF_RESET=1)
        if not res.json()['ok']:
            notify("Error making the call for presence", res.text)
            print(Variables(u'arg', FAILED=1))
            return 1

    # for variable, print only that one, otherwise does not work.
    print(v)
    return 0


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
