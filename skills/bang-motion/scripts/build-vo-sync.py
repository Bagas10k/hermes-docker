#!/usr/bin/env python3
"""Build one VO track that is forced to fit per-beat windows.

Usage:
    python3 build-vo-sync.py beats.json [out.mp3]

beats.json:
    {"dur": 34.4, "lang": "id", "beats": [
        {"id": 1, "start": 0.8, "end": 6.6, "text": "..."},
        ...
    ]}

Why per-beat: writing narration as prose and stretching it to fit visuals
produces audio talking about something the screen is not showing. Beat
windows come first; the text is written to fit them.

TTS source is Google Translate's public endpoint (no key, no install).
Replace `fetch_tts` with any provider that returns an mp3.
"""
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

TEMPO_MIN, TEMPO_MAX = 0.92, 1.30  # outside this = rewrite text, don't stretch


def sh(cmd):
    return subprocess.check_output(cmd).decode().strip()


def dur(path):
    return float(sh(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                     '-of', 'csv=p=0', path]))


def fetch_tts(text, path, lang='id'):
    if len(text) > 190:
        raise ValueError('segment too long for one TTS call: ' + text[:40])
    q = urllib.parse.urlencode({'ie': 'UTF-8', 'q': text, 'tl': lang, 'client': 'tw-ob'})
    req = urllib.request.Request('https://translate.google.com/translate_tts?' + q,
                                 headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as r, open(path, 'wb') as f:
        f.write(r.read())


def main():
    cfg = json.load(open(sys.argv[1]))
    out_dir = os.path.dirname(os.path.abspath(sys.argv[1]))
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(out_dir, 'vo_sync.mp3')
    total, lang = cfg['dur'], cfg.get('lang', 'id')

    manifest = []
    for b in cfg['beats']:
        raw = os.path.join(out_dir, f"seg_{b['id']}_raw.mp3")
        fit = os.path.join(out_dir, f"seg_{b['id']}.mp3")
        fetch_tts(b['text'], raw, lang)
        d = dur(raw)
        window = b['end'] - b['start']
        tempo = max(TEMPO_MIN, min(TEMPO_MAX, d / window))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw,
                        '-filter:a', f'atempo={tempo:.4f}', fit], check=True)
        dfit = dur(fit)
        if dfit > window:  # never bleed into the next beat
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', fit,
                            '-t', f'{window:.3f}', fit + '.t'], check=True)
            os.replace(fit + '.t', fit)
            dfit = dur(fit)
        manifest.append({**b, 'raw_dur': round(d, 2), 'tempo': round(tempo, 3),
                         'fit_dur': round(dfit, 2)})
        print(f"beat {b['id']}: raw {d:5.2f}s tempo {tempo:.2f} -> {dfit:5.2f}s "
              f"(window {window:.2f}s)")

    inputs, filters = [], []
    for i, m in enumerate(manifest):
        inputs += ['-i', os.path.join(out_dir, f"seg_{m['id']}.mp3")]
        ms = int(round(m['start'] * 1000))
        filters.append(f'[{i}:a]adelay={ms}|{ms},apad[a{i}]')
    mix = (';'.join(filters) + ';' + ''.join(f'[a{i}]' for i in range(len(manifest)))
           + f'amix=inputs={len(manifest)}:duration=longest:dropout_transition=0,'
             f'atrim=0:{total},volume=1.0[out]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', mix,
                    '-map', '[out]', '-ar', '44100', '-c:a', 'libmp3lame', '-b:a', '192k',
                    out], check=True)
    print(f'\n{out} = {dur(out):.2f}s (target {total}s)')
    json.dump({'dur': total, 'beats': manifest}, open(os.path.join(out_dir, 'beats.json'), 'w'), indent=2)

    print('\nonset terukur (cocokkan dengan start beat):')
    log = subprocess.run(['ffmpeg', '-hide_banner', '-i', out, '-af',
                          'silencedetect=noise=-35dB:d=0.3', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    for line in log.splitlines():
        if 'silence_end' in line:
            print('  ', line.strip())
    print('\nAturan: onset vs start beat toleransi +/-0.25s. Lebih dari itu = '
          'offset salah, geser tween visual ke onset terukur.')


if __name__ == '__main__':
    main()