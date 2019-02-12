#!/usr/bin/env python3

# Python script to convert BibTex entries to HTML code
# snippets.
import sys
import argparse
import fileinput
from collections import deque
from string import Template

"""
Bibliography list and dictionary data store

root list
[ {entry_0}, {entry_1}, ... ]

entry dictionary
{
  id : string, # key
  type : string,
  fields : dictionary
    {
      // Depending on type
    }
}

"""

templates = { '@article': \
              '''<div style="display:flex">
              <div style="display:inline; padding-left: 10px; padding-right: 10px;">[${number}]
              </div>
              <div style="display:inline">
              ${author}<i>${title}</i>${journal}.
              </div>
              </div>''', \
              '@book' : \
              '''<div style="display:flex">
              <div style="display:inline; padding-left: 10px; padding-right: 10px;">[${number}]
              </div>
              <div style="display:inline">
              ${author}<i>${title}</i>${publisher}${year}.
              </div>
              </div>''', \
              '@online' : \
              '''<div style="display:flex">
              <div style="display:inline; padding-left: 10px; padding-right: 10px;">[${number}]
              </div>
              <div style="display:inline">
              ${author}<i>${title}</i>${publisher}${year}. [Online].
              </div>
              </div>''' }

def estrip(strng, char):
    if strng[:len(strng)-1] == char and len(strng) > 1:
        return strng[0:len(strng)-2]
    else:
        return strng
    
def processAuthor(authors):
    ret = ""
    prepend = ""
    
    lst = authors.split('and')
    for value in lst:
        author = value
        names = author.strip().split()
        modName = ""
        if names[0].lower() == 'others':
            modName = 'et al'
        else:
            for name in names[0:len(names)-1]:
                modName = name[0] + '. '
                modName = modName + names[len(names)-1]
        ret = ret + prepend + modName.strip()
        prepend = ', '
    ret = ret.strip()
    return ret

def buildHTML(data):
    header = '''<html>
<head>

</head>
<body>
<h1>References</h1>
'''
    footer = '''</body>
</html>
'''

    id = 1
    authors = ""
    body = ""
    for ref in data:
        print(ref)
        fields = ref['data']
        for key in fields:
            if key == 'author':
                 fields[key] = processAuthor(fields[key])
            else:
                if  fields[key] != "" or fields[key] != None:
                    fields[key] = ', ' + fields[key]
                    
        s = templates[ref['type'].lower()]
        if s != None:
            result = Template(s).safe_substitute(fields, number=str(id))
            body += result
            id += 1

    return header + '\n' + body + '\n' + footer
    

def buildAST(inf):
    '''The function takes in a file or input stream
    and parses the file line by line building an
    AST and returns the data structure.'''
  
    root = deque([])

    data = {}
    for line in inf:
        if line[0] == '@': # First line
            if '{' in line:
                type = line[:line.find('{')].strip()
                id = line[line.find('{')+1:line.find(',')].strip()
                print("type= " + type + ", id= " + id)
        else:
            if line == '}\n':
                entry = {'type':type,'id':id,'data':data}
                root.append(entry)
                data = {}
            else:
                if line.split() != []:
                    key = line.split()[0].strip(' ')
                    value = line[line.find('=')+1:]
                    value = value.replace('\t','')
                    value = value.replace('\n','')
                    value = value.strip(' ')
                    value = value.strip('{')
                    value = value.strip(',')
                    value = value.strip('}')
                    if value != '' or value != None:
                        data[key] = value
        
    return root
                

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='BibTex to HTML converter')
    parser.add_argument('-i', '--input', \
                        dest='inputFile', \
                        help='Input BibText file. If no option, uses stdin.', \
                        required=True)
    
    parser.add_argument('-o', '--output', \
                        dest='outputFile', \
                        help='Output HTML file. If no option, uses stdout.')
    
    args = parser.parse_args()
    if args.inputFile:
        try:
            inf = open(args.inputFile)
            print("Opened file: " + args.inputFile)
        except:
            print("Failed to open file: " + args.inputFile)
            exit()

    if args.outputFile:
        outf = open(args.outputFile, 'w+')
    else:
        outf = sys.stdout
        
    dt = buildAST(inf)
    print("dt= " + str(dt))
    testData=[{'id':'test01', \
               'type':'@Book', \
               'data':{ 'author':'Todd Saharchuk and Donald Seuss', \
                       'title':'I am I said so Sam: A Short Story', \
                        'publisher':'Dreaming Publishing, Inc.', 'year':'2019'}},
              {'id':'test02', \
               'type':'@Book', \
               'data':{ 'author':'Howard Duck and others', \
                        'title':'How to survive as a B character in Marvel.', \
                        'publisher':'Marvel Comics, Inc.', \
                        'year':'2000'}}]
    output = buildHTML(dt)
    outf.write(output)
