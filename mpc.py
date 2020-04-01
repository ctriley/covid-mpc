import os
import sys
from gurobipy import *


def main():
    cities = ["new_york", "chicago"]
    travel_times = {"new_york": {"chicago": 1, "new_york": 0}, "chicago": {"new_york": 1, "chicago": 0}}
    demand_prediction = {"new_york": [5,3,2,1], "chicago": [2,3,4,2]}
    resources = {"new_york": [5, 4, 0, 0], "chicago": [3,7, 0, 0] }
    lookahead = 2
    length_of_resource_need = 1
    death_rate = .8
    print([x for x in range(0, length_of_resource_need)])
    print("#########################")
    run_model(cities, travel_times, demand_prediction, resources, 
        lookahead, death_rate, length_of_resource_need)
    

def run_model(cities, travel_times, demand_prediction, resources, lookahead, 
    death_rate, length_of_resource_need):
    try:
        model = Model("covid-mpc")

        # variables 
        xps = [[] for x in range(0,lookahead)]
        xrs = [[] for x in range(0,lookahead)]
        vs = [[] for x in range(0,lookahead)]
        us = [[] for x in range(0,lookahead)]
        for t in range(0, lookahead):
            for i, city in enumerate(cities):
                xps[t].append(model.addVar(name="xp_" + str(i) + str(t), 
                    vtype=GRB.INTEGER))
                obj_value = lookahead - t
                us[t].append(model.addVar(name="u_" + str(i) + str(t), 
                    vtype=GRB.INTEGER, obj=obj_value))
                vs[t].append(model.addVar(name="v_" + str(i) + str(t), 
                    vtype=GRB.INTEGER))
        for t in range(0, lookahead):
            for i, c1 in enumerate(cities):
                t2 = []
                for j, c2 in enumerate(cities):
                    obj_value = travel_times[c1][c2]
                    t2.append(model.addVar(name="xr_" + str(i) + str(j) + str(t),
                        vtype=GRB.INTEGER, obj=obj_value))
                xrs[t].append(t2)
        model.update()
        # constraints

        #1b
        for i, city in enumerate(cities):
            model.addConstr(xps[0][i] + us[0][i] == demand_prediction[city][0],
                    name="1b_" + str(i))
        
        for t in range(1, lookahead):
            for i, city in enumerate(cities):
                v_temp = []
                if t - 1 >= 0:        
                    v_temp.append(vs[t-1][i])
                ones = [1] * len(v_temp)
                expr = LinExpr(ones, v_temp)
                #1c
                model.addConstr(xps[t][i] + us[t][i] == demand_prediction[city][t] - expr,
                        name="1c_" + str(i) + str(t))
        for t in range(0, lookahead):
            for i, city in enumerate(cities):
                #1d
                model.addConstr(vs[t][i] >= death_rate * us[t][i],
                        name="1d_1_" + str(i) + str(t))
                model.addConstr(vs[t][i] <= death_rate * us[t][i] + 1,
                        name="1d_2_" + str(i) + str(t))
                #1e
                v_temp = []
                ones = []
                v_temp.append(xps[t][i])
                ones.append(1.0)
                for j, c2 in enumerate(cities):
                    v_temp.append(xrs[t][i][j])
                    ones.append(1.0)
                    tt = travel_times[c2][city]
                    if t - tt >= 0:
                        v_temp.append(xrs[t-tt][j][i])
                        ones.append(-1.0)
                    if t > 0:
                        v_temp.append(xps[t-1][i])
                        ones.append(-1.0)
                expr = LinExpr(ones, v_temp)
                model.addConstr(expr == resources[city][t],
                        name="1e_" + str(i) + str(t))

        model.optimize()
        model.write("model.lp")
        for v in model.getVars():
            print('%s %g' % (v.varName, v.x))

        print('Obj: %g' % model.objVal)

    except GurobiError as e:
        print("Error code " + str(e.errno) + ":" + str(e))
    except AttributeError as e:
        print("Encounter an attribute error" + str(e))


if __name__ == "__main__":
    main()
