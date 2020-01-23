import os
import slack


slack_token = os.environ["SLACK_API_TOKEN"]
client = slack.WebClient(token=slack_token)
channel_id = 'CQ3AMSQKA'  # gpu-leaderboard

for msg in client.channels_history(channel=channel_id).data['messages']:
    if 'GPU Leaderboard' in msg['text']:
        client.chat_delete(channel=channel_id, ts=msg['ts'])
