import ctypes
import os
import winreg
import re
import vdf #use vdf folder inside branch or use 'pip install vdf' in cmd

def read_reg(ep: str, p = r'', k = '') -> str: #searches and return k inside ep/p
    try:
        key = winreg.OpenKeyEx(ep, p)
        value = winreg.QueryValueEx(key,k)
        if key:
            winreg.CloseKey(key)
        return str(value[0])
    except Exception:
        raise RuntimeError("Steam folder not found in regestry")

def find_screensize() -> tuple: #findes screensize of main display
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screensize

def change_res(path) -> None: #changes resolution in config file
    path = path + r'\steamapps\common\Underlords\game\dac\cfg\video.txt'
    if not os.path.exists(path):
        raise RuntimeError("Config file not found")
    screensize = find_screensize()
    
    with open(path, 'r+') as file:
        file_text = file.read()
        file_text = re.sub(r'("setting\.defaultres"\s+)"\d+"', r'\g<1>"{}"'.format(screensize[0]), file_text)
        file_text = re.sub(r'("setting\.defaultresheight"\s+)"\d+"', r'\g<1>"{}"'.format(screensize[1]), file_text)
        file.seek(0)
        file.write(file_text)
    return

def find_game_path(path: str, appID: str) -> str: #trying to find the path_to_game in vdf files
    d = vdf.load(open(path))
    d = vdf.parse(open(path))

    for i in range(len(d['libraryfolders'])):
        if appID in d['libraryfolders'][str(i)]['apps']:
            return( d['libraryfolders'][str(i)]['path'])
            
            

DU_id = '1046930' #appID of Dota Underlords
SteamPath = read_reg(ep = winreg.HKEY_LOCAL_MACHINE, p = r'SOFTWARE\Wow6432Node\Valve\Steam', k = 'InstallPath') #searches Steam path in regestry
if not os.path.exists(SteamPath+r'\steam.exe'):
    raise RuntimeError("Steam folder isn't exist")

if os.path.exists(SteamPath+r'\steamapps\common\Underlords\game\bin\win64\underlords.exe'): #searches game in Steam folder
    change_res(SteamPath)
else: #trying to find game in other folders
    LFconfig = SteamPath+r'\config\libraryfolders.vdf'
    LFapps = SteamPath+r'\steamapps\libraryfolders.vdf'
    
    if os.path.exists(LFconfig) and os.path.exists(find_game_path(LFconfig, DU_id)+r'\steamapps\common\Underlords\game\bin\win64\underlords.exe'): 
        new_path = find_game_path(LFconfig, DU_id)
        change_res(new_path)
    elif os.path.exists(LFapps) and os.path.exists(find_game_path(LFapps, DU_id)+r'\steamapps\common\Underlords\game\bin\win64\underlords.exe'):
        new_path = find_game_path(LFapps, DU_id)
        change_res(new_path)
    else:
        raise RuntimeError("Dota Underlords folder not found")

os.system('cmd /c start steam://run/'+DU_id) #executes game