"""Re-level a finished reel's audio to -14.5 LUFS, peaks <= -1.5 dBTP (video copied). usage: python3 loudfix.py <file.mp4>"""
import re, os, sys, subprocess as sp
f = sys.argv[1]
r = sp.run(['ffmpeg', '-hide_banner', '-i', f, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]); g = round(-14.5 - I, 2)
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-c:v', 'copy', '-af', f'volume={g}dB,alimiter=limit=0.84:level=false', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', f + '.t.mp4'], check=True); os.replace(f + '.t.mp4', f)
r = sp.run(['ffmpeg', '-hide_banner', '-i', f, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
print(f, 'before', I, 'after', re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1], 'peak', re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1])
