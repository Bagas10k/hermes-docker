"""Generate an isolated browser lifecycle fixture, not a published UI."""
from pathlib import Path
import json

def render_fixture(width=300, height=200):
    if any(type(v) is not int or not 100 <= v <= 2000 for v in (width, height)):
        raise ValueError('dimensions must be integers from 100 to 2000')
    adapter = Path(__file__).with_name('browser_autoscroll.js').read_text()
    return f'''<!doctype html><meta charset="utf-8"><title>Edge scroll test fixture</title>
<style>body{{margin:0}}#body{{width:{width}px;height:{height}px;overflow:auto;touch-action:none;scroll-behavior:auto;direction:ltr}}#content{{width:2000px;height:2000px;background:repeating-linear-gradient(#eee 0 31px,#aaa 31px 32px)}}</style>
<div id="body" tabindex="0" aria-label="Scroll fixture"><div id="content"></div></div>
<script>{adapter}</script><script>
window.body=document.getElementById('body'); window.samples=[];
window.controller=attachEdgeScroll(body,s=>{{samples.push(s);if(samples.length>1000)samples.shift();}});
window.inspect=()=>({{active:controller.active,x:body.scrollLeft,y:body.scrollTop,samples:samples.length,selection:samples.at(-1)}});
</script>'''

if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('output');args=p.parse_args()
    Path(args.output).write_text(render_fixture())
