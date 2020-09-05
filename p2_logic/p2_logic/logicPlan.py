# logicPlan.py
# ------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In logicPlan.py, you will implement logic planning methods which are called by
Pacman agents (in logicAgents.py).
"""

import util
import sys
import logic
import game


pacman_str = 'P'
ghost_pos_str = 'G'
ghost_east_str = 'GE'
pacman_alive_str = 'PA'

class PlanningProblem:
    """
    This class outlines the structure of a planning problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the planning problem.
        """
        util.raiseNotDefined()

    def getGhostStartStates(self):
        """
        Returns a list containing the start state for each ghost.
        Only used in problems that use ghosts (FoodGhostPlanningProblem)
        """
        util.raiseNotDefined()
        
    def getGoalState(self):
        """
        Returns goal state for problem. Note only defined for problems that have
        a unique goal state such as PositionPlanningProblem
        """
        util.raiseNotDefined()

def tinyMazePlan(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def sentence1():
    """Returns a logic.Expr instance that encodes that the following expressions are all true.
    
    A or B
    (not A) if and only if ((not B) or C)
    (not A) or (not B) or C
    """
    A = logic.Expr('A')
    B = logic.Expr('B')
    C = logic.Expr('C')
    one = A|B
    two = (~A)%((~B)|C)
    three = logic.disjoin((~A),(~B),C)
    return logic.conjoin([one,two,three])

def sentence2():
    """Returns a logic.Expr instance that encodes that the following expressions are all true.
    
    C if and only if (B or D)
    A implies ((not B) and (not D))
    (not (B and (not C))) implies A
    (not D) implies C
    """
    A = logic.Expr('A')
    B = logic.Expr('B')
    C = logic.Expr('C')
    D = logic.Expr('D')
    one = C % (B|D)
    two = A >> ((~B)&(~D))
    three = (~(B&(~C))) >> A
    four = (~D) >> C
    return (logic.conjoin([one,two,three,four]))

def sentence3():
    """Using the symbols WumpusAlive[1], WumpusAlive[0], WumpusBorn[0], and WumpusKilled[0],
    created using the logic.PropSymbolExpr constructor, return a logic.PropSymbolExpr
    instance that encodes the following English sentences (in this order):

    The Wumpus is alive at time 1 if and only if the Wumpus was alive at time 0 and it was
    not killed at time 0 or it was not alive and time 0 and it was born at time 0.

    The Wumpus cannot both be alive at time 0 and be born at time 0.

    The Wumpus is born at time 0.
    """
    WumpusAlive1 = logic.PropSymbolExpr('WumpusAlive',1)
    WumpusAlive0 = logic.PropSymbolExpr('WumpusAlive',0)
    WumpusBorn0 = logic.PropSymbolExpr('WumpusBorn',0)
    WumpusKilled0 = logic.PropSymbolExpr('WumpusKilled',0)
    one = WumpusAlive1 % ((WumpusAlive0 & (~WumpusKilled0))|((~WumpusAlive0) & WumpusBorn0))
    two = ~(WumpusAlive0 & WumpusBorn0)
    three = WumpusBorn0
    result = logic.conjoin(one,two,three)
    return result

def findModel(sentence):
    """Given a propositional logic sentence (i.e. a logic.Expr instance), returns a satisfying
    model if one exists. Otherwise, returns False.
    """

    return logic.pycoSAT(logic.to_cnf(sentence))

def atLeastOne(literals) :
    """
    Given a list of logic.Expr literals (i.e. in the form A or ~A), return a single 
    logic.Expr instance in CNF (conjunctive normal form) that represents the logic 
    that at least one of the literals in the list is true.
    >>> A = logic.PropSymbolExpr('A');
    >>> B = logic.PropSymbolExpr('B');
    >>> symbols = [A, B]
    >>> atleast1 = atLeastOne(symbols)
    >>> model1 = {A:False, B:False}
    >>> print logic.pl_true(atleast1,model1)
    False
    >>> model2 = {A:False, B:True}
    >>> print logic.pl_true(atleast1,model2)
    True
    >>> model3 = {A:True, B:True}
    >>> print logic.pl_true(atleast1,model2)
    True
    """
    return logic.disjoin(literals)


def atMostOne(literals) :
    """
    Given a list of logic.Expr literals, return a single logic.Expr instance in 
    CNF (conjunctive normal form) that represents the logic that at most one of 
    the expressions in the list is true.
    """
    symbols = []
    results = []
    for symbol in literals:
        symbols.append(~symbol)
    for i in range(0,len(literals)-1):
        for j in range (i + 1, len(literals)):
            results.append((symbols[i]|symbols[j]))
    return logic.conjoin(results)

def exactlyOne(literals) :
    """
    Given a list of logic.Expr literals, return a single logic.Expr instance in 
    CNF (conjunctive normal form)that represents the logic that exactly one of 
    the expressions in the list is true.
    """

    return logic.conjoin(atLeastOne(literals),atMostOne(literals))


def extractActionSequence(model, actions):
    """
    Convert a model in to an ordered list of actions.
    model: Propositional logic model stored as a dictionary with keys being
    the symbol strings and values being Boolean: True or False
    Example:
    >>> model = {"North[3]":True, "P[3,4,1]":True, "P[3,3,1]":False, "West[1]":True, "GhostScary":True, "West[3]":False, "South[2]":True, "East[1]":False}
    >>> actions = ['North', 'South', 'East', 'West']
    >>> plan = extractActionSequence(model, actions)
    >>> print plan
    ['West', 'South', 'North']
    """
    actionmove = []
    times = []
    for m in model:
        if (logic.PropSymbolExpr.parseExpr(m)[0] in actions) and model[m]:
            actionmove.append(logic.PropSymbolExpr.parseExpr(m)[0])
            times.append(logic.PropSymbolExpr.parseExpr(m)[1])
    for i in range(0,len(times)):
        for j  in range(i + 1,len(times)):
            if int(times[i]) > int(times[j]):
                t1 = times[j]
                times[j] = times[i]
                times[i] = t1
                t2 = actionmove[j]
                actionmove[j] = actionmove[i]
                actionmove[i] = t2
    return actionmove


def pacmanSuccessorStateAxioms(x, y, t, walls_grid):
    """
    Successor state axiom for state (x,y,t) (from t-1), given the board (as a 
    grid representing the wall locations).
    Current <==> (previous position at time t-1) & (took action to move to x, y)
    """
    moves = []
    if not walls_grid[x+1][y]:
        moves.append(logic.PropSymbolExpr(pacman_str,x+1,y,t-1)&logic.PropSymbolExpr('West',t-1))
    if not walls_grid[x-1][y]:
        moves.append(logic.PropSymbolExpr(pacman_str,x-1,y,t-1)&logic.PropSymbolExpr('East',t-1))
    if not walls_grid[x][y+1]:
        moves.append(logic.PropSymbolExpr(pacman_str,x,y+1,t-1)&logic.PropSymbolExpr('South',t-1))
    if not walls_grid[x][y-1]:
        moves.append(logic.PropSymbolExpr(pacman_str,x,y-1,t-1)&logic.PropSymbolExpr('North',t-1))

    return logic.PropSymbolExpr(pacman_str,x,y,t) % (logic.disjoin(moves))


def positionLogicPlan(problem):
    """
    Given an instance of a PositionPlanningProblem, return a list of actions that lead to the goal.
    Available actions are game.Directions.{NORTH,SOUTH,EAST,WEST}
    Note that STOP is not an available action.
    """
    walls = problem.walls
    width, height = problem.getWidth(), problem.getHeight()
    start = problem.getStartState()
    goal = problem.getGoalState()
    logic_exp = []
    #initialize
    logic_exp = [logic.PropSymbolExpr(pacman_str,start[0],start[1],0)]
    for x in range(1, width + 1):
        for y in range(1, height + 1):
            if not walls[x][y] and (x != start[0] or y != start[1]):
                logic_exp.append(~logic.PropSymbolExpr(pacman_str,x,y,0))
    logic_exp.append(exactlyOne([logic.PropSymbolExpr('East',0),logic.PropSymbolExpr('West',0),logic.PropSymbolExpr('South',0),logic.PropSymbolExpr('North',0)]))

    for i in range(1,100):
        for x in range (1, width + 1):
            for y in range(1, height + 1):
                if not walls[x][y]:
                    logic_exp.append(pacmanSuccessorStateAxioms(x,y,i,walls))
        logic_exp.append(exactlyOne([logic.PropSymbolExpr('East',i), logic.PropSymbolExpr('West',i),logic.PropSymbolExpr('South',i),logic.PropSymbolExpr('North',i)]))
        logic_exp.append(pacmanSuccessorStateAxioms(goal[0],goal[1],i + 1,walls))
        logic_exp.append(logic.PropSymbolExpr(pacman_str,goal[0],goal[1],i + 1))

        model = findModel(logic.conjoin(logic_exp))
        if model:
            actions = ['East','West','South','North']
            return extractActionSequence(model, actions)
        logic_exp.pop()

def foodLogicPlan(problem):
    """
    Given an instance of a FoodPlanningProblem, return a list of actions that help Pacman
    eat all of the food.
    Available actions are game.Directions.{NORTH,SOUTH,EAST,WEST}
    Note that STOP is not an available action.
    """
    walls = problem.walls
    width, height = problem.getWidth(), problem.getHeight()
    startstate = problem.getStartState()
    start = startstate[0]
    foodgrid = startstate[1]
    logic_exp = []
    logic_exp = [logic.PropSymbolExpr(pacman_str, start[0],start[1],0)]
    for x in range(1, width + 1):
        for y in range(1, height + 1):
            if not walls[x][y] and ( x != start[0] or y != start[1]):
                logic_exp.append(~logic.PropSymbolExpr(pacman_str,x,y,0))

    logic_exp.append(exactlyOne([logic.PropSymbolExpr('East',0),logic.PropSymbolExpr('West',0),logic.PropSymbolExpr('South',0),logic.PropSymbolExpr('North',0)]))

    for t in range(1,100):
        for x in range(1, width + 1):
            for y in range(1,height + 1):
                if not walls[x][y]:
                    logic_exp.append(pacmanSuccessorStateAxioms(x,y,t,walls))

        logic_exp.append(exactlyOne([logic.PropSymbolExpr('East',t),logic.PropSymbolExpr('West',t),logic.PropSymbolExpr('South',t),logic.PropSymbolExpr('North',t)]))

        count = 0
        #count the number of food logic added in logic_exp
        for x in range(1, width + 1):
            for y in range (1, height + 1):
                visit = []
                if foodgrid[x][y]:
                    for i in range(1, t+1):
                        visit.append(logic.PropSymbolExpr(pacman_str,x,y,i))
                    logic_exp.append(atLeastOne(visit))
                    count = count + 1
        model = findModel(logic.conjoin(logic_exp))
        if model:
            actionmove = ['East','West','South','North']
            return extractActionSequence(model, actionmove)

        for i in range(1, count + 1):
            logic_exp.pop()

# Abbreviations
plp = positionLogicPlan
flp = foodLogicPlan

# Some for the logic module uses pretty deep recursion on long expressions
sys.setrecursionlimit(100000)
    