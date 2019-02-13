#!/usr/bin/env python3
# Python script to convert BibTex entries to HTML code
# snippets.
#
# See LICENSE file for license and legal details

import sys
import argparse
import fileinput
import copy
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
baseFields = ['author','title','url','available','accessed','year','publisher','pages','booktitle']

              
templates = { '@article': \
              '''<div class="reference">
              <div>[${number}]
              </div>
              <div>
              ${author}<i>${title}</i>${journal}.
              </div>
              </div>''', \
              '@book' : \
              '''<div class="reference">
              <div>[${number}]
              </div>
              <div>
              ${author}<i>${title}</i>${publisher}${year}.
              </div>
              </div>''', \
              '@online' : \
              '''<div class="reference">
              <div>[${number}]
              </div>
              <div>
              ${author}<i>${title}</i>${publisher}${year}. [Online]. ${accessed}
              </div>
              </div>''', \
              '@inproceedings': \
              '''<div class="reference">
              <div>[${number}]
              </div>
              <div>
              ${author}<i>${title}</i>${publisher}${volume}${pages}${month}.
              </div>
              </div>''', \
              '@incollection': \
              '''<div class="reference">
              <div>[${number}]
              </div>
              <div>
              ${author}<i>${title}</i>${booktitle}${chapter}${publisher}${year}.
              </div>
              </div>''', \
              '@misc': \
              '''<div class="reference">
              <div>[${number}]
              </div>
              <div>
              ${author}<i>${title}</it>${}
              '''}

def processAuthor(authors):
    ret = ""
    prepend = ""

    # return in single author name found
    # else, process list
    if ' ' not in authors:
        return authors
    else:
        lst = authors.split('and')
        for value in lst:
            author = value
            names = author.strip().split()
            modName = ""
            try:
                if names != None and names[0].lower() == 'others':
                    modName = 'et al'
                else:
                    for name in names[0:len(names)-1]:
                        modName = name[0] + '. '
                        modName = modName + names[len(names)-1]
            except:
                pass
            ret = ret + prepend + modName.strip()
            prepend = ', '
        ret = ret.strip()
    return ret

def buildHTML(data):
    header = '''<html>
<head>
    <style>
    div.reference {
    display: flex;
    padding-top: 0.18em;
    padding-bottom: 0.18em;
    }
    div.reference div:nth-child(1) {
    display: block;
    tex-align: center;
    padding-right: 10px;
    padding-left: 10px;
    }
    div.reference div:nth-child(2) {
    display: block;
    text-align: left;
    }
    </style>
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
        for key in ref['data']:
            if key == 'author':
                ref['data'][key] = processAuthor(ref['data'][key])
            elif key == 'accessed' and \
                 ref['data'][key] != '':
                ref['data'][key] = "[Accessed: " + \
                                   ref['data'][key] + \
                                   "]"
            else:
                if  ref['data'][key] != "" and \
                    ref['data'][key] != None:
                    ref['data'][key] = ', ' + ref['data'][key]
                    
        s = templates[ref['type'].lower()]
        if s != None:
            result = Template(s).safe_substitute(ref['data'], number=str(id))
            body += result
            id += 1

    return header + '\n' + body + '\n' + footer
    

def buildList(inf):
    '''The function takes in a file or input stream
    and parses the file line by line building a
    List and returns the data structure.'''
  
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

    # This fix is temporary
    # TODO(Todd): Find a better way of handling
    # null parsed fields for template strings
    for entry in root:
        minimalFields = copy.deepcopy(baseFields)
        for key in entry['data']:
            if key in minimalFields:
                minimalFields.remove(key)
        for key in minimalFields:
            entry['data'][key] = ''
            
    
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
            inf = open(args.inputFile, 'r', encoding='utf8')
            print("Opened file: " + args.inputFile)
        except:
            print("Failed to open file: " + args.inputFile)
            exit()

    if args.outputFile:
        outf = open(args.outputFile, 'w+', encoding='utf8')
    else:
        outf = sys.stdout
        
    dt = buildList(inf)
    output = buildHTML(dt)
    outf.write(output)
