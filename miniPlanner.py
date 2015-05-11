import json
from heapq import heappush, heappop
from collections import namedtuple
with open('crafting.json') as f:
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

# Dict of crafting recipes (each is a dict):
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
      checkflag = True
      for i,a in produce:
         if maxInv[i] == 0:
             checkflag = False
         if i in state:
            if state[i] >= maxInv[i]:
                checkflag = False
      for each in requires:
         if each not in state:
            checkflag = False
      for each,amount in consumes:
         if each not in state:
            checkflag = False
         else:
            if (state[each] < amount):
               checkflag = False
      return checkflag
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
   num = 1
	# print out how many of each item you can have
   mining = []
   if is_goal(initial):
      return
   else:
      inventory = initial
      adjlist = graph(inventory)
      lookat = []

      for steps in adjlist:
        heappush(lookat, (steps[2], steps, mining))

      while len(lookat) > 0:
         curr = lookat.pop(0)
         mining1Copy = []
         for items in curr[2]:
            mining1Copy.append(items)
         if is_goal(curr[1][1]):
            curr[2].append((curr[1][0], curr[1][1]))
            print ""
            print "BEGIN MINING AND CRAFTING", Crafting['Goal'] 
            for items in curr[2]:
                print  "Step", num, ":", items
                num = num + 1
            print "FINISHED CRAFTING", Crafting['Goal']
            print ""
            return
         num = 1
         adjlist = graph(curr[1][1])
         mining1Copy.append((curr[1][0], curr[1][1]))
         heu = steps[2] + curr[0] - 4
         for steps in adjlist:
         	heappush(lookat, (heu, steps, mining1Copy))
      return
   
def make_graph(state):
	for r in all_recipes:
		if r.check(state):
			yield (r.name, r.effect(state), r.cost, state.copy())

def is_goal(state):
   for item, amount in Crafting['Goal'].items():
      if item in state:
         if state[item] < amount:
            return False
      else:
         return False
   return True

def buildInventory():
	for items in Crafting['Items']:
	    maxInv[items] = 0
	for action,rule in Crafting['Recipes'].items():
	    if 'Requires' in rule:
	        for each in rule["Requires"].keys():
	            maxInv[each] = 1
	    if 'Consumes' in rule:
	        for each,amount in rule['Consumes'].items():
	            if maxInv[each] < amount:
	                maxInv[each] = amount
	maxInv[u'wooden_axe'] = 0
	maxInv[u'stone_axe'] = 0
	maxInv[u'iron_axe'] = 0
	maxInv[u'iron_pickaxe'] = 0

Recipe = namedtuple('Recipe',['name','check','effect','cost'])
all_recipes = []
maxInv = {}
buildInventory()
for name, rule in Crafting['Recipes'].items():
   checker = make_checker(rule)
   effector = make_effector(rule)
   recipe = Recipe(name, checker, effector, rule['Time'])
   all_recipes.append(recipe)

search(make_graph,Crafting['Initial'],is_goal)