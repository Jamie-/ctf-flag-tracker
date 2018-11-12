#!/usr/bin/env python

import argparse
import tracker

def setadmin(username):
    with tracker.app.app_context():
        u = tracker.user.get_user(username)
        u.set_perm(10)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Set super-admin privileges for user.')
    parser.add_argument('user', help='Target username')
    args = parser.parse_args()

    setadmin(args.user)
    print("[ OK ] Set super-admin privileges for {}".format(args.user))
