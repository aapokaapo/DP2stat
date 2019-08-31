import os

# def get_spawns_from_ent(path):
#     print("hi")


def get_spawns_from_log(path, map_name, loc_path) -> list():
    """
    Iterates through log file created in dp
    Searches 5 line code blocks starting with defined words
    translates these into bsp compatible entity lines
    :param path: location of log
    :param map_name: name of map (without directories)
    :return: lines of new info_player_deathmatch entities
    """
    # line beginnings to look for
    line_starts = ["Location", "Old Position", "Position", "Angles", "_sun_angle"]

    # get all lines within the log
    lines = list()
    with open(path) as f:
        for line in f:
            lines.append(line.replace("\n", ""))

    # get all lines containing info to create a spawn (defined in line_starts)
    ent_lines = list()
    # print(ent_lines)
    remove_spawns = list()
    default_keyvalues = list()
    default_keys = ["loadedco2", "giveco2", "giveammo", "givegun", "givebarrel", "givehopper"]
    default_spawnkeys = {"loadedco2":0, "giveco2":0, "giveammo":50, "givegun": 0, "givebarrel": "brass", "givehopper":0}
#$default_loadedco2 $default_giveco2 $default_ammo $default_gun $default_barrel $default_hopper
    keys = {}
    for idx, line in enumerate(lines):
        # print(f"{line} - {'EntGenDefaults' in line}")
        if map_name in line:
            if "EntGenDefaults:" in line:
                default_keyvalues = line.split(" ")[line.split(" ").index("EntGenDefaults:")+1:len(line.split(" "))-2]
                default_spawnkeys = dict(zip(default_keys, default_keyvalues))
                print(default_spawnkeys)
            if "SetKey" in line:
                print(line)
                loc=(line.split(" ")[line.split(" ").index("SetKey")+1])
                key = (line.split(" ")[line.split(" ").index("SetKey")+2])
                value = (line.split(" ")[line.split(" ").index("SetKey")+3])
                try:
                    keys[loc][key]=value
                except KeyError:
                    keys[loc] = {key:value}
            if "RemoveSpawn" in line:
                print(line)
                remove_spawns.append(line.split(" ")[line.split(" ").index("RemoveSpawn")+1])
                print(line.split(" ")[line.split(" ").index("RemoveSpawn")+1])
            matching = True
            linez = list()
            for i in range(1,5):
                if idx+i >= len(lines):
                    matching=False
                    break
                if not lines[idx+i].startswith(line_starts[i-1]):
                    matching = False
            if matching:
                for i in range(5):
                    linez.append(lines[idx+i])
                ent_lines.append(linez)
    print("keys:")
    print(keys)
    # create lines that represent info_player_deathmatch'es
    spawns = list()
    print(f" Remove spawns {remove_spawns}")
    old_loc_lines=list()

    # with open(loc_path+map_name+".loc", "r") as loc:
    #     old_loc_lines=loc.read()
    #     if old_loc_lines:
    #         old_loc_lines=old_loc_lines.split("\n")
    #         old_loc_lines.pop(len(old_loc_lines)-1)
    #         with open(loc_path+map_name+".loc", "w") as loc2:
    #             for idx, l in enumerate(old_loc_lines):
    #                 print(l)
    #                 print(f" -- {l.split(' ')[3] not in remove_spawns}")
    #                 if l.split(" ")[3] not in remove_spawns:
    #                     loc2.write(l+"\n")
    print(ent_lines)
    loc_lines=list()
    for lines in ent_lines:
        local_spawns = list()
        local_spawns.append('{')
        local_spawns.append('"teamnumber" "0"') # Spawn can be used by all teams if mode it TDM
        local_spawns.append('"classname" "info_player_deathmatch"') # Entity class

        # get loc id generated by cvar_inc in game
        id=lines[1].split(" ")[1].replace("'", "")
        # translate 'angles' output (from -180 to 180) to range from 0 to 360 by shifting angles < 0
        rotation=round(float(lines[4].split(" ")[1]))
        if rotation <0:
            rotation += 360
        # get coordinates from 'pos' output
        coordinates = lines[3].split(" ")
        origin = [round(float(coordinates[i])) for i in range(1,4)]
        loc_origin = f"{origin[0]*8} {origin[1]*8} {origin[2]*8}"
        origin = f"{origin[0]} {origin[1]} {origin[2]}"
        loc_line=loc_origin+" "+id
        loc_lines.append(loc_line)
        # print(loc_line)
        # print(f"id: {id}, rotation:{rotation}, origin: {origin}")
        # Append items player should start with
        local_spawns.append(f'"origin" "{origin}"')
        local_spawns.append(f'"angle" "{rotation}"')
        local_spawns.append(f'"_loc_id" "{id}"')
        print(id in keys)
        # print("giveammo" in keys[id])
        # ammo_val = default_spawnkeys["giveammo"]
        # if id in keys and "giveammo" in keys[id]:
        #     ammo_val = keys[id]["giveammo"]
        # print(keys[id]["giveammo1"] if id in keys and "giveammo2" in keys[id] else default_spawnkeys["giveammo"])
        for default_key in default_keys:
            print(keys[id] if id in keys else default_spawnkeys[default_key])
            print(default_spawnkeys[default_key])
            print(id in keys and default_key in keys[id] and not keys[id][default_key] == "0" and default_spawnkeys[default_key] and not default_spawnkeys[default_key]=="0")
            if id in keys and default_key in keys[id] and not keys[id][default_key] == "0" and default_spawnkeys[default_key] and not default_spawnkeys[default_key]=="0":
                print(f' lol{id} - {keys[id][default_key]=="0"} - {keys[id][default_key]}')
                local_spawns.append(f'"{default_key}" "{keys[id][default_key] if id in keys and default_key in keys[id] else default_spawnkeys[default_key]}"')
            # local_spawns.append(f'"givebarrel" "{keys[id]["givebarrel"] if id in keys and "givebarrel" in keys[id] else default_spawnkeys["givebarrel"]}"')
            # local_spawns.append(f'"givehopper" "{keys[id]["givehopper"] if id in keys and "givehopper" in keys[id] else default_spawnkeys["givehopper"]}"')
            # local_spawns.append(f'"givegun" "{keys[id]["givegun"] if id in keys and "givegun" in keys[id] else default_spawnkeys["givegun"]}"')
            # local_spawns.append(f'"loadedco2" "{keys[id]["loadedco2"] if id in keys and "loadedco2" in keys[id] else default_spawnkeys["loadedco2"]}"')
            # local_spawns.append(f'"giveco2" "{keys[id]["giveco2"] if id in keys and "giveco2" in keys[id] else default_spawnkeys["giveco2"]}"')
            # local_spawns.append('}')
        spawns.append(local_spawns)
        print("omg")
    #     # Some optional print lines
    #     for line in lines:
    #         print(line)
    #     print(spawns)
    # print(loc_lines)
    with open(loc_path+map_name+".loc", "w") as f2:
        for loc_line in loc_lines:
            f2.write(loc_line+"\n")
    return spawns, remove_spawns, keys


def get_old_entities(path, message_attachment, remove_spawns, loc_path, map_name, keys) -> list():
    """
    Gets entity block from mapfile, alters worldspawn towards DM/TDM and removes info_player_deathmatches
    :param path: path to map file
    :param message_attachment: adds a substring to worldspawn message indicating the edited entities
    :return: string list of entities as they would be stored in a regular .bsp / .ent
    """
    is_ent=False
    with open(path+".bsp", "rb") as f:  # bsps are binary files
        bytes1 = f.read() # stores all bytes in bytes1 variable (named like that to not interfere with builtin names
        # get offset (position of entity block begin) and length of entity block -> see bsp quake 2 format documentation
        offset = int.from_bytes(bytes1[8:12], byteorder='little', signed=False)
        length = int.from_bytes(bytes1[12:16], byteorder='little', signed=False)
        # Decode entity block to ascii / regular string
        lines = (bytes1[offset:offset+length-1].decode("ascii", "ignore"))
        # print(lines)
        if os.path.isfile(path+".ent"):
            is_ent=True
            with open(path+".ent", "r") as f2:
                lines=f2.read()
                print("ent")
                # print((lines))
        else:
            print("not ent")
            # print(lines)
            # old_spawns = ent_gen.get_spawns_from_ent(path+map+".ent")

        lines = lines.split("\n")
        print(lines)
        print(len(lines))

        # fill list of strings describing one entity and append it to list containing all entities + wipe that list
        ents = list()
        localents = list()
        for i in range(len(lines)):
            localents.append(lines[i])
            if lines[i] == "}":
                ents.append(localents)
                localents = list()

        # Iterate through worldspawn (first entity- maps could in theory have a different entity order!)
        # If it contains a gamemode- change it to DM/TDM, if not- add it. also change other settings towards DM/TDM
        contains_gamemode = False
        for idx, line in enumerate(ents[0]):
            if line.startswith('"message"'):
                if not is_ent:
                    ents[0][idx] = line[0:len(line)-1] + message_attachment + '"'
                else:
                    ents[0][idx] = line[0:len(line)-1] + '"'
            elif line.startswith('"gamemode"'):
                ents[0][idx] = line[0:12]+'1"'
                contains_gamemode = True
            elif line.startswith('"teamnumber"'):
                ents[0][idx] = ""
            elif line.startswith('"maxteams"'):
                ents[0][idx] = ""
            elif line.startswith('"team'):
                ents[0][idx] = ""
        if not contains_gamemode:
            ents[0].append(ents[0][len(ents[0])-1])
            ents[0][len(ents[0])-2] = '"gamemode" "1"'
        ents[0] = [x for x in ents[0] if x] # removes empty lines
        if not is_ent:
            ents = [x for x in ents if not '"classname" "info_player_deathmatch"' in x] # removes info_player_deathmatches
            return ents, is_ent
        else:
            test=([ [(y.replace('"', "").split(" ")[1]) in remove_spawns for y in x if "_loc_id" in y] for x in ents])
            test=[x for x in test if x]
            print(f"test - {test}")
            ents2 = list()
            old_loc_lines = list()
            loc_id = -1
            for idx1,x in enumerate(ents):
                to_remove = False
                for y in x:
                    if "_loc_id" in y:
                        loc_id = y.replace('"', "").split(" ")[1]
                        if loc_id in keys:
                            for idx2, z in enumerate(x):
                                for key in keys[loc_id]:
                                    if key in z and not keys[loc_id][key] == 0:
                                        print(keys[loc_id][key])
                                        print(keys[loc_id][key]==0)
                                        ents[idx1][idx2] = '"'+key+'" "'+ keys[loc_id][key] + '"'
                            print(keys[loc_id])
                        if ((loc_id) in remove_spawns):
                            to_remove = True
                if not to_remove:
                    # for idx, y in enumerate(x):
                    #     if not
                    ents2.append(x)
                    if '"classname" "info_player_deathmatch"' in x:
                        print(f"here: \n{x}")
                        origin=[str(int(y)*8) for y in x[3].replace('"', "").split(" ")[1:4]]
                        loc_line = " ".join(origin)+" "+x[5].replace('"', "").split(" ")[1]
                        old_loc_lines.append(loc_line)
            with open(loc_path + map_name + ".loc", "a") as f2:
                for old_line in old_loc_lines:
                    f2.write(old_line+"\n")
                return ents2, is_ent
            # ents = [x for x in ents if not [(y.replace('"', "").split(" ")[1]) in remove_spawns for y in x if "_loc_id" in y]] # removes info_player_deathmatches
        # print(ents)


def save_ent(old_ents, new_ents, path) -> None:
    """
    firstly writes old entities then writes new spawns
    :param old_ents: original entities: edited worldspawn and no old spawns
    :param new_ents: newly created info_player_deathmatches
    :param path: where to save the entity to
    :return: None
    """
    with open(path, "w") as f:
        for ent in old_ents:
            for line in ent:
                f.write(line+"\n")
        for ent in new_ents:
            for line in ent:
                print(line+"\n")
                f.write(line+"\n")
