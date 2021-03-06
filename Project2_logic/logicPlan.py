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
    return [s, s, w, s, w, w, s, w]


def sentence1():
    """Returns a logic.Expr instance that encodes that the following expressions are all true.
    
    A or B
    (not A) if and only if ((not B) or C)
    (not A) or (not B) or C
    """
    A = logic.Expr('A')
    B = logic.Expr('B')
    C = logic.Expr('C')
    return logic.conjoin([(A | B),
                          (~A % (~B | C)),
                          logic.disjoin([~A, ~B, C])])


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
    return logic.conjoin([(C % (B | D)),
                          A >> (~B & ~D),
                          ~(B & ~C) >> A,
                          ~D >> C])


def sentence3():
    """Using the symbols WumpusAlive[1], WumpusAlive[0], WumpusBorn[0], and WumpusKilled[0],
    created using the logic.PropSymbolExpr constructor, return a logic.PropSymbolExpr
    instance that encodes the following English sentences (in this order):

    The Wumpus is alive at time 1 if and only if the Wumpus was alive at time 0 and it was
    not killed at time 0 or it was not alive and time 0 and it was born at time 0.

    The Wumpus cannot both be alive at time 0 and be born at time 0.

    The Wumpus is born at time 0.
    """
    WumpusAlive_1 = logic.PropSymbolExpr('WumpusAlive', 1)
    WumpusAlive_0 = logic.PropSymbolExpr('WumpusAlive', 0)
    WumpusBorn_0 = logic.PropSymbolExpr('WumpusBorn', 0)
    WumpusKilled_0 = logic.PropSymbolExpr('WumpusKilled', 0)

    return logic.conjoin([WumpusAlive_1 % ((WumpusAlive_0 & ~WumpusKilled_0) | (~WumpusAlive_0 & WumpusBorn_0)),
                          ~(WumpusAlive_0 & WumpusBorn_0),
                          WumpusBorn_0])


def findModel(sentence):
    """Given a propositional logic sentence (i.e. a logic.Expr instance), returns a satisfying
    model if one exists. Otherwise, returns False.
    """
    cnf = logic.to_cnf(sentence)
    sol = logic.pycoSAT(cnf)
    return sol


def atLeastOne(literals):
    """
    Given a list of logic.Expr literals (i.e. in the form A or ~A), return a single 
    logic.Expr instance in CNF (conjunctive normal form) that represents the logic 
    that at least one of the literals in the list is true.
    >>> A = logic.PropSymbolExpr('A')
    >>> B = logic.PropSymbolExpr('B')
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
    final = logic.disjoin(literals)
    return final


def atMostOne(literals):
    """
    Given a list of logic.Expr literals, return a single logic.Expr instance in 
    CNF (conjunctive normal form) that represents the logic that at most one of 
    the expressions in the list is true.
    """
    conj = []
    for i in range(len(literals)):
        for j in range(len(literals)):
            if j > i:
                conj.append(logic.disjoin([~literals[i], ~literals[j]]))
    # print(logic.conjoin(conj))
    return logic.conjoin(conj)


def exactlyOne(literals):
    """
    Given a list of logic.Expr literals, return a single logic.Expr instance in 
    CNF (conjunctive normal form)that represents the logic that exactly one of 
    the expressions in the list is true.
    """
    return atLeastOne(literals) & atMostOne(literals)


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
    plan = []
    for k in model:
        if (logic.PropSymbolExpr.parseExpr(k)[0] in actions) and model[k] == True:
            plan.append((logic.PropSymbolExpr.parseExpr(k)[0], int(logic.PropSymbolExpr.parseExpr(k)[1])))
    return [xxx[0] for xxx in sorted(plan, key=lambda x: x[1])]


def pacmanSuccessorStateAxioms(x, y, t, walls_grid):
    """
    Successor state axiom for state (x,y,t) (from t-1), given the board (as a 
    grid representing the wall locations).
    Current <==> (previous position at time t-1) & (took action to move to x, y)
    """
    listlit = []
    actions = ['South', 'North', 'West', 'East']
    xs = [x, x, x + 1, x - 1]
    ys = [y + 1, y - 1, y, y]
    for i in range(len(actions)):
        if not walls_grid[xs[i]][ys[i]]:
            listlit.append(
                logic.PropSymbolExpr(pacman_str, xs[i], ys[i], t - 1) & logic.PropSymbolExpr(actions[i], t - 1))
    return logic.to_cnf(logic.disjoin(listlit) % logic.PropSymbolExpr(pacman_str, x, y, t))


def positionLogicPlan(problem):
    """
    Given an instance of a PositionPlanningProblem, return a list of actions that lead to the goal.
    Available actions are game.Directions.{NORTH,SOUTH,EAST,WEST}
    Note that STOP is not an available action.
    """
    walls = problem.walls
    width, height = problem.getWidth(), problem.getHeight()

    "********CODE*******"
    x_0, y_0 = problem.getStartState()
    x_N, y_N = problem.getGoalState()
    actions = ['South', 'North', 'West', 'East']
    MAX_TIME = 50
    knowledgeBase = logic.PropSymbolExpr(pacman_str, x_0, y_0, 0)
    for t in range(0, MAX_TIME + 1):
        checkGoal = logic.PropSymbolExpr(pacman_str, x_N, y_N, t + 1)
        knowledgeBase = logic.conjoin(
            [knowledgeBase, exactlyOne([logic.PropSymbolExpr(action, t) for action in actions])])
        for x in range(1, width + 1):
            for y in range(1, height + 1):
                if t == 0 and (x != x_0 or y != y_0):
                    knowledgeBase = logic.conjoin([knowledgeBase, ~(logic.PropSymbolExpr(pacman_str, x, y, t))])
                if not walls[x][y]:
                    knowledgeBase = logic.conjoin([knowledgeBase, pacmanSuccessorStateAxioms(x, y, t + 1, walls)])
        isGoal = logic.conjoin(knowledgeBase, checkGoal)
        model = findModel(isGoal)

        if model:
            return extractActionSequence(model, actions)


def foodLogicPlan(problem):
    """
    Given an instance of a FoodPlanningProblem, return a list of actions that help Pacman
    eat all of the food.
    Available actions are game.Directions.{NORTH,SOUTH,EAST,WEST}
    Note that STOP is not an available action.
    """
    walls = problem.walls
    width, height = problem.getWidth(), problem.getHeight()

    "*** YOUR CODE HERE ***"
    x_0, y_0 = problem.getStartState()[0]
    foods = problem.getStartState()[1]
    actions = ['South', 'North', 'West', 'East']
    MAX_TIME = 50
    knowledgeBase = logic.PropSymbolExpr(pacman_str, x_0, y_0, 0)
    for t in range(0, MAX_TIME + 1):
        knowledgeBase = logic.conjoin([knowledgeBase,
                                       exactlyOne([logic.PropSymbolExpr(action, t) for action in actions])])
        checkGoal = logic.PropSymbolExpr(pacman_str, x_0, y_0, 0)
        for x in range(1, width + 1):
            for y in range(1, height + 1):
                if t == 0 and (x != x_0 or y != y_0):
                    knowledgeBase = logic.conjoin([knowledgeBase, ~(logic.PropSymbolExpr(pacman_str, x, y, t))])
                if not walls[x][y]:
                    knowledgeBase = logic.conjoin([knowledgeBase, pacmanSuccessorStateAxioms(x, y, t + 1, walls)])
                if foods[x][y]:
                    checkGoal = logic.conjoin([checkGoal,
                        logic.disjoin([logic.PropSymbolExpr(pacman_str, x, y, tt) for tt in range(0, t+2)])])
        isGoal = logic.conjoin([checkGoal, knowledgeBase])
        model = findModel(isGoal)

        if model:
            return extractActionSequence(model, actions)



# Abbreviations
plp = positionLogicPlan
flp = foodLogicPlan

# Some for the logic module uses pretty deep recursion on long expressions
sys.setrecursionlimit(100000)
