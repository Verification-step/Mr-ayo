import os, json, asyncio, tempfile, requests, soundfile as sf, sounddevice as sd
from dotenv import load_dotenv
from websockets.server import serve
from agent import run_agent
from audio import record, transcribe

load_dotenv()
CLIENTS=set()

def tts(text):
    key=os.getenv('OPENROUTER_API_KEY','')
    if not key: return
    try:
        r=requests.post('https://openrouter.ai/api/v1/audio/speech',headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},json={'model':os.getenv('TTS_MODEL','fish-audio/s2.1-pro:free'),'input':text,'voice':os.getenv('TTS_VOICE','alloy'),'response_format':'wav'},timeout=90)
        if r.status_code >= 400: return
        f=tempfile.NamedTemporaryFile(suffix='.wav',delete=False); f.write(r.content); f.close()
        data,rate=sf.read(f.name,dtype='float32'); sd.play(data,rate); sd.wait()
    except Exception as e:
        print('TTS:',e)

def send_state(state,label,text=''):
    msg=json.dumps({'type':'state','state':state,'label':label,'text':text})
    for ws in list(CLIENTS):
        try: asyncio.create_task(ws.send(msg))
        except Exception: pass

async def handler(ws):
    CLIENTS.add(ws)
    await ws.send(json.dumps({'type':'state','state':'idle','label':'Ready','text':'Ctrl + Space to speak'}))
    try:
        async for raw in ws:
            m=json.loads(raw)
            if m.get('type')!='listen_once': continue
            try:
                send_state('listening','Listening','Speak now…')
                path=await asyncio.to_thread(record,5)
                send_state('thinking','Transcribing','Understanding your voice')
                text=await asyncio.to_thread(transcribe,path)
                if not text: continue
                send_state('thinking','Thinking',text)
                answer=await asyncio.to_thread(run_agent,text,send_state)
                await ws.send(json.dumps({'type':'reply','text':answer}))
                send_state('speaking','Speaking',answer)
                await asyncio.to_thread(tts,answer)
                send_state('idle','Ready','Ctrl + Space to speak')
            except Exception as e:
                await ws.send(json.dumps({'type':'reply','text':f'Error: {e}'}))
                send_state('error','Error',str(e))
    finally:
        CLIENTS.discard(ws)

async def main():
    host=os.getenv('MR_AYO_HOST','127.0.0.1'); port=int(os.getenv('MR_AYO_PORT','8765'))
    print(f'Mr Ayo engine listening on ws://{host}:{port}')
    async with serve(handler,host,port): await asyncio.Future()

if __name__=='__main__': asyncio.run(main())
