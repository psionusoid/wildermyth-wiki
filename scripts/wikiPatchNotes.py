string = '\n'
with open('change log.txt','r',encoding='utf8') as f:
  lines = f.readlines()
  
  start = True
  new = True
  for line in lines:
    if line.isspace():
      new = True
    
    try: 
      firstword = int(line.replace('.',' ').split(maxsplit=1)[0])
    except:
      firstword = None
    
    if (new and line[0].isdigit()) or (firstword is not None and 2000<firstword<2020):
      if not start:
        while string[-1].isspace():
          string = string[:-1]
        string += '</no' + 'wiki>\n'
        #string += '|}\n'
      else:
        start = False
      string += '== %s ==\n'%line[:-1]
      #string += '\n{| role="presentation" class="wikitable mw-collapsible mw-collapsed" style="text-align: left"\n'
      #string += "| '''Patch notes'''\n"
      #string += '|-\n|\n'
      string += ' <no' + 'wiki>'
      new = False
    else:
      string += line
  
  while string[-1].isspace():
    string = string[:-1]
  string += '</no' + 'wiki>\n'
  #string += '|}\n'

string += '\n<small>Updated using [[/Script|this script]].</small>'

with open('wikiPatchNotes.txt', 'w') as f:
  f.write(string)