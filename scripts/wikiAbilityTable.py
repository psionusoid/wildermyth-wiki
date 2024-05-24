import json
from glob import glob
import re

aspect_directory = 'assets/data/aspects'
text_file = 'assets/text/aspects/aspects.properties'

# make dictionary of localized names

aspectNames = {}
aspectBlurbs = {}
with open(text_file,'r',encoding='utf8') as f:
  lines = f.readlines()
  for line in lines:
    if line[0] == '#':
      continue
    try:
      key,val = line.split('=')
    except:
      continue
    try:
      key_split = key.split('.')
    except:
      continue
    if len(key_split) == 2 and key_split[-1] == 'name':
      aspectNames[key_split[0]] = val[:-1]
    elif len(key_split) == 2 and key_split[-1] == 'blurb':
      aspectBlurbs[key_split[0]] = val[:-1]

# read game version

with open('version.txt','r',encoding='utf8') as f:
  lines = f.readlines()
  version = lines[0]

# make list of abilities, by deck

decks = {'common':[],'warrior':[],'hunter':[],'mystic':[],'upgrade':[]}

aspectfiles = glob(aspect_directory + '/*')
for file in aspectfiles:
  with open(file) as f:
    data = json.load(f)
    for entry in data:
      for deck in decks:
        if entry.get('info', {}).get('abilityDeckUsage') == deck:
          decks[deck] += [entry]

# move upgrades to other deck, if they upgrade that deck's ability

upgrades = []
for entry in decks['upgrade']:
  upgradeFor = entry.get('info', {}).get('upgradeForAbility')
  if upgradeFor is not None:
    for deck in decks:
      for base in decks[deck]:
        if base['id'] == upgradeFor:
          decks[deck] += [entry]
          break
      else:
        continue
      break
    else:
      upgrades += [entry]
  else:
    upgrades += [entry]
    
decks['upgrade'] = upgrades

# sort ability decks by localized name

for deck in decks:
  decks[deck] = sorted(decks[deck], key=lambda d: aspectNames[d['id']]) 

# wiki blurb for each deck

deck_blurbs = {
  'common':'=== General Abilities ===\nThese abilities are available to all heroes.\n',
  'warrior':'=== Warrior Abilities ===\nThese abilities are only available to [[Warrior]]s.\n',
  'hunter':'=== Hunter Abilities ===\nThese abilities are only available to [[Hunter]]s.\n',
  'mystic':'=== Mystic Abilities ===\nThese abilities are only available to [[Mystic]]s.\n',
  'upgrade':'=== Theme Upgrades ===\nThese upgrades require specific [[theme]]s.',
  }

# function to replace [tag]...[] or [tag]...[tag]
# with new...new, while respecting nested brackets

def replace_tag(tag,new,string):
  while True:
    start = string.find('[%s]'%tag)
    if start < 0:
      break
    num = 1
    for j in re.finditer(r'\[.*?\]',string[start+len(tag)+2:]):
      tag_ = string[start+len(tag)+2+j.start():start+len(tag)+2+j.end()][1:-1]
      if tag_ not in ['',tag]:
        num += 1
      else:
        num -= 1
      if num == 0:
        end = start+len(tag)+2+j.end()
        string = string[:start] + new + string[start+len(tag)+2:end-2-len(tag_)] + new + string[end:]
        break
  return string

# function to replace <a/b/.../y:aa/bz/.../yy/zz> with zz

def fail_condition(string):
  for opentag in ['<self.','<test:','<mf']:
    while True:
      start = string.find(opentag)
      if start < 0:
        break
      num = 1
      slashes = []
      passed_colon = False
      for i,c in enumerate(string[start+len(opentag):]):
        if c == '<':
          num += 1
        elif c == '>':
          num -= 1
          if num == 0:
            end = i+start+len(opentag)+1
            break
        elif c == '/' and num == 1 and passed_colon:
          slashes += [i+start+len(opentag)]
        elif c == ':':
          passed_colon = True
      if len(slashes) == 0:
        slashes += [end-1]
      string = string[:start] + string[slashes[-1]+1:end-1] + string[end:]
  return string

# list of words to replace with links in the wiki

linkwords = {
  'Bonus Damage':None,
  'Spell Damage':None,
  'Potency':None,
  'Stunt Chance':None,
  'Temp Health':None,
  'Temporary Health':None,
  'Armor':'Armor (Stat)',
  'Warding':None,
  'Dodge':None,
  'Block':None,
  'Speed':None,
  'Recovery Rate':None,
  'Retirement Age':None,
  'Grayplane':None,
  'bonus damage':None,
  'spell damage':None,
  'armor':'Armor (Stat)',
  'warding':None,
  'dodge':None,
  'block':None,
  'augment':None,
  'grayplane':None,
  'hidden':None,
  }

# function to turn game-formatted ability blurb into wiki-formatted ability blurb

def parse(blurb):
  out = blurb
  
  out = replace_tag('b',"'''",out) # bold -> bold
  out = replace_tag('blue',"",out) # blue -> plain
  out = replace_tag('gray',"",out) # gray -> plain
  
  out = out.replace('<self>','Hero')
  out = out.replace('<name>','Hero')
  
  # assume any requirements are not met
  out = fail_condition(out)
  
  ### TODO: rewrite these to appropriately respect nested brackets and braces
  
  out = re.sub(r'\<int:(.*?)\>', 'x', out) # formula -> x
  out = re.sub(r'\<float:(.*?)\>', 'x', out) # formula -> x
  
  # status effect -> link
  out = re.sub(r'\[:statusEffect\.(.*?)\](.*?)\[\]', '[[\g<1>|\g<2>]]', out)
  out = re.sub(r'\[statusEffect:(.*?)\](.*?)\[\]', '[[\g<1>|\g<2>]]', out)
  
  # leave out "(Currently ...)" note which is based on hero's current stats
  out = re.sub(r'\(Current.*?\)', '', out)
  
  ### ---
  
  out = out.replace('\\n','<br />') # newline -> newline
  
  for word in linkwords: # replace words with links
    if linkwords[word] is not None:
      out = re.sub(r'(^|[^\[])' + word + r'($|[^\]])','\g<1>[[%s|%s]]\g<2>'%(linkwords[word],word),out)
    else:
      out = re.sub(r'(^|[^\[])' + word + r'($|[^\]])','\g<1>[[%s]]\g<2>'%(word),out)
  return out

# build output string

string = ''

for deck in decks:
  
  # add deck blurb
  string += deck_blurbs[deck]
  
  # add table headings
  if deck != 'upgrade':
    string += '\n{| class="wikitable"\n! Name\n! Description\n|-\n'
  else:
    string += '\n{| class="wikitable sortable"\n! Name\n! Requirement\n! Description\n|-\n'
    
  # add ability lines
  for entry in decks[deck]:
    
    # add name
    name = aspectNames[entry['id']]
    if name[-1] == '+':
      nameStr = '[[' + name[:-1] + ']]+'
    else:
      nameStr = '[[' + name + ']]'
    nameStr = nameStr.replace('/',']]/[[')
    string += '| %s\n'%(nameStr)
    
    # add requirements
    if deck == 'upgrade':
      requirements = []
      themes = []
      legs = {}
      arms = {}
      for req in entry.get('abilityRequiresOneAspectOf'):
        requirements += [req]
        
        # get associated info
        theme = None
        if req.startswith('themePiece_'):
          theme = 'theme_' + req.split('_')[1]
          if req.endswith('leftArm') or req.endswith('rightArm'):
            if arms.get(theme): arms[theme] += 1
            else: arms[theme] = 1
          if req.endswith('leftLeg') or req.endswith('rightLeg'):
            if legs.get(theme): legs[theme] += 1
            else: legs[theme] = 1
        elif req.startswith('theme_'):
          theme = req
        themes += [theme]
      
      # start requirement string
      reqStr = ''
      
      # only precede with theme if there is only one
      onlyTheme = None
      if len(set(themes)) == 1 and themes[0] is not None:
        reqStr += '[[%s]]'%aspectNames[themes[0]]
        onlyTheme = themes[0]
      
      # compress requirements
      reqs = []
      for i,req in enumerate(requirements):
        
        # if requirement = theme, don't repeat it
        if onlyTheme is not None and req == onlyTheme:
          continue
        
        # combine 2 arms
        if (req.endswith('leftArm') or req.endswith('rightArm')) and arms[themes[i]] != 1:
          if arms.get(themes[i]) >= 2:
            reqname = re.sub(r' \([LR]\)', '', aspectNames[req])
            arms[themes[i]] = -1
          elif arms.get(themes[i]) < 0:
            continue
        
        # combine 2 legs
        elif (req.endswith('leftLeg') or req.endswith('rightLeg')) and legs[themes[i]] != 1:
          if legs.get(themes[i]) >= 2:
            reqname = re.sub(r' \([LR]\)', '', aspectNames[req])
            legs[themes[i]] = -1
          elif legs.get(themes[i]) < 0:
            continue
        
        else:
          reqname = aspectNames[req]
        
        # requirements don't need to link if the theme already will
        if onlyTheme is None:
          reqs += ['[[%s|%s]]'%(aspectNames[themes[i]],reqname)]
        else:
          reqs += ['%s'%(reqname)]
      
      # join requirements into our string
      if len(reqs) > 0:
        reqStr += ': '
        reqStr += ' or '.join(reqs)
      string += '| %s\n'%(reqStr)
    
    # add blurb
    blurb = aspectBlurbs[entry['id']]
    string += '| %s\n|-\n'%parse(blurb)
  
  # close table
  string += '|}\n'
  string += '<small>Last updated [[%s]] using [[/Script|this script]].</small>\n'%version[:-1]
  
# write the final string

with open('wikiAbilityTable.txt', 'w') as f:
  f.write(string)
