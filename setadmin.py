#!/usr/bin/env python

import argparse
import tracker

def setadmin(username):
    with tracker.app.app_context():
        u = tracker.user.get_user(username)
        if u is not None:
            u.set_perm(10)
        else:
            raise tracker.user.UserError('User does not exist.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Set super-admin privileges for user.')
    parser.add_argument('user', help='Target username')
    args = parser.parse_args()

    try:
        setadmin(args.user)
        print("[ OK ] Set super-admin privileges for {}".format(args.user))
    except tracker.user.UserError as e:
        print("[ERROR] {}".format(str(e)))
