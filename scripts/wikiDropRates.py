import json as json
from glob import glob
import math

### data from the compiled code -- must be updated manually

artifactSpawnChanceDecreasePerSuccess = 0.5
artifactSpawnChanceIncreasePerFailure = 0.15

itemWeights = {
  'weapon':0.3,
  'armor':0.31,
  'augment':0.4,
  'offHand':0.1,
  }

weaponWeights = {
  'sword':1.0,
  'axe':1.0,
  'spear':1.0,
  'mace':1.0,
  'bow':1.5,
  'crossbow':0.8,
  'dagger':0.7,
  'staff':1.0,
  'wand':0.8,
  }

armorWeights = {
  'warriorArmor':4.0,
  'hunterArmor':3.0,
  'mysticArmor':2.0,
}

rootNames = {
  'weapon':'Weapon',
  'armor':'Armor',
  'augment':'Augment',
  'offHand':'Off Hand',
  }

armorNames = {
  'warriorArmor':'Warrior Armor',
  'hunterArmor':'Hunter Armor',
  'mysticArmor':'Mystic Armor',
  }

weaponTier = lambda chapter: max(1,math.ceil(chapter / 2.0))
armorTier = lambda chapter: max(1,math.ceil(chapter / 3.0))

###

with open('version.txt','r',encoding='utf8') as f:
  lines = f.readlines()
  version = lines[0]

###

namePath = 'assets/text/dynamic/dynamic.properties'

itemNames = {}
categoryNames = {}
with open(namePath,'r',encoding='utf8') as f:
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
    if len(key_split) == 2 and key_split[0] == 'item':
      itemNames[key_split[1]] = val[:-1]
    elif len(key_split) == 2 and key_split[0] == 'itemTypeDescriptiveNameUpper':
      categoryNames[key_split[1]] = val[:-1]

###

itemPath = 'assets/data/items/items'
itemList = {}
categoryDividend = {}

for itemFile in glob(itemPath + '/*.json'):
  try:
    with open(itemFile) as f:
      data = json.load(f)
      try:
        ident = data['uniqueCategory']
      except:
        continue
      try:
        name = itemNames[ident]
      except:
        continue
      category = data.get('category')
      if data.get('onlySpawnById'):
        continue
      if category not in itemList:
        itemList[category] = {}
      if ident not in itemList[category]:
        itemList[category][ident] = name
        if category not in categoryDividend:
          categoryDividend[category] = 1
        else:
          categoryDividend[category] += 1
  except Exception as e:
    print(itemFile,e)
    
###

rootTable = '''
{| class="wikitable" style="text-align: center"
! rowspan=2 | Item type !! rowspan=2 | Relative<br />drop rate !! colspan=5 | Tier
|-
! Chapter 1 !! Chapter 2 !! Chapter 3 !! Chapter 4 !! Chapter 5
'''

for cat in itemWeights:
  line = '|-\n| [[%s]] || %s '%(rootNames[cat],str(itemWeights[cat]))
  if cat == 'weapon':
    line += ''.join(['|| %d '%weaponTier(c) for c in range(1,6)])
  elif cat == 'armor':
    line += ''.join(['|| %d '%armorTier(c) for c in range(1,6)])
  else:
    line += ''.join(['|| ' for c in range(5)])
  line += '\n'
  rootTable += line
rootTable += '|-\n|}\n'

###

weaponCatTable = '''
{| class="wikitable sortable" style="text-align: center"
! Weapon type !! Relative drop rate
'''
for cat in weaponWeights:
  line = '|-\n| %s || %s \n'%(categoryNames[cat],str(weaponWeights[cat]))
  weaponCatTable += line
weaponCatTable += '|-\n|}\n'

###

armorCatTable = '''
{| class="wikitable" style="text-align: center"
! Armor type !! Relative drop rate
'''
for cat in armorWeights:
  line = '|-\n| %s || %s \n'%(armorNames[cat],str(armorWeights[cat]))
  armorCatTable += line
armorCatTable += '|-\n|}\n'

###

weaponTable = '''
{| class="wikitable sortable" style="text-align: center"
! Name !! Type !! Effective drop rate
'''
for cat in weaponWeights:
  for weapon in itemList[cat]:
    line = '|-\n| [[%s]] || %s || %.3f \n'%(itemList[cat][weapon],categoryNames[cat],weaponWeights[cat]/categoryDividend[cat])
    weaponTable += line
weaponTable += '|-\n|}\n'

###

string = ''

string += '''
== Item types ==

When generating a random item drop, the game first chooses the type of item. The relative chance of getting each item type is given in the following table. However, a given item drop source may not allow every possible type. For weapons and armor, the tier depends on the chapter and is also given in the table.
'''
string += rootTable

string += '''
If a [[weapon]] drops, the relative odds of each type of weapon are as follows:
'''
string += weaponCatTable

string += '''
If instead a piece of [[armor]] drops, the relative odds of each class are as follows:
'''
string += armorCatTable

string += '''
== Artifacts ==

If weapon is selected to drop, there is a chance that it will be an [[artifact]] weapon. The chance starts at 0, increases by %s each time a non-artifact weapon drops, and decreases by %s each time an artifact weapon drops. The following artifacts can appear as random drops. Each artifact of a given type is equally likely to drop. Accordingly, the table lists each artifact's effective drop rate, which is calculated as the weapon type's relative drop rate divided by the number of droppable artifacts of that type.
'''%(artifactSpawnChanceIncreasePerFailure,artifactSpawnChanceDecreasePerSuccess)
string += weaponTable
string += '''
An artifact will not drop if a hero in the campaign already possesses it. This behavior can raise the effective drop rate of other artifacts of the same type.
'''

string += '\n==Notes==\nLast updated [[%s]] using [[/Script|this script]].\n'%version[:-1]

with open('wikiDropRates.txt', 'w') as f:
  f.write(string)