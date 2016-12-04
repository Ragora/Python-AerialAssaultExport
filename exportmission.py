"""
    exportmission.py

    This software is licensed under the MIT license. See LICENSE for more information.
"""

import os
import re

def command_mission(command, result):
        mission = " ".join(command[1:]).lstrip("\"").rstrip("\"")
        print("Found Mission - %s" % mission)
        result["mission"] = "%s - Aerial Assault Port" % mission

def command_music(command, result):
    result["root"]["musicTrack"] = command[1]

def command_camera(command, result):
    position = "%s %s %s" % (command[1], command[3], command[2])

    entity = {
        "position": position,
        "class": "Camera",
        "scale": "1 1 1",
        "datablock": "Observer",
    }

    result["observerDropsGroup"]["children"].append(entity)

def command_spawn(command, result):
    position = "%s %s %s" % (command[2], command[4], command[3])
    team = int(command[1])

    # The weights and radiuses may not be correct
    entity = {
        "class": "SpawnSphere",
        "position": position,
        "radius": command[5],
        "sphereWeight": command[6],
        "indoorWeight": command[6],
        "outdoorWeight": command[7],
        "datablock": "SpawnSphereMarker",
    }
    result["teamSpawnsGroups"][team]["children"].append(entity)

def command_sensor(command, result):
    position = "%s %s %s" % (command[4], command[6], command[5])

    # FIXME: Right now we always force large sensors
    # FIXME: I don't know for sure if these are actually team and power group ID's
    team_id = int(command[3])
    group_id = int(command[2])

    entity = {
        "class": "StaticShape",
        "datablock": "SensorLargePulse",
        "position": position,
        "team": team_id,
    }

    # FIXME: We don't know 100% if these are actually the team ID's and power groups
    result["powerGroups"].setdefault(team_id, {})
    result["powerGroups"][team_id].setdefault(group_id, [])
    result["powerGroups"][team_id][group_id].append(entity)

def command_pickup(command, result):
    position = "%s %s %s" % (command[1], command[3], command[2])

    # FIXME: These may not always be valid datablocks in Base T2
    item_datablock = command[4]
    entity = {
        "class": "Item",
        "position": position,
        "datablock": item_datablock,
        "scale": "1 1 1",
        "static": "1",
        "rotate": "0",
    }

    result["root"]["children"].append(entity)

def command_generator(command, result):
    position = "%s %s %s" % (command[3], command[5], command[4])

    # FIXME: Convert to T2's rots
    rotation = "%s %s %s" % (command[7], command[9], command[8])

    team_id = int(command[1])
    group_id = int(command[2])
    entity = {
        "datablock": "GeneratorLarge",
        "rotation": rotation,
        "position": position,
        "class": "StaticShape",
        "nametag": "Ported",
        "team": team_id,
    }

    # FIXME: We don't know 100% if these are actually the team ID's and power groups
    result["powerGroups"].setdefault(team_id, {})
    result["powerGroups"][team_id].setdefault(group_id, [])
    result["powerGroups"][team_id][group_id].append(entity)

def command_waypoint(command, result):
    position = "%s %s %s" % (command[2], command[4], command[3])

    team_id = int(command[1])
    entity = {
        "class": "Waypoint",
        "datablock": "WaypointMarker",
        "team": str(team_id),
        "name": "%s <UNABLE TO LOOKUP TEXT>" % command[5],
    }
    result["root"]["children"].append(entity)

def command_sun(command, result):
    direction = "%s %s %s" % (command[1], command[3], command[2])
    color = "%f %f %f" % (float(command[4]) / 255, float(command[5]) / 255, float(command[6]) / 255)
    ambient = "0.800000 0.800000 0.800000 1.000000"

    entity = {
        "class": "Sun",
        "color": color,
        "direction": direction,
        "ambient": ambient,
    }
    result["root"]["children"].append(entity)

def command_sky(command, result):
    # ['SKY', 'Data/Sky/lush/SkyT.bmp', 'Data/Sky/lush/SkyF.bmp', 'Data/Sky/lush/SkyL.bmp', 'Data/Sky/lush/SkyB.bmp', 'Data/Sky/lush/SkyR.bmp']
    # FIXME: Resolve the mat file
    entity = {
        "class": "Sky",
        "objectName": "Sky",
        "position": "0 0 0",
        "scale": "1 1 1",
        "rotation": "1 0 0 0",
        "materialList": "sky_desert_brown.dml",
    }
    result["objectNames"]["Sky"] = entity
    result["root"]["children"].append(entity)

def command_inven(command, result):
    position = "%s %s %s" % (command[3], command[5], command[4])

    if len(command) == 7:
        rotation = "1 0 0 0"
    else:
        # FIXME: Convert this to axis-angle, quat, whatever T2 uses
        rotation = "%s %s %s" % (command[7], command[9], command[8])

    team_id = int(command[1])
    group_id = int(command[2])
    entity = {
        "position": position,
        "rotation": rotation,
        "team": str(team_id),
        "nameTag": "Ported",
        "class": "StaticShape",
        "dataBlock": "StationInventory",
    }

    # FIXME: We don't know 100% if these are actually the team ID's and power groups
    result["powerGroups"].setdefault(team_id, {})
    result["powerGroups"][team_id].setdefault(group_id, [])
    result["powerGroups"][team_id][group_id].append(entity)

def command_bounds(command, result):
    if len(command) == 4:
        bounds_end = [0.0, 0.0, 0.0]
    else:
        bounds_end = [float(axis) for axis in command[4:7]]

    bounds_start = [float(axis) for axis in command[1:4]]

    temp = bounds_start[1]
    bounds_start[1] = bounds_start[2]
    bounds_start[2] = temp

    temp = bounds_end[1]
    bounds_end[1] = bounds_end[2]
    bounds_end[2] = temp

    bounds_delta = [start - bounds_end[index] for index, start in enumerate(bounds_start)]

    # FIXME: WTF is the fourth component in T2 MIS files?
    area = "%f %f %f 1024" % (bounds_delta[0], bounds_delta[1], bounds_delta[2])
    flight_ceiling = str(max(bounds_start[2], bounds_end[2]))

    entity = {
        "class": "MissionArea",
        "objectName": "MissionArea",
        "area": area,
        "flightCeiling": flight_ceiling,
        "flightCeilingRange": "50",
    }
    result["objectNames"]["MissionArea"] = entity
    result["root"]["children"].append(entity)

def command_building(command, result):
    position = "%s %s %s" % (command[2], command[4], command[3])

    if len(command) == 9 or len(command) == 10:
        scale = "%s %s %s" % (command[5], command[7], command[6])
        rotation = "1 0 0 0"

        # FIXME: These entries have /* on the end of them?
        command.pop()
    elif len(command) == 8:
        scale = "%s %s %s" % (command[5], command[7], command[6])
    else:
        # FIXME: Convert this to axis-angle, quat, whatever T2 uses
        rotation = "%s %s %s" % (command[5], command[7], command[6])
        scale = "%s %s %s" % (command[8], command[10], command[9])

        # FIXME: These entries have /* on the end of them?
        if len(command) == 13:
            command.pop()

    interior_file = "%s.dif" % command[len(command) - 1].lstrip("\"").rstrip("\"")
    entity = {
        "class": "InteriorInstance",
        "position": position,
        "scale": scale,
        "rotation": rotation,
        "interiorFile": interior_file,
        "showTerrainInside": "1",
    }

    result["root"]["children"].append(entity)

def command_terrain(command, result):
    empty_squares = ""

    if "EMPTYSQUARES" in command:
        empty_squares = " ".join(command[command.index("EMPTYSQUARES") + 1:])

    terrain_file = command[1].lstrip("\"").rstrip("\"")
    entity = {
        "class": "TerrainBlock",
        # Assume always-origin for now
        "position": "0 0 0",
        "scale": "1 1 1",
        "objectName": "Terrain",
        "terrainFile": terrain_file,
        "emptySquares": empty_squares
    }

    result["objectNames"]["Terrain"] = entity
    result["root"]["children"].append(entity)

def command_scenery(command, result):
    position = "%s %s %s" % (command[1], command[3], command[2])

    # FIXME: Convert this to axis-angle, quat, whatever T2 uses
    rotation = "%s %s %s" % (command[4], command[6], command[5])

    try:
        if len(command) == 8:
            scale = "1 1 1"
            shapename = command[7]
        else:
            scale = "%s %s %s" % (command[7], command[9], command[8])
            shapename = command[10]
    except IndexError as e:
        print("!!! Skipped an entity, this is a bug.")
        return

    shapename = "%s.dts" % shapename.lstrip("\"").rstrip("\"")
    entity = {
        "class": "TSStatic",
        "shapeName": shapename,
        "position": position,
        "rotation": rotation,
        "scale": scale
    }
    result["root"]["children"].append(entity)

def export_mission(data):
    command_map = {
        "MISSION": command_mission,
        "MUSIC": command_music,
        "CAMERA": command_camera,
        "SPAWN": command_spawn,
        "SENSOR": command_sensor,
        "PICKUP": command_pickup,
        "GENERATOR": command_generator,
        "WAYPOINT": command_waypoint,
        "SUN": command_sun,
        "SKY": command_sky,
        "INVEN": command_inven,
        "BOUNDS": command_bounds,
        "BUILDING": command_building,
        "TERRAIN": command_terrain,
        "SCENERY": command_scenery,
    }

    mission_result = {
        "objectNames": {},
        "root": {"class": "SimGroup", "objectName": "MissionGroup", "children": []},

        # Each team group
        "teamsGroup": None,
        # The drop points
        "observerDropsGroup": None,

        # The spawns in each team
        "teamSpawnsGroups": None,
        # The powered groups in each team
        "teamPoweredGroups": None,

        # Used for determining what should power what
        "powerGroups": {},
    }

    mission_result["teamsGroup"] = {"class": "SimGroup", "objectName": "Teams", "children": []}
    mission_result["root"]["children"].append(mission_result["teamsGroup"])

    mission_result["observerDropsGroup"] = {"class": "SimGroup", "objectName": "ObserverDropPoints", "children": []}
    mission_result["root"]["children"].append(mission_result["observerDropsGroup"])

    mission_result["teamSpawnsGroups"] = []
    mission_result["teamPoweredGroups"] = []

    # Generate the team groups
    for team in range(8):
        mission_result["powerGroups"][team] = {}

        team_group = {"class": "SimGroup", "objectName": "Team%u" % team, "children": []}
        spawns_group = {"class": "SimGroup", "objectName": "SpawnSpheres", "children": []}
        powered_group = {"class": "SimGroup", "objectName": "Powered", "children": []}

        # Create the main team group
        mission_result["teamsGroup"]["children"].append(team_group)

        # Spawns underneath of it
        mission_result["teamSpawnsGroups"].append(spawns_group)
        team_group["children"].append(spawns_group)

        # Powered group underneath of the main team
        mission_result["teamPoweredGroups"].append(powered_group)
        team_group["children"].append(powered_group)

    for component in data:
        command = component[0]

        if command not in command_map:
            print("!!! Unknown command: %s" % command)
        else:
            command_map[command](component, mission_result)

    # Build the power groups correctly
    for team_id in mission_result["powerGroups"]:
        for group_id in mission_result["powerGroups"][team_id]:
            group = {"class": "SimGroup", "objectName": "Team%uPowerGroup%u" % (team_id, group_id), "children": mission_result["powerGroups"][team_id][group_id]}
            mission_result["teamPoweredGroups"][team_id]["children"].append(group)

    # Export the object list
    counter = 0
    file_name = "missions/%s.mis" % mission_result["mission"]
    while os.path.exists(file_name) is True:
        counter = counter + 1
        file_name = "missions/%s-%u.mis" % (mission_result["mission"], counter)

    with open(file_name, "w") as handle:
        handle.write("// DisplayName = %s\r\n" % mission_result["mission"])
        handle.write("// MissionTypes = CTF\r\n")
        handle.write("\r\n")

        handle.write("//--- OBJECT WRITE BEGIN ---\r\n")

        def recurse_scene(current, depth):
            declaration_tabbing = "".join(["\t"] * depth)
            attribute_tabbing = "".join(["\t"] * (depth + 1))
            for entity in current:
                name = ""
                if "objectName" in entity:
                    name = entity["objectName"]

                handle.write("%snew %s(%s) {\r\n" % (declaration_tabbing, entity["class"], name))

                # Dump all the keys
                for attribute in entity:
                    if attribute != "children" and attribute != "class" and attribute != "objectName":
                        handle.write("%s%s = \"%s\";\r\n" % (attribute_tabbing, attribute, entity[attribute]))

                if "children" in entity:
                    recurse_scene(entity["children"], depth + 1)

                handle.write("%s};\r\n" % declaration_tabbing)

        recurse_scene([mission_result["root"]], 0)

        handle.write("//--- OBJECT WRITE END ---")

def process_mission(self, signature, buffer, index):
    valid_commands = ["SCENERY", "INVEN", "WAYPOINT", "CAMERA", "POWER", "SWITCH", "SPAWN", "PICKUP", "WATERMARK",
    "BUILDING", "BOUNDS", "TERRAIN", "SKY", "FOG", "MUSIC", "ENVIRONMENT", "MISSION", "SUN", "TURRET", "VEHICLEPAD",
    "GENERATOR", "SENSOR"]

    comment_regex = re.compile("//.*")
    line_delineator_regex = re.compile("((\r\n|\n|\r|\n\r))*")

    searched_bytes = buffer[index:]

    mission_data = buffer[index:index + searched_bytes.find("\x0D\x0A\x00\x00")]
    mission_data = re.sub(comment_regex, "", mission_data)

    lines = line_delineator_regex.split(mission_data)

    commands = []
    current_command = []
    for line in lines:
        line = line.lstrip()

        # Filter anything that has garbled data
        try:
            test = line.encode("ascii")
        except UnicodeDecodeError as e:
            continue

        # Ignore Blank Lines
        if line == "":
            continue

        components = line.split()
        if components[0] in valid_commands:
            if len(current_command) != 0:
                commands.append(current_command)
            current_command = components
            continue

        current_command += components
    export_mission(commands)
