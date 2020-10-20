import os
import slack
import time
import subprocess
import random


slack_token = os.environ["SLACK_API_TOKEN"]
client = slack.WebClient(token=slack_token)
channel_id = 'CQ3AMSQKA'  # gpu-leaderboard
# channel_id = 'C01D5SJ4PBN'  # gpu-leaderboard-debug

def disguise(string, replace='*'):
    return ''.join([c if random.random()>0.3 else replace for c in string])

def delete_msg(ts):
    client.chat_delete(
      channel=channel_id,
      ts=ts
    )

def push_msg():
    # depends on: https://github.com/albanie/slurm_gpustat
    gpustats = subprocess.run(['slurm_gpustat', '--color', '0'], stdout=subprocess.PIPE).stdout.decode('utf-8')

    out_msg = 'The GPU Leaderboard :slightly_smiling_face:\n'
    out_msg += '```AT: %s\n' %(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    out_msg += gpustats + '```'

    results = client.chat_postMessage(
      channel=channel_id,
      text=out_msg
    )
    return results


while True:
# for i in range(3):
    res = push_msg()
    ts = res.data['ts']
    # time.sleep(10)
    time.sleep(3600*5)
    delete_msg(ts)
