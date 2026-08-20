import os, json, base64, subprocess, time, webbrowser, pyautogui, psutil
from PIL import ImageGrab

SAFE_TOOLS = {
    'open_application': 'safe', 'open_url': 'safe', 'get_active_window': 'safe',
    'get_system_info': 'safe', 'type_text': 'confirm', 'press_key': 'confirm',
    'click': 'confirm', 'take_screenshot': 'safe'
}

def execute(name, args):
    if name not in SAFE_TOOLS:
        return {'ok': False, 'error': 'Unknown tool'}
    try:
        if name == 'open_application':
            subprocess.Popen(args['application'], shell=True)
            return {'ok': True, 'message': f"Opened {args['application']}"}
        if name == 'open_url':
            webbrowser.open(args['url'])
            return {'ok': True, 'message': f"Opened {args['url']}"}
        if name == 'get_active_window':
            try:
                import win32gui
                return {'ok': True, 'title': win32gui.GetWindowText(win32gui.GetForegroundWindow())}
            except Exception:
                return {'ok': True, 'title': 'Windows active-window title unavailable'}
        if name == 'get_system_info':
            return {'ok': True, 'cpu_percent': psutil.cpu_percent(), 'ram_percent': psutil.virtual_memory().percent, 'battery': (psutil.sensors_battery().percent if psutil.sensors_battery() else None)}
        if name == 'type_text':
            pyautogui.write(args['text'], interval=0.01)
            return {'ok': True, 'message': 'Text typed'}
        if name == 'press_key':
            pyautogui.press(args['key'])
            return {'ok': True, 'message': f"Pressed {args['key']}"}
        if name == 'click':
            pyautogui.click(int(args['x']), int(args['y']))
            return {'ok': True, 'message': 'Clicked'}
        if name == 'take_screenshot':
            path = os.path.join(os.getcwd(), 'screen.png')
            ImageGrab.grab().save(path)
            return {'ok': True, 'path': path}
    except Exception as e:
        return {'ok': False, 'error': str(e)}
