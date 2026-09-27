"""Run bounded, real CPU chat streams; Linux RSS sampling, no dependencies."""
import argparse, json, pathlib, socket, subprocess, threading, time, urllib.request

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--server', required=True)
    ap.add_argument('--model', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--threads', type=int, default=2)
    ap.add_argument('--context', type=int, default=1024)
    ap.add_argument('--no-repack', action='store_true')
    args = ap.parse_args()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
    command = [args.server, '-m', args.model, '--host', '127.0.0.1', '--port', str(port), '-ngl', '0', '-t', str(args.threads), '-tb', str(args.threads), '-c', str(args.context), '-np', '1', '-b', '128', '-ub', '64']
    if args.no_repack: command.append('--no-repack')
    output = pathlib.Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    peak = [0]; stop = threading.Event()
    with output.with_suffix('.log').open('w') as log:
        proc = subprocess.Popen(command, stdout=log, stderr=log)
        def sample():
            while not stop.wait(.02):
                try:
                    for line in pathlib.Path(f'/proc/{proc.pid}/status').read_text().splitlines():
                        if line.startswith('VmRSS:'): peak[0] = max(peak[0], int(line.split()[1]))
                except FileNotFoundError: return
        worker = threading.Thread(target=sample, daemon=True); worker.start()
        try:
            base = f'http://127.0.0.1:{port}'
            ready = False
            for _ in range(300):
                if proc.poll() is not None: raise RuntimeError('server exited; inspect log')
                try:
                    with urllib.request.urlopen(base + '/health', timeout=1) as r: ready = r.status == 200
                except OSError: pass
                if ready: break
                time.sleep(.2)
            if not ready: raise TimeoutError('server not ready')
            runs = []
            for prompt in ['Write only a JavaScript debounce function with clearTimeout.', 'Write only a CSS rule for reduced motion.', 'Write only a JavaScript clamp function.']:
                payload = {'messages':[{'role':'user','content':prompt}], 'max_tokens':96, 'temperature':0, 'stream':True}
                request = urllib.request.Request(base+'/v1/chat/completions', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'})
                start = time.perf_counter(); first = None; text = ''; done = False; chunks = 0
                with urllib.request.urlopen(request, timeout=90) as response:
                    for raw in response:
                        if not raw.startswith(b'data: '): continue
                        data = raw[6:].strip()
                        if data == b'[DONE]': done = True; break
                        event = json.loads(data)
                        if event.get('error'): raise RuntimeError(str(event['error']))
                        for choice in event.get('choices', []):
                            content = choice.get('delta', {}).get('content') or ''
                            if content:
                                if first is None: first = time.perf_counter()-start
                                text += content; chunks += 1
                assert text and done, 'missing actual content or stream completion'
                runs.append({'prompt':prompt, 'ttft_s':first, 'total_s':time.perf_counter()-start, 'content_chunks':chunks, 'text':text, 'done':done})
            result = {'command':command, 'peak_sampled_rss_kib':peak[0], 'rss_under_1_5_gib':peak[0] <= 1.5*1024*1024, 'runs':runs, 'limits':'Three short requests, sampled RSS not cgroup memory or 4GB hardware certification; output correctness not assumed.'}
            output.write_text(json.dumps(result, indent=2)+'\n')
            print(json.dumps({k:v for k,v in result.items() if k not in ['command','runs']}, indent=2))
            print(json.dumps([{k:v for k,v in r.items() if k!='text'} for r in runs], indent=2))
        finally:
            proc.terminate()
            try: proc.wait(timeout=10)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait()
            stop.set(); worker.join(timeout=1)
if __name__ == '__main__': main()
