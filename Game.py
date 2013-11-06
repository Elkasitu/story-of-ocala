##########################
### The Story of Ocala ###
##########################

__author__ = """Adrian Torres"""
__date__ = """04/10/2013"""
__version__ = """0.5"""

##########################
###      Imports       ###
##########################

import random
import os
import math
import time
from copy import deepcopy
from getchar import getch

##########################
###  Global Variables  ###
##########################

# Keeps track of entities
ID = 0
# Keeps track of items
ITEM_ID = 0
# Keeps track of skills
SKILL_ID = 0
# Keeps track of maps
MAP_ID = 0
# Keeps track of what each mob drops, at what rate [ITEM_ID, RATE]
DROPLIST = {'Bison':[[0, 0.5], [1, 0.5]],
            'Goblin': [[0, 0.7], [1, 0.7]],
            }
# Experience given by each mob
EXPTABLE = {'Bison': 1.3,
            'Goblin': 1.7,
            }

##########################
###    Map Tilesets    ###
##########################

MAIN = [[0]*32,
        [0] + [1]*30 + [0],
        [0] + [1]*30 + [0],
        [0] + [1]*30 + [0],
        [0] + [1]*30 + [0],
        [0] + [1]*30 + [0],
        [0] + [1]*30 + [0],
        [0] + [1]*30 + [0],
        [0] + [1]*30 + [0],
        [0] + [1]*30 + [0],
        [0] + [1]*30 + [0],
        [0] + [1]*30 + [0],
        [0] + [1]*30 + [0],
        [0] + [1]*30 + [0],
        [0] + [1]*30 + [0],
        [0]*32]

##########################
###      Effects       ###
##########################

# Heals the player by the specified amount, caller is optional (mainly for the skill class)
def heal(player, amount, caller=None):
    if not player.dead:
        if player.hp + amount > player.MAXHP:
            player.hp = player.MAXHP
        else:
            player.hp += amount
    else:
        # Player is dead, cannot heal
        print("%s is dead!"%player.name)

# Heals 20 HP
def heal_small(player, caller=None):
    heal(player, 20)
# Recovers the player's mana by the specified amount, caller is optional (mainly for the skill class)
def mana(player, amount, caller=None):
    if not player.dead:
        if player.mp + amount > player.MAXMP:
            player.mp = player.MAXMP
        else:
            player.mp += amount
    else:
        # Player is dead, cannot recover mana
        print("%s is dead!"%player.name)

# Recovers 20 MP
def mana_small(player, caller=None):
    mana(player, 10)

##########################
### Class definitions  ###
##########################

# Skill class, for the creation, modification and cast of skills from the player/mob object to another player/mob object
class Skill():

    def __init__(self, name, effect, mpCost, requiredLevel):
        global SKILL_ID
        self.ID = SKILL_ID
        SKILL_ID += 1
        self.name = name
        self.effect = effect
        self.mpCost = mpCost
        # Required level for the player to learn any given skill, to be implemented later
        self.requiredLevel = requiredLevel

    # Function for casting the skill on another object/on the caller
    def cast(self, caller, receiver):
        caller.mp -= self.mpCost
        self.effect(receiver, caller)
        if caller != receiver:
            print("%s casted %s on %s!"%(caller.name, self.name, receiver.name))
        else:
            print("%s casted %s on himself!"%(caller.name, self.name))

# Map class, for the creation and modification of maps, without changing the original
class Map():

    def __init__(self, name, mapTileSet, spawnSpots, spawnableMobs):
        global MAP_ID
        self.ID = MAP_ID
        MAP_ID += 1
        self.name = name
        # Creates a deepcopy of the tileSet, for modifications without changing the original
        self.mapTileSet = deepcopy(mapTileSet)
        self.spawnSpots = spawnSpots
        self.spawnableMobs = spawnableMobs
        self.spawnSet = False
        self.mobsInMap = []

    # Returns the map's height
    def height(self):
        return len(self.mapTileSet)

    # Returns the map's width
    def width(self):
        return len(self.mapTileSet[0])

    # Renders the tileSet's numeric values into string characters // TODO: Add colours to each individual type of character
    def renderMap(self):
        rep = ''
        for row in self.mapTileSet:
            for column in row:
                if column == 0:
                    rep += '#'
                elif column == 1:
                    rep += ' '
                elif column == 2:
                    rep += '@'
                elif column == 5:
                    rep += 'M'
                elif column == 100:
                    rep += 'B'
                elif column == 101:
                    rep += 'G'
            rep += '\n'
        print(rep)

    # Checks if the given coords are occupied by an entity in the map
    def isOccupied(self, coords):
        if self.mapTileSet[coords[1]][coords[0]] == 1:
            return False
        else:
            return True

    # Checks if there is anything other than empty spaces or "bedrock" in a 3x3 area
    def surroundings(self, coords):
        entities = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                if self.mapTileSet[coords[1]+y][coords[0]+x] not in (0, 1):
                    entities.append(self.mapTileSet[coords[1]+y][coords[0]+x])
        return entities

    # Plots the representation of the entity in the given coords (tuple)
    def plot(self, coords, entityRep):
        plotted = False
        if not self.isOccupied(coords):
            self.mapTileSet[coords[1]][coords[0]] = entityRep
            plotted = True
        return plotted

    # Unplots whatever is at the given coords (tuple)
    def unplot(self, coords):
        unplotted = False
        if self.isOccupied(coords):
            self.mapTileSet[coords[1]][coords[0]] = 1
            unplotted = True
        return unplotted

    # Assigns an object to a representation on the map, namely mobs
    def spawnMob(self, rep, coords):
        if rep == 100:
            self.mobsInMap.append(Mob("Bison", 50, 0, 5, 10, coords, rep))
        elif rep == 101:
            self.mobsInMap.append(Mob("Goblin", 75, 10, 1, 25, coords, rep))

    # Sets numerical representations on the tileSet, which are then rendered into string representations
    def setSpawn(self):
        if not self.spawnSet:
            for e in range(self.spawnSpots):
                loop = True
                while loop:
                    x, y = random.randint(0, (self.width()-1)), random.randint(0, (self.height()-1))
                    coords = (x, y)
                    if not self.isOccupied(coords):
                        r = random.randint(0, len(self.spawnableMobs)-1)
                        self.spawnMob(self.spawnableMobs[r], coords)
                        self.plot(coords, self.spawnableMobs[r])
                        loop = False
        self.spawnSet = True


class Character():

    def __init__(self, name, hp, mp, minAttack, maxAttack, coords, rep, skills=[]):
        # Global ID variable to keep track of Characters that would have the same name (i.e: Mob spawns)
        global ID
        self.ID = ID
        ID += 1
        self.minAttack = minAttack
        self.maxAttack = maxAttack
        self.hp = self.MAXHP = hp
        self.mp = self.MAXMP = mp
        self.name = name
        self.dead = False
        self.coords = coords
        # Numerical representation on the tileSet
        self.rep = rep
        # Skills possessed by the character at instance creation time
        self.skills = skills

    # Very basic attack module, but works // TODO: Increase complexity
    def attack(self, player, dmg=None):
        if dmg == None:
            dmg = random.randint(self.minAttack, self.maxAttack)
        if self.hp <= 0:
            print("%s is dead!"%self.name)
        elif player.hp <= 0:
            print("%s is already dead, %s is the winner!"%(player.name, self.name))
        else:
            player.hp -= dmg
            print("%s attacks %s! %s loses %d health points!"%(self.name, player.name, player.name, dmg))

    # Lets the character use Skill objects, and cast them on other Character entities/subclasses
    def skill(self, skill, receiver):
        for s in self.skills:
            if s.name == skill:
                s.cast(self, receiver)

    # Checks if the entity's dead, and updates death-related variables
    def checkDead(self):
        if self.hp <= 0:
            self.hp = 0
            self.dead = True

    # Heals the character object to full health
    def heal(self):
        if not self.dead:
            self.hp = self.MAXHP
        else:
            print("%s is dead, cannot restore health"%self.name)

    # Revives the character
    def revive(self):
        self.dead = False

    # Moves the character upwards
    def moveUp(self):
        newCoords = (self.coords[0], self.coords[1]-1)
        MAP = MAPLIST["Current"]
        if not MAP.isOccupied(newCoords):
            MAP.unplot(self.coords)
            MAP.plot(newCoords, self.rep)
            self.coords = newCoords

    # Moves the character downwards
    def moveDown(self):
        newCoords = (self.coords[0], self.coords[1]+1)
        MAP = MAPLIST["Current"]
        if not MAP.isOccupied(newCoords):
            MAP.unplot(self.coords)
            MAP.plot(newCoords, self.rep)
            self.coords = newCoords

    # Moves the character to the left
    def moveLeft(self):
        newCoords = (self.coords[0]-1, self.coords[1])
        MAP = MAPLIST["Current"]
        if not MAP.isOccupied(newCoords):
            MAP.unplot(self.coords)
            MAP.plot(newCoords, self.rep)
            self.coords = newCoords

    # Moves the character to the right
    def moveRight(self):
        newCoords = (self.coords[0]+1, self.coords[1])
        MAP = MAPLIST["Current"]
        if not MAP.isOccupied(newCoords):
            MAP.unplot(self.coords)
            MAP.plot(newCoords, self.rep)
            self.coords = newCoords


class Player(Character):

    def __init__(self, name, hp, mp, minAttack, maxAttack, coords, rep):
        # Player objects share ID with Character object throught inheritance
        global ID
        self.ID = ID
        ID += 1
        self.minAttack = minAttack
        self.maxAttack = maxAttack
        self.hp = self.MAXHP = hp
        self.mp = self.MAXMP = mp
        self.name = name
        self.level = 1
        self.exp = 0.0
        # Minimum exp required to level up
        self.minExp = 10.0
        # The player benefits from a 12-slot backpack
        self.backpack = Backpack(12)
        # The backpack object is given an owner variable containing the player itself, to be able to go back to the caller
        self.backpack.owner = self
        self.dead = False
        self.coords = coords
        self.rep = rep
        # Skills the player possesses // TODO: Implement skill acquiring function
        self.skills = []

    # The function updates the character's variables regarding levels and experience // TODO: Increase complexity
    def levelup(self):
        self.level += 1
        self.exp -= self.minExp
        self.minExp += self.minExp*0.35
        self.MAXHP += int(self.MAXHP*0.1)
        self.MAXMP += int(self.MAXMP*0.1)
        self.hp = self.MAXHP
        self.mp = self.MAXMP
        self.minAttack += int(self.minAttack*0.15)
        self.maxAttack += int(self.maxAttack*0.15)

    # Checks if the player has leveled up
    def checkLevelup(self):
        if self.exp >= self.minExp:
            self.levelup()
            print("%s is now level %d!"%(self.name, self.level))

    # Displays the player's backpack // TODO: Implement for the GUI
    def displayBackpack(self):
        itemsNone = 0
        items = 'You have '
        moreThanOne = False
        for e in self.backpack.storage:
            if e[0] != None:
                if not moreThanOne:
                    items += "%d %s"%(e[1], e[0].name)
                    moreThanOne = True
                else:
                    items += ", %d %s"%(e[1], e[0].name)
            else:
                 itemsNone += 1
        if itemsNone == self.backpack.slots:
            items = "You don't have any items in your backpack"
        else:
            items += " items in your backpack"
        print(items)


# For defining Item objects, which would be held inside a Backpack object, and usable from within
class Item():

    def __init__(self, name, isUsable, effect=None):
        # Global ID for Item objects, to keep track of them even if they have the same name
        global ITEM_ID
        self.ID = ITEM_ID
        ITEM_ID += 1
        self.name = name
        self.effect = effect
        self.isUsable = isUsable

    # Uses the Item object itself, by calling the effect if it's usable
    def use(self, owner):
        if self.isUsable:
            self.effect(owner)
        else:
            print("%s is not usable!"%self.name)

# Backpack class to be used mainly inside the Player class, but could also be applied to any Character class/subclass instance
class Backpack():

    def __init__(self, slots):
        self.storage = [[None]]
        self.storage *= slots
        self.slots = slots

    # Adds the item parameter quantity times, into the storage list
    def add(self, item, quantity):
        b = True
        i = 0
        fullCount = 0
        while b:
            slot = self.storage[i]
            if slot[0] == None:
                self.storage[i] = [item, quantity]
                b = False
            elif slot[0].ID == item.ID:
                slot[1] += quantity
                b = False
            else:
                fullCount += 1
            i += 1
        if fullCount == self.slots:
            print("Your backpack is full!")

    # Removes whichever item is in the slot parameter by the quantity parameter
    def remove(self, slot, quantity):
        if self.storage[slot][1] < quantity:
            self.storage[slot] = [None, 0]
        else:
            self.storage[slot][1] -= quantity

    # Uses the item by calling the Item.use() function, passing by the owner (the caller)
    def use(self, itemName):
        for slot in self.storage:
            if slot[0] != None:
                if slot[0].name == itemName:
                    slot[0].use(self.owner)
                    slot[1] -= 1
                    # Reduces the amount of given item by 1, or deletes it completely if the stack only contains 1
                    if slot[1] == 0:
                        slot[0] = None
                        slot[1] = 0
                    return
        else:
            # The user doesn't have enough of the given item
            print("You don't have enough of that item")
            return

# Mob class designed to represent enemies
class Mob(Character):

    # The drop method, when the entity dies it may or may not drop an item depending on the DROPLIST // TODO: Drop item on the ground
    def drop(self, killer):
        drops = DROPLIST[self.name]
        for e in drops:
            rnd = random.random()
            if rnd >= e[1]:
                # The dropped item is instantly added to the player's backpack
                killer.backpack.add(ITEMS[e[0]], 1)
                print("%s dropped %s"%(self.name, ITEMS[e[0]].name))

    # Searches for a player in a 3x3 area
    def detectPlayer(self):
        s = MAPLIST["Current"].surroundings(self.coords)
        if 2 in s:
            battle(player, self)

    # Special checkDead method, if the enemy dies it deletes its instance from the map
    def checkDead(self):
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            MAPLIST["Current"].unplot(self.coords)
            for mob in MAPLIST["Current"].mobsInMap:
                if mob.ID == self.ID:
                    MAPLIST["Current"].mobsInMap.remove(mob)

    # Follows the player around, efficient tracking using vectors
    def autoMove(self):
        m = lambda x1, x2, y1, y2: math.sqrt((x2-x1)**2 + (y2-y1)**2)
        module = m(self.coords[0], player.coords[0], self.coords[1], player.coords[1])
        e = math.sqrt(50)
        if module > 0 and module < e:
            modules = [m(self.coords[0]-1, player.coords[0], self.coords[1], player.coords[1]),
                       m(self.coords[0]+1, player.coords[0], self.coords[1], player.coords[1]),
                       m(self.coords[0], player.coords[0], self.coords[1]+1, player.coords[1]),
                       m(self.coords[0], player.coords[0], self.coords[1]-1, player.coords[1])
                       ]
            for i in range(4):
                if modules[i] < module:
                    module = modules[i]
                    ind = i
            if ind == 0:
                self.moveLeft()
            elif ind == 1:
                self.moveRight()
            elif ind == 2:
                self.moveDown()
            else:
                self.moveUp()      

##########################
###      Entities      ###
##########################

# playerMatias = Player("Matias", 100, 50, 10, 15)#
player = Player("Adrian", 500, 500, 10, 15, (5, 5), 2)
testMob = Mob("Bison", 50, 0, 1, 5, (10,10), 100)
# Keeps track of all entity objects
ENTITYLIST = [player]

##########################
###       Items        ###
##########################

pot_hp_small = Item("HP Potion", True, heal_small)              # ID = 0
pot_mp_small = Item("MP Potion", True, mana_small)              # ID = 1
# List of all items
ITEMS = [pot_hp_small, pot_mp_small]

##########################
###        Maps        ###
##########################

map_Main = Map("Main", MAIN, 3, [100, 101])
# Keeps track of all Map entities
MAPLIST = {"Current": map_Main, "Main": map_Main}

##########################
###       Skills       ###
##########################

skill_Heal_I = Skill("Heal I", heal_small, 10, 5)
        
##########################
###     Functions      ###
##########################

# Battle between playerEnt and mobEnt until either of the entities dies // TODO: Change to manual, GUI, Increase complexity
def battle(playerEnt, mobEnt):
    while playerEnt.hp > 0 and mobEnt.hp > 0:
        updateScreen()
        actionBar(1)
        print("Press A to attack")
        cmd = getch()
        while cmd.lower() != "a":
            cmd = getch()
        if cmd.lower() == "a":
            player.attack(mobEnt)
        mobEnt.attack(playerEnt)
        time.sleep(3)
    if playerEnt.hp == 0:
        # If at the end of the battle, the player's hp is null, then the player has died. Game over.
        print("Game over!")
    else:
        # Post-battle executions, xp gain, drops and levelup check
        r = random.random()
        xp = EXPTABLE[mobEnt.name]*(playerEnt.level*0.5) + r
        print("You killed %s! You obtain %.2f experience points!"%(mobEnt.name, xp))
        mobEnt.drop(playerEnt)
        playerEnt.exp += xp
        playerEnt.checkLevelup()
    playerEnt.checkDead()
    mobEnt.checkDead()
    time.sleep(3)
    updateScreen()

# Clears the screen and then prints the current map and GUI elements
def updateScreen():
    os.system('cls' if os.name=='nt' else 'clear')
    statusBar()
    MAPLIST["Current"].renderMap()

# Bar displaying HP, MP, Level and Experience values for the player
def statusBar():
    statusBar = ["##########################################",
                 "# HP: %00d # MP: %d ## Lvl: %d # XP: %.2f #"%(player.hp, player.mp, player.level, player.exp),
                 "##########################################"]
    for s in statusBar:
        print(s)

def actionBar(state, *args):
    
##    actionBar_OuttaBattle = ["##########################################",
##                             "# %-*s #"%(38, args[1]),
##                             "##########################################"]
##    actionBar_Backpack = ["##########################################",
##                          "# (%d) %-*s## (%d) %-*s #"%(args[0][0], 13, args[0][1], args[1][0], 13, args[1][1]),
##                          "# (%d) %-*s## (%d) %-*s #"%(args[2][0], 13, args[2][1], args[3][0], 13, args[3][1]),
##                          "# (%d) %-*s## (%d) %-*s #"%(args[4][0], 13, args[4][1], args[5][0], 13, args[5][1]),
##                          "# (%d) %-*s## (%d) %-*s #"%(args[6][0], 13, args[6][1], args[7][0], 13, args[7][1]),
##                          "# (%d) %-*s## (%d) %-*s #"%(args[8][0], 13, args[8][1], args[9][0], 13, args[9][1]),
##                          "# (%d) %-*s## (%d) %-*s #"%(args[10][0], 13, args[10][1], args[11][0], 13, args[11][1]),
##                          "##########################################"]
    actionBar_Combat = ["##########################################"]

    if state == 0:
        for i in actionBar_OuttaBattle:
            print(i)
    elif state == 1:
        for i in actionBar_Combat:
            print(i)
        

# Main game loop
def main():
    # Iterates over every entity and plots it into the map // DEPRECATED
    currentMap = MAPLIST["Current"]
    for e in ENTITYLIST:
        currentMap.plot(e.coords, e.rep)
    mainLoop = True
    player = ENTITYLIST[0]
    currentMap.setSpawn()
    # Updates the screen
    updateScreen()
    while mainLoop:
        for mob in currentMap.mobsInMap:
            mob.detectPlayer()
            mob.autoMove()
        key = getch()
        # Waits for user keypress
        if key.lower() == "w":
            player.moveUp()
            updateScreen()
        elif key.lower() == "s":
            player.moveDown()
            updateScreen()
        elif key.lower() == "a":
            player.moveLeft()
            updateScreen()
        elif key.lower() == "d":
            player.moveRight()
            updateScreen()

main()
