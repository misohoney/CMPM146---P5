import json
from heapq import heappush, heappop
from collections import namedtuple
with open('Crafting.json') as f:
   Crafting = json.load(f)

# List of items that can be in your inventory:
print "Items:", Crafting['Items']
# example: ['bench', 'cart', ..., 'wood', 'wooden_axe', 'wooden_pickaxe']

# List of items in your initial inventory with amounts:
print "Inventory:", Crafting['Initial']
# {'coal': 4, 'plank': 1}

# List of items needed to be in your inventory at the end of the plan:
# (okay to have more than this; some might be satisfied by initial inventory)
print "Goal:", Crafting['Goal']
# {'stone_pickaxe': 2}

# Dict of crafting recipeDict (each is a dict):
#print Crafting['Recipes']['craft stone_pickaxe at bench']
# example:
# { 'Produces': {'stone_pickaxe': 1},
#   'Requires': {'bench': True},
#   'Consumes': {'cobble': 3, 'stick': 2},
#   'Time': 1
# }
   
def make_checker(rule):
   consumes = []
   requires = []
   if 'Consumes' in rule:
      consumes = [(item,rule['Consumes'][item]) for item in rule['Consumes']]
   if 'Requires' in rule:
      requires = [item for item in rule['Requires'].keys()]
   produce = [(item,rule['Produces'][item]) for item in rule['Produces']]
   def check(state):
      for i,a in produce:
         if recipeDict[i] == 0:
             return False
         if i in state:
            if state[i] >= recipeDict[i]:
                return False
      for each in requires:
         if each not in state:
            return False
      for each,amount in consumes:
         if each not in state:
            return False
         else:
            if (state[each] < amount):
               return False
      return True
   return check

def make_effector(rule):
   consumes = []
   produce = []
   if 'Consumes' in rule:
      consumes = [(item,rule['Consumes'][item]) for item in rule['Consumes']]
   if 'Produces' in rule:
        produce = [(item,rule['Produces'][item]) for item in rule['Produces']]
   def effect(state):
      returnstate = state.copy()
      for i,a in consumes:
         returnstate[i] -= a
      for i,a in produce:
         if not i in state:
            returnstate[i] = 0
         returnstate[i] += a
      return returnstate
   return effect

def search(graph,initial,is_goal):
   #the amount of goal object
   for each, amount in Crafting['Goal'].items():
       recipeDict[each] = amount
       #print "amount", amount, each, "recipe", recipeDict[each]
   num = 1
   craftPath = []
   if is_goal(initial):
      return
   else:
      inventory = initial
      adjlist = graph(inventory)
      lookat = []
      for steps in adjlist:
        heappush(lookat, (steps[2], steps, craftPath))
        #print "lookat:", lookat, "steps[2]:", steps[2], "steps:", steps, "craftPath", craftPath
      while len(lookat) > 0:
         curr = lookat.pop(0)
         #print "curr:", curr
         copyPath = []
         for items in curr[2]:
            copyPath.append(items)
         if is_goal(curr[1][1]):
            curr[2].append((curr[1][0], curr[1][1]))
            print ""
            print "BEGIN PROCESS", Crafting['Goal'] 
            print ""
            for items in curr[2]:
                print  "Step", num, ":", items
                num = num + 1
            print ""
            print "FINISHED", Crafting['Goal']
            print ""
            return
         num = 1
         adjlist = graph(curr[1][1])
         copyPath.append((curr[1][0], curr[1][1]))
         heu = steps[2] + curr[0] - 4
         for steps in adjlist:
            heappush(lookat, (heu, steps, copyPath))
      return
   
def graph(state):
   for r in all_recipes:
      if r.check(state):
         yield (r.name, r.effect(state), r.cost, state.copy())

#function to identify if items is already there/made
def is_goal(state):
   for item, amount in Crafting['Goal'].items():
      if item in state:
         if state[item] < amount:
            return False
      else:
         return False
   return True

#function to add all info to recipeDict 
def buildDict():
   #set all value of crafting items to 0
   print ""
   print "RECIPES:"
   print ""
   for items in Crafting['Items']:
       recipeDict[items] = 0
       #print items
   #check all the rules in recipeDict
   for action,rule in Crafting['Recipes'].items():
       print "Action:", action
       print "Rule:", rule
       #If there is requirements in rule 
       #set numbers of required item to 1
       if 'Requires' in rule:
           for each in rule["Requires"].keys():
               recipeDict[each] = 1
               print "Requires", each, recipeDict[each]
       #If there is Consumes found in rule
       #set the amount of Consumes items to the largest number found
       if 'Consumes' in rule:
           for each,amount in rule['Consumes'].items():
               if recipeDict[each] < amount:
                   recipeDict[each] = amount
                   print "Consumes", each, recipeDict[each]
       print ""


   #items that are not in requires or consumes to craft other objects
   recipeDict[u'wooden_axe'] = 0
   recipeDict[u'stone_axe'] = 0
   recipeDict[u'iron_axe'] = 0
   recipeDict[u'iron_pickaxe'] = 0
   print "RECIPES END"
   print ""


Recipe = namedtuple('Recipe',['name','check','effect','cost'])
all_recipes = []
recipeDict = {} #store all the recipeDict information
action = {}
buildDict() #build a dict of crafting recipeDict
for name, rule in Crafting['Recipes'].items():
   checker = make_checker(rule)
   effector = make_effector(rule)
   recipe = Recipe(name, checker, effector, rule['Time'])
   all_recipes.append(recipe)

search(graph,Crafting['Initial'],is_goal)