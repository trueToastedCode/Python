import os
import re
import pyperclip


def is_extension(filename, extension):
    return True if re.search(f'\.{extension}$', filename.lower()) else False


def gen_exports(path, prepath):
    str = ''
    for root, dirs, files in os.walk(path):
        for file in files:
            if is_extension(file, 'dart'):
                str += f'export \'package:{prepath}{root[len(path):]}/{file}\';\n'
    return str


text = gen_exports('/Users/lennard/StudioProjects/teacherrate/teacherratemodule/lib/src', 'teacherratemodule/src')
pyperclip.copy(text)
