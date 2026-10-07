"""ノッポンズの音を書き出す: python3 render.py <出力フォルダ>
render.html の合成音をヘッドレス Chromium で 48kHz 描画し、ループごとに音量をそろえて MP3 にする。"""
import asyncio, base64, json, struct, subprocess, sys, os
from playwright.async_api import async_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=sys.argv[1]; SR=48000
IDS=['r1','r2','r3','b1','b2','b3','m1','m2','m3','v1','v2','v3','x1']
# target loudness (RMS, full scale = 1.0) per part
TARGET={'r':.13,'b':.13,'m':.085,'v':.09,'x':.05}
def target(i,h):
    if i=='drone': return .05
    if i=='x1' and h: return .09
    return TARGET[i[0]]
def mp3(name,b64,kbps=80):
    pcm=base64.b64decode(b64); w=os.path.join(HERE,name+'.wav')
    with open(w,'wb') as f:
        f.write(b'RIFF'+struct.pack('<I',36+len(pcm))+b'WAVEfmt '+struct.pack('<IHHIIHH',16,1,1,SR,SR*2,2,16)+b'data'+struct.pack('<I',len(pcm))+pcm)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',w,'-ac','1','-c:a','libmp3lame','-b:a',f'{kbps}k',os.path.join(OUT,name+'.mp3')],check=True)
    os.remove(w)
async def main():
    os.makedirs(OUT,exist_ok=True)
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page()
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+os.path.join(HERE,'render.html'))
        hits={}; report={}
        for i in IDS+['drone']:
            for h in ([True] if i=='drone' else [False,True]):
                r=await pg.evaluate(f"renderLoop('{i}',{str(h).lower()},{target(i,h)})")
                name=f"{i}_{'h' if h else 'n'}"; mp3(name,r['b64']); report[name]=(r['gain'],r['peak'])
                if i!='drone': hits[name]=r['hits']
        for on in [True,False]:
            r=await pg.evaluate(f"renderSting({str(on).lower()})"); name='sting_'+('on' if on else 'off'); mp3(name,r['b64'])
        json.dump(hits,open(os.path.join(HERE,'hits.json'),'w'),separators=(',',':'))
        print('errors:',errs); print(json.dumps(report))
        print('empty hits:',[k for k,v in hits.items() if not v])
        await b.close()
asyncio.run(main())
