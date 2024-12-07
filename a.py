import os, sys
import sumolib
import traci
import time
import pandas as pd
import xml.etree.ElementTree as ET
import traci.constants

# district.xml 파일 열기 및 확인
try:
    tree = ET.parse('district.xml')
    root = tree.getroot()
    tazlist = []
    cnt = 0
    for neighbor in root.iter('taz'):
        if cnt == 2:
            for roadId in neighbor.iter('tazSink'):
                valueList = list(roadId.attrib.values())
                tazlist.append(valueList[0])
        cnt += 1
    print("district.xml 파일이 성공적으로 열렸습니다.")
except ET.ParseError as e:
    print(f"district.xml 파일을 열 수 없습니다: {e}")
    sys.exit(1)

# 네트워크 파일 로드
net = sumolib.net.readNet('gangnam.net.xml')
edges = net.getEdges()

# SUMO 시뮬레이션 명령어 설정
sumoBinary = sumolib.checkBinary('sumo')
sumoCmd = [sumoBinary, "-c", "sumo.sumocfg"]

# 트래픽 시뮬레이션 시작
traci.start(sumoCmd, label="sim")

# 초기 도로 통과에 필요한 시간 설정
for edge in edges:
    edge_id = edge.getID()
    elen = traci.lane.getLength(edge_id + "_0")
    e_s = traci.lane.getMaxSpeed(edge_id + "_0")
    traci.edge.setEffort(edge.getID(), (elen / e_s) * 0.7)

step = 0
while step < 86400:
    traci.simulationStep()

    if step > 25200 and step < 75600: # 특정 시간대에 요금 부과
        if step % 180 == 0:  # 업데이트 주기 180초로 설정
            for edge in edges:
                if edge.getID() in tazlist:
                    traci.edge.setEffort(edge.getID(), traci.edge.getTraveltime(edge.getID()) + edge.getLength() * 0.06)
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
        if step % 180 == 0:  # 업데이트 주기 180초로 설정
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
                
    if step % 180 == 0:
        print(step)
    step += 1

traci.close()
