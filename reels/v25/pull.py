"""Rebuild a file sent from the HF sandbox as base64 chunks (tool-result JSON files) -> bytes."""
import sys, json, base64
out = sys.argv[1]; parts = sys.argv[2:]
s = ''.join(json.load(open(p))['content'] for p in parts).split('|')[0]
open(out, 'wb').write(base64.b64decode(s)); print(out, len(s))
