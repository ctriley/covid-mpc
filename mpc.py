import os
import sys
from gurobipy import *


def main():
    cities = ["new_york", "chicago"]
    travel_times = {"new_york": {"chicago": 1}}
    demand_prediction = {"new_york": [5,3,2,1], "chicago": [2,3,4,2]}
    resources {"new_york": [5, 4], "chicago": [3,7] }
    lookahead = 4
    length_of_resource_need = 1
    death_rate = .8
    run_model(cties, travel_times, demand_prediction, resources, 
        lookahead, death_rate, length_of_resource_need)
    

def run_model(cities, travel_times, demand_prediction, resources, lookahead, 
    death_rate, length_of_resource_need):
    try:
        m = Model("covid-mpc")

        # variables 
        xps = [[] for x in xrange(lookahead)]
        xrs = [[] for x in xrange(lookahead)]
        vs = [[] for x in xrange(lookahead)]
        us = [[] for x in xrange(lookahead)]
        for i in xrange(lookahead):
            for city in cities:
                xps[i].append(model.addVar(vtype=GRB.INTEGER))
                obj_value = lookahead - i
                us[i].append(model.addVar(vtype=GRB.INTEGER, obj=obj_value))
                vs[i].append(model.addVar(vtype=GRB.INTEGER))
        for i in range(0, lookahead):
            for c1 in cities:
                t2 = []
                for c2 in cities:
                    obj_value = travel_times[i][j]
                    t2.append(model.addVar(vtype=GRB.INTEGER, obj=obj_value))
                xrs[i].append(t2)

        # constraints

        #1b
        for i, city in enumerate(cities):
            model.addConstr(xp[0][i] + us[0][i] == demand_prediction[city][0])
        
        for t in range(1, lookahead):
            for i, city in enumerate(cities):
                v_temp = []
                for k in xrange(length_of_resource_need):
                    if i - k >=0:
                        v_temp.append(vs[t][i-k])
                ones = [1] * len(v_temp)
                expr = LinExpr(ones, v_temp)
                #1c
                model.addConstr(x[t][i] + us[t][i] == demand_prediction[city][t] - expr)
                #1d
                model.addConstr(vs[t][i] >= death_rate * u[t][i])
                model.addConstr(vs[t][i] <= death_rate * u[t][i] + 1)
                #1e
                v_temp = []
                for j, c2 in enumerate(cities):
                    tt = travel_times[j][i]
                    if t - tt >= 0:
                        v_temp.append(xrs[t-tt][j][i])
                    if t > 0:
                        v_temp.append(xps[t-1][i])
                ones = [1] * len(v_temp)
                expr = LinExpr(ones, v_temp)
                model.addConstr(xps[t][i] + xrs[t][i][j] == resources[city][t] + expr)

        m.optimize()

        for v in m.getVars():
            print('%s %g' % (v.varName, v.x))

        print('Obj: %g' % m.objVal)

    except GurobiError as e:
        print("Error code " + str(e.errno) + ":" + str(e))
    except AttributeError:
        print("Encounter an attribute error")


if __name__ == "__main__":
    main()