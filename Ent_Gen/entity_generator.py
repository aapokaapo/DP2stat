def get_spawns(path, map_name) -> list():
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
    for idx, line in enumerate(lines):
        if map_name in line:
            matching = True
            linez = list()
            for i in range(1,5):
                if not lines[idx+i].startswith(line_starts[i-1]):
                    matching = False
            if matching:
                for i in range(5):
                    linez.append(lines[idx+i])
                ent_lines.append(linez)

    # create lines that represent info_player_deathmatch'es
    spawns = list()
    print(ent_lines)
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
        origin = f"{origin[0]} {origin[1]} {origin[2]}"
        print(f"id: {id}, rotation:{rotation}, origin: {origin}")
        # Append items player should start with
        local_spawns.append(f'"origin" "{origin}"')
        local_spawns.append(f'"angle" "{rotation}"')
        local_spawns.append(f'"_loc_id" "{id}"')
        local_spawns.append(f'"giveammo" "200"')
        local_spawns.append(f'"givebarrel" "brass"')
        local_spawns.append(f'"givehopper" "200"')
        local_spawns.append(f'"givegun" "stingray"')
        local_spawns.append(f'"loadedco2" "20oz"')
        local_spawns.append('}')
        spawns.append(local_spawns)

        # Some optional print lines
        for line in lines:
            print(line)
        print(spawns)
    return spawns


def get_old_entities(path, message_attachment) -> list():
    """
    Gets entity block from mapfile, alters worldspawn towards DM/TDM and removes info_player_deathmatches
    :param path: path to map file
    :param message_attachment: adds a substring to worldspawn message indicating the edited entities
    :return: string list of entities as they would be stored in a regular .bsp / .ent
    """
    with open(path, "rb") as f:  # bsps are binary files
        bytes1 = f.read() # stores all bytes in bytes1 variable (named like that to not interfere with builtin names
        # get offset (position of entity block begin) and length of entity block -> see bsp quake 2 format documentation
        offset = int.from_bytes(bytes1[8:12], byteorder='little', signed=False)
        length = int.from_bytes(bytes1[12:16], byteorder='little', signed=False)
        # Decode entity block to ascii / regular string
        lines = (bytes1[offset:offset+length-1].decode("ascii", "ignore"))
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
                ents[0][idx] = line[0:len(line)-1] + message_attachment + '"'
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
        ents = [x for x in ents if not '"classname" "info_player_deathmatch"' in x] # removes info_player_deathmatches
        print(ents)
        return ents


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
                f.write(line+"\n")
