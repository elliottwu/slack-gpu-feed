import os
import slack
import time
import subprocess
import random


slack_token = os.environ["SLACK_API_TOKEN"]
client = slack.WebClient(token=slack_token)
channel_id = 'CQ3AMSQKA'  # gpu-leaderboard

def disguise(string, replace='*'):
    return ''.join([c if random.random()>0.3 else replace for c in string])

def delete_msg(ts):
    client.chat_delete(
      channel=channel_id,
      ts=ts
    )

def push_msg():
    all_results = {}
    num_wait = 0
    total_num_gpu = 0
    total_num_job = 0
    total_num_bash = 0
    lines = subprocess.run(['squeue', '-o "%u %P %t %b %j"'], stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
    for line in lines:
        if 'gpu' in line:
            username, pty, state, num_gpu, name = line.strip().strip('"').split(' ')
            if state == 'PD':
                num_wait += 1
                continue

            if 'gpu' not in num_gpu:
                continue

            num_gpu = num_gpu.split(':')
            if len(num_gpu) == 2:
                num_gpu = int(num_gpu[-1])

                if username not in all_results:
                    all_results[username] = [0,0,0]
                all_results[username][0] += num_gpu
                all_results[username][1] += 1
                total_num_gpu += num_gpu
                total_num_job += 1

                if name == 'bash' or name == 'sh' or name == 'zsh':
                    all_results[username][2] += 1
                    total_num_bash += 1

    all_results = sorted(all_results.items(), key=lambda kv: kv[1][0], reverse=True)

    out_msg = 'The GPU Leaderboard :slightly_smiling_face:\n'
    out_msg += '```AT: %s\n' %(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    out_msg += '===============================\n'
    out_msg += '%-*s%-*s%-*s%s\n' %(12, 'USER', 7, '#GPU', 7, '#JOB', '#BASH')
    out_msg += '\n'.join(['%-*s%-*d%-*d%d'%(12, disguise(username)+':', 7, num_gpu, 7, num_job, num_bash) for username, (num_gpu, num_job, num_bash) in all_results])
    out_msg += '\n%-*s%-*d%-*d%d' %(12, 'TOTAL:', 7, total_num_gpu, 7, total_num_job, total_num_bash)
    out_msg += '\n\n%-*s%d'%(19, '#jobs awaiting:', num_wait)
    out_msg += '\n===============================```'

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
