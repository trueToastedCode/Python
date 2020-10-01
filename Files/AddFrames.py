"""
- Do whatever  you want to do with this code -

command:
python AddFrames.py "(argument 0) scratch project file name" "(argument 1) folder name of frames" "(argument 2) frame name & %X formatter"

%X will replaces by the frame number
-> %X%X%X (and number 1 by the code) = 001

argument defaults:
-> If oyu write None, the code will leave the default valuer
0: Scratch-Projekt.sb3
1: ./frames/
2: frame%X%X%X.jpg

example:
1. python AddFrames.py MyProject.sb3 None frame.jpg
-> Code will format frame name in this case as frame%X.jpg

2. python AddFrames.py MyProject.sb3 None MyFrameName%X%X%X%X-OtherCharacters-.jpg
"""

import json
import random
import os
import shutil
import hashlib
import sys
import zipfile
from PIL import Image

config = {
    'file_s_project': 'Scratch-Projekt.sb3',
    'folder_temp': './temp/',
    'folder_frames': './frames/',
    'file_frame': 'frame%X%X%X.jpg'
}

def create_folder(path):
    os.mkdir(path)

lowercase_uppercase_digits = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def new_set(name):
    asset_id = ''.join(random.choice(lowercase_uppercase_digits) for i in range(8))
    asset_id = hashlib.md5((asset_id).encode('utf-8')).hexdigest()
    return {
        'assetId': asset_id,
        'name': name,
        'bitmapResolution': 2,
        'md5ext': asset_id + format,
        'dataFormat': format[1:],
        'rotationCenterX': width,
        'height': height
    }

if __name__ == '__main__':
    # set arguments
    switcher = {
        1: 'file_s_project',
        2: 'folder_frames',
        3: 'file_frame'
    }
    for i in range(1, len(sys.argv)):
        if i > 3:
            print(f'[!] Option \'{sys.argv[i]}\' is too much and will be ignored!')
            continue
        if sys.argv[i] != 'None':
            config[switcher.get(i)] = sys.argv[i]

    # check files and paths
    print('[Check paths]')
    for i, key in enumerate(config.keys()):
        print(config[key], end='')
        if not os.path.exists(config[key]):
            if key == 'folder_temp':
                create_folder(config[key])
            else:
                print(' FAIL')
                exit(1)
        elif key == 'folder_temp':
            # clean folder
            try:
                shutil.rmtree(config[key])
            except Exception as e:
                print(' FAIL')
                print(e)
                exit(1)
            create_folder(config[key])
        print(' OK')
        if i == 2:
            break

    # check frames
    print('\n[Check frame]')

    # format
    format = None
    x = None
    for i in range(len(config['file_frame'])-1, -1, -1):
        if config['file_frame'][i] == '.':
            x = i
            break
    if x is None:
        print('Invalid frame name: No format (f.x. .jpg)')
        exit(1)
    format = config['file_frame'][x:]
    config['file_frame'] = config['file_frame'][:x]
    print('format=' + format)

    # %X - format frame name
    z = -1
    start = y = 0
    i = x
    while i > 0:
        if config['file_frame'][i - 2:i] == '%X':
            y += 1
            if z == -1:
                end = i
                z = -2
        elif z == -2:
            start = i
            break
        i += z

    if y == 0:
        start = end = x
        y = 1

    config['file_frame'] = config['file_frame'][:start] + f'%0{y}d' + config['file_frame'][end:]
    print('frame name converted=' + config['file_frame'])

    # dimensions
    p = config['folder_frames'] + (config['file_frame'] % 0) + format
    if not os.path.exists(p):
        print(f'Error reading dimensions: {p} does not exist!')
        exit(1)
    with Image.open(p) as img:
        width, height = img.size
        img.close()
    print(f'dimension={width}x{height}')

    print('\n[Update project]')

    # extract scratch project
    with zipfile.ZipFile(config['file_s_project'], 'r') as zip_ref:
        print('Extracting Scratch project', end='')
        zip_ref.extractall(config['folder_temp'])
        zip_ref.close()
    print(' OK')

    # read project json
    print('Read project json', end='')
    with open(config['folder_temp'] + 'project.json', 'r') as f:
        data = json.load(f)
        f.close()
    sets = data['targets'][0]['costumes']
    print(' OK')

    # copy frames into temp scratch project
    print('Appending frames', end='')
    i = 0
    while True:
        name = config['file_frame'] % i
        if not os.path.exists(config['folder_frames'] + name + format):
            print(' OK')
            name = config['file_frame'] % (i-1)
            print(f'(Stopped at frame name {name})')
            break
        set = new_set(name)
        sets.append(set)
        shutil.copy(config['folder_frames'] + name + format, config['folder_temp'] + set['assetId'] + format)
        i += 1

    # update temp scratch project json
    print('Update json', end='')
    data['targets'][0]['costumes'] = sets
    with open(config['folder_temp'] + 'project.json', 'w') as f:
        json.dump(data, f, indent=2)
        f.close()
    print(' OK')

    # create new name
    new_name = None
    x = None
    for i in range(len(config['file_s_project'])-1, -1, -1):
        if config['file_s_project'][i] == '.':
            x = i
            break
    if x is None:
        x = len(config['file_s_project'])
    new_name = config['file_s_project'][:x] + '_Repacked.sb3'

    # zip project
    print('Packing temp Scratch project', end='')
    zf = zipfile.ZipFile(new_name, 'w', zipfile.ZIP_DEFLATED)
    src = os.path.abspath(config['folder_temp'])
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            zf.write(absname, arcname)
    zf.close()
    print(' OK')
