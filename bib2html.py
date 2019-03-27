#!/usr/bin/env python3
# Python script to convert BibTex entries to HTML code
# snippets.
#
# See LICENSE file for license and legal details

import sys
import argparse
import fileinput
import copy
import re
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
baseFields = ['author','title','url','available','accessed','year','publisher','pages','booktitle','volume']

              
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

              ${author}<i>${title}</i>${publisher}${year}. [Online]. ${url}${accessed}
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
              ${author}<i>${title}</it>
              </div>
              </div>
              ''',
              '@journal': \
              '''<div class="reference">
              <div>[${number}]
              </div>
              <div>
              ${author}<i>${title}</i>${booktitle}${volume}
              </div>
              </div>
              ''',
              '@techreport': \
              '''<div class="reference">
              <div>[${number}]
              </div>
              <div>
              ${author}<i>${title}</i>${publisher}${year}
              </div>
              </div>
              '''}

def swapNames(lst):
    for fullname in lst:
        names = fullname.split(',')
        for name in names:
            name.strip(' ')
        if len(names) > 1:
            temp = names[0]
            names = names[1:len(names)-1]
            names.append(temp)
            out = ""
            for name in names:
                out += name + ' '
            return out
        else:
            return names
    
def processAuthor(authors):
    ret = ""
    prepend = ""

    # return in single author name found
    # else, process list
    if ' ' not in authors:
        return authors
    else:
        lst = authors.split('and')
        if ',' in lst:
            swapNames(lst)
        for value in lst:
            author = value
            names = author.strip().split()
            for name in names:
                name = name.strip('{').strip('}')
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

def buildReferenceHTML(data):
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
            elif key == 'title' and \
              ref['data'][key] != '':
                ref['data'][key] = ref['data'][key].replace('{','').replace('}','')
                if ref['data']['author'] != '':
                    ref['data'][key] = ', ' + ref['data'][key]
            elif key == 'url':
              if ref['data'][key] != '':
                if 'url' in ref['data'][key]:
                    ref['data'][key] = ref['data'][key][3:]
                    ref['data'][key].strip('{}')
                ref['data'][key] = 'Available: <a href="' + ref['data'][key] + '">' + \
                                   ref['data'][key] + '</a> '
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
    
def buildHTML(body, data):
    doc = ""

    matcher = re.compile(r'(\$\{[a-zA-Z0-9:\.\-]*})')
    num = 0
    for line in body:
        match = matcher.search(line)
        while match:
            citation = match.groups()[0]
            #            print('citation= ', citation, end='')
            #            print(', match.groups()= ', match.groups())            
            key = citation.strip('$').strip('{}')
            (entry, id) = getEntry(key, data)
            if entry:
                line.replace(citation, '[' + str(id) + '] ')
            match = matcher.search(line)
            break
        num = num+1
        doc = doc + line + '\n'
    return doc

def getEntry(key, data):
    id = 1
    for entry in data:
        idStr = entry['id']
        if idStr.lower() == key.lower():
            return (entry, id)
        id = id + 1 
    return (None,None)
    
def buildList(inf):
    '''The function takes in a file or input stream
    and parses the file line by line building a
    List and returns the data structure.'''
  
    root = deque([])

    data = {}
    for line in inf:
        if line[0] == '@': # First line
            if '{' in line:
                type = line[:line.find('{')].strip().lower()
                id = line[line.find('{')+1:line.find(',')].strip()
        else:
            # end of record dependent on single '}' on line
            # TODO(Todd): fix
            if line.strip() == '}':
                entry = {'type':type,'id':id,'data':data}
                root.append(entry)
                data = {}
            else:
                kv = line.split('=')
                if len(kv) > 1:
                    kv[0] = kv[0].strip('\t\n{,} ')
                    kv[1] = kv[1].strip('\t\n{,} ')
                    if kv[0] != '' and kv[1] != None:
                        data[kv[0]] = kv[1]

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

    parser.add_argument('-ih', '--inputhtml', \
                        dest='inputHtml', \
                        help='Input HTML file.  If present, will modify ${<tag>} citations in html document.')
    parser.add_argument('-oh', '--outputhtml', \
                        dest='outputHtml', \
                        help='Output HTML file.  Must be present if option -ih, --inputHtml option present.')
    
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

    if args.inputHtml and not args.outputHtml or \
       not args.inputHtml and args.outputHtml:
        print('-ih and -oh are required together to process HTML input file.')
        exit()

    dt = buildList(inf)
    output = buildReferenceHTML(dt)
    
    outf.write(output)

    if args.inputHtml and args.outputHtml:
        try:
            inhf = open(args.inputHtml, 'r', encoding='utf8')
            print('Opened input HTML file: ', args.inputHtml)
        except:
            print('Failed to open HTML input file: ', args.inputHtml)
            exit()
        outputHtml = buildHTML(inhf, dt)

#        print(outputHtml)
        
        try:
            outhf = open(args.outputHtml, 'w+', encoding='utf-8')
            print('Opened output HTML file for writing: ', args.outputHtml)
        except:
            print('Failed to write HTML outut file: ', args.outputHtml)
            
        outhf.write(outputHtml)

