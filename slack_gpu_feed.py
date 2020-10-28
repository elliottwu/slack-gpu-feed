import os
import numpy as np
import slack
import time
import subprocess
import random
import argparse


slack_token = os.environ["SLACK_API_TOKEN"]
client = slack.WebClient(token=slack_token)
channel_id = 'CQ3AMSQKA'  # gpu-leaderboard
# channel_id = 'C01D5SJ4PBN'  # gpu-leaderboard-debug

def disguise(string, replace='*'):
    return ''.join([c if random.random()>0.3 else replace for c in string])

def get_slack_ids(path):
    slack_ids = {}
    for l in open(path, 'r'):
        username, slack_id = l.split()
        slack_ids[username] = slack_id
    return slack_ids

def get_warnings(gpustats, limit, slack_id_path):
    slack_ids = get_slack_ids(slack_id_path)
    warning_users = []
    for line in gpustats.split('\n'):
        if '[total: ' in line:
            user, _, num_gpu = line.split()[:3]
            if int(num_gpu) > limit:
                warning_users.append(slack_ids[user])
    if warning_users:
        warning_msg = '\n:warning: These users have exceeded the GPU limit of %d per user: ' %limit
        warning_msg += ' '.join(['<@'+u+'>' for u in warning_users]) + '.'
        warning_msg += '\nPlease reduce the usage in order to give fair access to everyone! (Read: https://uox-vggrobots.slack.com/archives/C0SQQMBLN/p1603701994063500)'
    else:
        warning_msg = ''
    return warning_msg

def delete_msg(ts):
    client.chat_delete(
      channel=channel_id,
      ts=ts
    )

def push_msg(args):
    # depends on: https://github.com/albanie/slurm_gpustat
    gpustats = subprocess.run(['slurm_gpustat', '--color', '0'], stdout=subprocess.PIPE).stdout.decode('utf-8')

    out_msg = 'The GPU Leaderboard :slightly_smiling_face:\n'
    out_msg += '```AT: %s\n' %(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    out_msg += gpustats + '```'

    if args.limit >= 0 and args.slack_id_path is not None and os.path.isfile(args.slack_id_path):
        out_msg += get_warnings(gpustats, args.limit, args.slack_id_path)

    results = client.chat_postMessage(
      channel=channel_id,
      text=out_msg
    )
    return results

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=12, help='limit to number of GPUs per user, supply a posive number to trigger warnings')
    parser.add_argument('--slack_id_path', type=str, default='./slack_ids.txt', help='path to the file containing matches of usernames and Slack IDs')
    args = parser.parse_args()

    while True:
    # for i in range(3):
        res = push_msg(args)
        ts = res.data['ts']
        # time.sleep(10)
        time.sleep(3600*5)
        delete_msg(ts)

run()
