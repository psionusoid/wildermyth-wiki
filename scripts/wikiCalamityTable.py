import json
from glob import glob

deck_file = 'assets/data/generation/monsterDecks.json'
name_file = 'assets/text/dynamic/dynamic.properties'
  
monsterNames = {}
cardNames = {}
flavorNames = {}
cardNumbers = {}
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
    if len(key_split) == 2 and key_split[-1] == 'name':
      monsterNames[key_split[0]] = val[:-1]
    elif len(key_split) == 2 and key_split[0] == 'monsterCardName':
      cardNames[key_split[-1]] = val[:-1]
    elif len(key_split) == 2 and key_split[1] == 'plural':
      flavorNames[key_split[0]] = val[:-1]
    elif len(key_split) == 3 and key_split[0] == 'monsterCard' and key_split[1] == 'nameFormula':
      cardNumbers[int(key_split[2])] = val[4:-1]

with open('version.txt','r',encoding='utf8') as f:
  lines = f.readlines()
  version = lines[0]
string = ''

def add_entry(card_list,flavor,i,entry):
  try:
    card_list[flavor][i] += [entry]
  except:
    card_list[flavor] += [[] for _ in range(i-len(card_list[flavor])+1)]
    card_list[flavor][i] += [entry]

card_list = {}
max_cards = 0 # per faction
with open(deck_file) as f:
  data = json.load(f)
  for i in range(len(data)):
    flavor = flavorNames[data[i]['groupFlavor']]
    tracks = data[i]['tracks']
    card_list[flavor] = []
    for j in range(len(tracks)):
      cardName = cardNames[tracks[j]['name']]
      cards = tracks[j]['cards']
      for k in range(len(cards)):
        monsters = [monsterNames[c] for c in cards[k]]
        if k == 0:
          if 'onlyIfFlavorHasCards' in tracks[j]:
            add_entry(card_list,flavor,tracks[j]['onlyIfFlavorHasCards'],{'name':cardName,'numeral':cardNumbers[k],'cards':monsters,'count':k+1,'position':j})
            max_cards = max(tracks[j]['onlyIfFlavorHasCards'],max_cards)
          else:
            add_entry(card_list,flavor,0,{'name':cardName,'numeral':cardNumbers[k],'cards':monsters,'count':k+1,'position':j})
        else:
          if 'trackAdvanceThresholds' in tracks[j]:
            add_entry(card_list,flavor,tracks[j]['trackAdvanceThresholds'][k-1],{'name':cardName,'numeral':cardNumbers[k],'cards':monsters,'count':k+1})
            max_cards = max(tracks[j]['trackAdvanceThresholds'][k-1],max_cards)
          else:
            pass

string = 'Many [[calamity]] cards introduce new [[monster]]s or increase the number of monsters that spawn within a [[mission]]. '
string += 'These cards can only be drawn if the associated [[faction]] holds a number of calamity cards that meets or exceeds some threshold. '
string += 'In this way, each faction has a [[calamity track]] consisting of successively more dangerous cards.\n'
string += '==Table==\n'
string += 'If drawn within a [[mission]], each card typically generates a number of the specified monster equal to the card\'s roman numeral. '
string += 'There are some exceptions, which are noted in the table. '
string += 'Also, \'\'italicized\'\' cards are not drawn as [[calamity]] cards but are instead available from a campaign\'s outset.\n'
string += '{| class="wikitable" style="text-align: center"\n'
string += '! Threshold<br>cards !! [[%s]] !! [[%s]] !! [[%s]] !! [[%s]] !! [[%s]]\n'%tuple(card_list)

for i in range(max_cards+1):
  string += '|-\n'
  string += '| %d '%i
  for flavor in list(card_list):
    string += '|| '
    try:
      for j,card in enumerate(card_list[flavor][i]):
        if j > 0:
          string += '<br>'
        if 'position' in card and card['position'] < 2:
          string += "''"
        string += '[[%s|%s]] %s'%(card['cards'][0],card['name'],card['numeral'])
        if 'position' in card and card['position'] < 2:
          string += "''"
        if len(set(card['cards'])) > 1 or len(card['cards']) != card['count']:
          string += '<ref>'
          for k,c in enumerate(set(card['cards'])):
            if k > 0: string += ', '
            string += '%d %s'%(card['cards'].count(c),c)
          string += '</ref>'
    except IndexError:
      pass
  string += '\n'
string += '|}\n\n'
string += '==Notes==\n'
string += 'Last updated [[%s]] using [[/Script|this script]].\n'%version[:-1]
  
with open('wikiCalamityTable.txt', 'w') as f:
  f.write(string)