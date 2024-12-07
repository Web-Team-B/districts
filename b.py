import os, sys
import sumolib
import traci
import time
import pandas as pd
import xml.etree.ElementTree as ET
import traci.constants

median_income = 2077892
hours_in_a_month = 30 * 8
hourly_rate = median_income / hours_in_a_month
secondary_rate = hourly_rate / 3600
toll = 2000
toll_to_time = toll / secondary_rate
print(toll)

tree = ET.parse('yeoksam_district.xml')
root = tree.getroot()

tazlist = []
for taz in root.iter("taz"):
        for taz_sink in taz.findall("tazSink"):
            tazlist.append(taz_sink.get("id"))

net = sumolib.net.readNet('gangnam.net.xml')
edges = net.getEdges()

sumoBinary = sumolib.checkBinary('sumo')
sumoCmd = [sumoBinary, "-c", "gangnam.sumocfg"]

traci.start(sumoCmd, label="sim")

for edge in edges:
    edge_id = edge.getID()
    elen = traci.lane.getLength(edge_id + "_0")
    e_s = traci.lane.getMaxSpeed(edge_id + "_0")
    traci.edge.setEffort(edge.getID(), (elen / e_s) * 0.7)



step = 0
while step < 86400:
    traci.simulationStep()

    if 25200 < step < 75600:
        if step % 60 == 0:
            for edge in edges:
                if edge.getID() in tazlist:
                        traci.edge.setEffort(edge.getID(), traci.edge.getTraveltime(edge.getID())+toll_to_time)
                else:
                    traci.edge.setEffort(edge.getID(), traci.edge.getTraveltime(edge.getID()))
            for vehId in traci.vehicle.getIDList():
                st = traci.vehicle.getRoadID(vehId)
                dt = traci.vehicle.getRoute(vehId)[-1]
                veh = traci.vehicle.getTypeID(vehId)
                route = traci.simulation.findRoute(st, dt, vType=veh, depart=step, routingMode=2).edges
                traci.vehicle.setRoute(vehId, route)

            for vehId in traci.simulation.getDepartedIDList():
                traci.vehicle.rerouteEffort(vehId)

    else:
        if step % 60 == 0:
            for edge in edges:
                traci.edge.setEffort(edge.getID(), traci.edge.getTraveltime(edge.getID()))

            for vehId in traci.vehicle.getIDList():
                st = traci.vehicle.getRoadID(vehId)
                dt = traci.vehicle.getRoute(vehId)[-1]
                veh = traci.vehicle.getTypeID(vehId)
                route = traci.simulation.findRoute(st, dt, vType=veh, depart=step, routingMode=2).edges
                traci.vehicle.setRoute(vehId, route)

            for vehId in traci.simulation.getDepartedIDList():
                traci.vehicle.rerouteEffort(vehId)
                
    if step % 60 == 0:
        print(step)
    step += 1

traci.close()
