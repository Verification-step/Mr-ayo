import os, base64, tempfile, requests, sounddevice as sd, soundfile as sf

OR_URL='https://openrouter.ai/api/v1/chat/completions'

def record(seconds=5):
    rate=16000
    data=sd.rec(int(seconds*rate),samplerate=rate,channels=1,dtype='float32')
    sd.wait()
    f=tempfile.NamedTemporaryFile(suffix='.wav',delete=False); f.close()
    sf.write(f.name,data,rate,subtype='PCM_16')
    return f.name

def transcribe(path):
    key=os.getenv('OPENROUTER_API_KEY','')
    if not key: raise RuntimeError('OPENROUTER_API_KEY is missing')
    raw=open(path,'rb').read(); encoded=base64.b64encode(raw).decode()
    body={'model':os.getenv('PERCEPTION_MODEL','nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free'),'messages':[{'role':'user','content':[{'type':'text','text':'Transcribe this audio exactly. Return only the spoken words, no commentary.'},{'type':'input_audio','input_audio':{'data':encoded,'format':'wav'}}]}]}
    r=requests.post(OR_URL,headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},json=body,timeout=90)
    r.raise_for_status(); return r.json()['choices'][0]['message']['content'].strip()
