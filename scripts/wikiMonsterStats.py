import json
from glob import glob

with open('version.txt','r',encoding='utf8') as f:
  lines = f.readlines()
  version = lines[0]

name_path_base = ''

type_paths = {
  'Deepist':['assets/data/monsters/cultist'],
  'Drauven':['assets/data/monsters/drauven'],
  'Gorgon':['assets/data/monsters/gorgon'],
  'Morthagi':['assets/data/monsters/morthagi'],
  'Thrixl':['assets/data/monsters/thrixl'],
  'Miscellaneous':['./assets/data/monsters/misc'],
  'Age of Ulstryx':['mods/builtIn/villain_ulstryx/assets/data/monsters/misc'],
  'The Enduring War':['mods/builtIn/villain_enduringWar/assets/data/monsters/morthagi','mods/builtIn/villain_enduringWar/assets/data/monsters/misc'],
  'Monarchs Under the Mountain':['mods/builtIn/villain_monarchs/assets/data/monsters/cultist'],
  'Eluna and the Moth':['mods/builtIn/villain_ecthis/assets/data/monsters/thrixl'],
  'All the Bones of Summer':['mods/builtIn/villain_cvawn/assets/data/monsters/drauven'],
  'The Sunswallower\'s Wake':['mods/builtIn/villain_vulture_lord/assets/data/monsters/misc'],
  }
  
names = {}
for m in (['.'] + glob('mods/builtIn/*')):
  name_file = m + '/assets/text/dynamic/dynamic.properties'
  try:
    with open(name_file,'r',encoding='utf8') as f:
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
        if len(key_split) != 2 or key_split[-1] != 'name':
          continue
        names[key_split[0]] = val[:-1]
  except:
    continue
  
diffs = {
  'Storyteller':'combatDifficulty_1',
  'Adventurer':'combatDifficulty_10',
  'Tragic Hero':'combatDifficulty_20',
  'Walking Lunch':'combatDifficulty_30',
  }

def read_stat(data,stat,diff):
  out = data['stats'][stat]
  try:
    out = data[diff]['stats'][stat]
  except:
    pass
  return out

for diff in list(diffs):
  
  d = diffs[diff]
  string = '[[Monster]] [[stat]]s at %s [[difficulty]] level:\n\n'%diff
  for faction in list(type_paths):
    string += '{| role="presentation" class="wikitable sortable mw-collapsible mw-collapsed" style="text-align: center"\n'
    string += '| style="width:880px" | ' + ("'''%s'''\n"%faction if faction=='Miscellaneous' else "'''[[%s]]'''\n"%faction)
    string += '|-\n'
    string += '|\n\n'
    string += '{| class="wikitable sortable" style="text-align: center"\n'
    string += '! ID !! Name !! [[Health]] !! [[Armor]] !! [[Warding]] !! [[Block]] + [[Dodge]] !! [[Speed]] !! [[Melee Accuracy]] !! [[Ranged Accuracy]]\n'
    for l in type_paths[faction]:
      for m in glob(l + '/*.json'):
        with open(m) as f:
          data = json.load(f)
          id = data['id']
          name = names[id]
          health = read_stat(data,'HEALTH',d)
          speed = read_stat(data,'SPEED',d)
          armor = read_stat(data,'ARMOR',d)
          warding = read_stat(data,'WARDING',d)
          block = read_stat(data,'BLOCK',d)
          dodge = read_stat(data,'DODGE',d)
          macc = read_stat(data,'MELEE_ACCURACY',d)
          racc = read_stat(data,'RANGE_ACCURACY',d)
          
          avoid = str(int(block)+int(dodge))
          string += '|-\n'
          string += '| <small>' + id + '</small> || [[' + name + ']] || ' + health + ' || ' + armor + ' || ' + warding + ' || ' + avoid + ' || ' + speed + ' || ' + macc + ' || ' + racc + '\n'
      
    string += '|}\n\n'
    string += '|}\n\n'
    
  string += '==Notes==\nLast updated [[%s]] using [[Monster stats/Script|this script]].\n'%version[:-1]
  
  with open('wikiMonsterStats_%s.txt'%diff, 'w') as f:
    f.write(string)