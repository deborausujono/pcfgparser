fout = open('tst.parse.gld', 'w')
fin = open('tst1.parse.gld', 'r')

out = ''
lines = fin.readlines()
for line in lines:
    if line == '\n': out += line
    else:
        line = line.replace('\n', '')
        out += line

fout.write(out)
