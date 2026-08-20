import os, json, requests
from tools import execute, SAFE_TOOLS

BASE='https://openrouter.ai/api/v1/chat/completions'
TOOLS=[
 {'type':'function','function':{'name':'open_application','description':'Open a Windows application or executable.','parameters':{'type':'object','properties':{'application':{'type':'string'}},'required':['application']}}},
 {'type':'function','function':{'name':'open_url','description':'Open a URL in the default browser.','parameters':{'type':'object','properties':{'url':{'type':'string'}},'required':['url']}}},
 {'type':'function','function':{'name':'get_active_window','description':'Get the current foreground window title.','parameters':{'type':'object','properties':{}}}},
 {'type':'function','function':{'name':'get_system_info','description':'Get CPU, RAM and battery status.','parameters':{'type':'object','properties':{}}}},
 {'type':'function','function':{'name':'type_text','description':'Type text into the active application.','parameters':{'type':'object','properties':{'text':{'type':'string'}},'required':['text']}}},
 {'type':'function','function':{'name':'press_key','description':'Press one keyboard key.','parameters':{'type':'object','properties':{'key':{'type':'string'}},'required':['key']}}},
 {'type':'function','function':{'name':'click','description':'Click a screen coordinate.','parameters':{'type':'object','properties':{'x':{'type':'integer'},'y':{'type':'integer'}},'required':['x','y']}}}
]

SYSTEM='''You are Mr Ayo, a Windows desktop AI agent. Be concise and practical. You can use tools to perform tasks. Never claim an action succeeded unless the tool returned success. For multi-step tasks, execute one step, inspect the result, then continue. Treat destructive or risky actions as confirmation-required. Return a short final response.'''

def ask(messages):
    key=os.getenv('OPENROUTER_API_KEY','')
    if not key: raise RuntimeError('OPENROUTER_API_KEY is missing. Put it in .env')
    payload={'model':os.getenv('BRAIN_MODEL','google/gemma-4-26b-a4b-it:free'),'messages':messages,'tools':TOOLS,'tool_choice':'auto','temperature':0.2}
    r=requests.post(BASE,headers={'Authorization':f'Bearer {key}','Content-Type':'application/json','X-Title':'Mr Ayo'},json=payload,timeout=90)
    if r.status_code >= 400:
        fallback=os.getenv('BRAIN_FALLBACK_MODEL','nvidia/nemotron-3-ultra-550b-a55b:free')
        payload['model']=fallback
        r=requests.post(BASE,headers={'Authorization':f'Bearer {key}','Content-Type':'application/json','X-Title':'Mr Ayo'},json=payload,timeout=90)
    r.raise_for_status(); return r.json()['choices'][0]['message']

def run_agent(user_text, send_state):
    messages=[{'role':'system','content':SYSTEM},{'role':'user','content':user_text}]
    for _ in range(8):
        send_state('thinking','Thinking','Planning the next step')
        msg=ask(messages); messages.append(msg)
        calls=msg.get('tool_calls') or []
        if not calls:
            return msg.get('content') or 'Done.'
        for call in calls:
            name=call['function']['name']; args=json.loads(call['function'].get('arguments') or '{}')
            level=SAFE_TOOLS.get(name,'restricted')
            if level!='safe':
                send_state('executing','Confirmation required',f'{name} needs your confirmation')
                # First MVP: do not execute confirmation-level actions automatically.
                result={'ok':False,'confirmation_required':True,'message':f'{name} requires explicit confirmation in the HUD.'}
            else:
                send_state('executing','Executing',name.replace('_',' '))
                result=execute(name,args)
            messages.append({'role':'tool','tool_call_id':call['id'],'content':json.dumps(result)})
    return 'I stopped after several steps to avoid running endlessly.'
