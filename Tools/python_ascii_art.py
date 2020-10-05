special = '\\\''

with open('art.txt', 'r') as f:
    print('print(')
    while True:
        line = f.readline()
        if not line:
            break
        line = line.rstrip()
        for i in range(len(line)):
            if i == 0:
                print('    \'', end='')
            if line[i] in special:
                print('\\', end='')
            print(line[i], end='')
            if i + 1 == len(line):
                print('\\n\'')
    print(')')
    f.close()
