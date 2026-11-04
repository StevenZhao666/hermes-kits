# Torrent Download Debugging Workflow

When a magnet link or .torrent file "won't open":

## Step 1: Inspect the torrent
Read the .torrent file to extract info_hash, tracker URL, file name, size.
```
python -c "
with open('file.torrent','rb') as f: data=f.read()
# ... bencode parse ...
print('tracker:', tracker_url)
print('size:', total_length)
"
```

## Step 2: Check tracker response
Contact the tracker directly with HTTP GET. If it returns peers but they're all unreachable (behind NAT), the torrent needs DHT.

## Step 3: Check if peers are reachable
Try TCP connect to each peer IP:port. If all timeout → they're behind NAT/firewall.

## Step 4: Try DHT
Use aria2c with `--bt-tracker` adding public trackers. Watch SD (seed count):
- `SD:>0` → seeds exist, download should work
- `SD:0` after 2+ minutes → no one is seeding, torrent is dead

## Step 5: Verify seeds with multiple trackers
Add these public trackers for better DHT coverage:
- `udp://tracker.opentrackr.org:1337/announce`
- `udp://tracker.torrent.eu.org:451/announce`
- `udp://open.demonii.com:1337/announce`

## Common Issues

| Symptom | Diagnosis |
|---------|-----------|
| 0 peers from tracker | Tracker down or info_hash unknown |
| Peers returned but all timeout | All peers behind NAT |
| CN:>0 but SD:0, DL:0B | Connected to leechers only, no seeds |
| CN:0 after briefly CN:>0 | DHT routing nodes only, not actual peers |

## 关于私有 tracker 的资源

- 很多资源站用的是「半私有 tracker」：做种的人就是下过这个资源的人，且大多在 NAT 后面 → 做种数经常接近 0，任何工具都下不动。
- 判断依据：`SD:0` 持续两分钟以上 = 确实没有活跃做种，不是工具的问题。
