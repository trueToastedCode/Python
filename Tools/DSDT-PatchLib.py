def is_none(str, msg=None):
    if str == None:
        if msg != None:
            print(msg)
        return True
    return False

# read file lines to list
def get_lines(fileName):
    file = open(fileName, 'r')
    lines = []
    while (True):
        line = file.readline()
        if not line:
            break
        lines.append(line.rstrip())
    file.close()
    return lines

def write_lines(lines, fileName):
    file = open(fileName, 'w')
    for line in lines:
        file.write(line + '\n')
    file.close()

# get space before firt character
def get_space(str):
    spaceCounter = 0
    for i in range(len(str)):
        if str[i] == ' ':
            spaceCounter += 1
        else:
            break
    return spaceCounter

# find line/s with string
def find(lines, str, lineStart=0, lineEnd=None, firstRes=True):
    # prepare list in case if not firstRes
    res = None
    if not firstRes:
        res = []

    for i in range(lineStart, len(lines)):
        if lineEnd is not None and i == lineEnd:
            break
        if str in lines[i]:
            # return or append founded line
            if firstRes:
                return i
            else:
                res.append(i)

    # return res or None if no res
    if res is None or len(res) == 0:
        return None
    else:
        return res

def find_in_parent(lines, str, parent, lineStart=0, lineEnd=None, firstRes=True):
    parentStart = find(lines, parent, lineStart, lineEnd, True)
    if is_none(parentStart, '\'' + parent + '\' not found!'):
        return

    parentEnd = find_end_clip(lines, parentStart)
    if is_none(parentStart, '\'' + parent + '\' not found!'):
        return

    return find(lines, str, parentStart, parentEnd, firstRes)

# find end clip to first founded open clip
def find_end_clip(lines, lineStart):
    clip = None
    for i in range(lineStart, len(lines)):
        if '{' in lines[i]:
            if clip is None:
                clip = 1
            else:
                clip += 1

        if '}' in lines[i]:
            if clip is None:
                return i
            clip -= 1

        if clip is None and i != len(lines)-1 and ('{' in lines[i+1]) is False:
            clip = 1

        if clip == 0:
            return i
    return None

# find open clip to line
def find_open_clip(lines, lineNum):
    clip = None
    for i in range(lineNum, -1, -1):
        if '}' in lines[i]:
            if clip is None:
                clip = 1
            else:
                clip += 1

        if '{' in lines[i]:
            if clip is None:
                return i
            else:
                clip -= 1

        if clip is None:
            clip = 1

        if clip == 0:
            return i
    return None

# add content to line
def add_content(lines, lineNum, content, space=0):
    print('Insert content in {} with space={}'.format(lineNum, space))

    if type(content) != list:
        content = [content]
    if space == 0:
        space = ''
    else:
        space = ' ' * space

    for i in range(len(content) - 1, -1, -1):
        lines.insert(lineNum, space + content[i])
    return lines

# replace content
def replace(lines, lineStart, lineEnd, replacement=None, space=True):
    if replacement != None and type(replacement) != list:
        replacement = [replacement]

    # find space
    if replacement is not None:
        if type(space) is bool:
            if space is True:
                for i in range(lineStart, lineEnd + 1):
                    if lines[i] != '':
                        space = get_space(lines[i])
                        break
                if type(space) is bool:
                    print('No space found!')
                    space = 0
            else:
                space = 0

    # delete lines
    x = lineEnd-lineStart+1
    for i in range(x):
        del lines[lineStart]

    # insert replacement
    if replacement != None:
        lines = add_content(lines, lineStart, replacement, space)

    return lines

# rename things
def rename(lines, before, after, missHex=True, log=False):
    outLines = []
    lineCounter = 1
    if missHex:
        for line in lines:
            lineAfter = line.replace(before, after);

            outLines.append(lineAfter)
            if log:
                if lineAfter != line:
                    print('[' + str(lineCounter) + '] ' + line + ' -> ' + lineAfter)
                lineCounter += 1
    else:
        lenBefore = len(before)
        for line in lines:
            hexCounter = 0
            replacements = []
            for i in range(0, len(line) - lenBefore + 1):
                if line[i:i + lenBefore] == before:
                    isHex = False
                    # check if character is in hex implemented
                    for x in range(i, -1, -1):
                        if line[x] == 'x':
                            hexCounter += 1
                            isHex = True
                        if line[x] == ' ' or isHex:
                            break

                    if isHex is False:
                        replacements.append(i)

            if len(replacements) == 0:
                outLines.append(line)
            else:
                lineAfter = ''
                start = 0
                for x in replacements:
                    if x == 0:
                        lineAfter += after
                    else:
                        lineAfter += line[start:x] + after
                    start = x+lenBefore
                lineAfter += line[start:]

                outLines.append(lineAfter)
                if log:
                    if lineAfter != line:
                        print('[' + str(lineCounter) + '] ' + line + ' -> ' + lineAfter + ' (Missed', hexCounter,
                              'hex/es)')
                    lineCounter += 1

    return outLines