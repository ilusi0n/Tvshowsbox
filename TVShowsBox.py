#!/usr/bin/env python

import sys
import os.path
from sys import argv
import sqlite3

from os.path import expanduser
home = expanduser("~")
configFile = home + "/.config/TVShowsBox/TVShowsBox.conf"
configFolder = home + "/.config/TVShowsBox"


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def checkDatabase():
    database = getDataBaseName()
    if (database == ""):
        sys.exit(bcolors.FAIL + "Error: Edit the configuration file and give the database a name" + bcolors.ENDC)

    return os.path.exists(database)


def getDataBaseName():
    with open(configFile, 'r') as inp:
        data = inp.readlines()

    for line in data:
        #print(line)
        if "#Database" in line:
            return ""
        if "Database=" in line:
            databaseName = line.replace("Database=", "").replace('"', "").strip()
            return home + "/.config/TVShowsBox/" + databaseName + ".db"


def createDatabase():
    database = getDataBaseName()
    if (database == ""):
        sys.exit(bcolors.FAIL + "Error: Edit the configuration file and give the database a name" + bcolors.ENDC)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute("CREATE TABLE watchingSeries (Name text, Season integer, Episode integer)")
    conn.commit()
    conn.close()


def searchEntry(name):
    database = getDataBaseName()
    result = True
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute("SELECT rowid FROM watchingSeries WHERE Name LIKE ?", (name,))
    data = c.fetchall()
    if len(data) == 0:
        result = False
    conn.close()
    return result


#this entry must exist!
def getEntry(name):
    database = getDataBaseName()
    result = True
    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql = "SELECT * FROM watchingSeries WHERE Name = ?"
    for row in c.execute(sql, t):
        result = row
    conn.close()
    return result


def createEntry(args):
    database = getDataBaseName()
    name = " ".join(args)
    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql = "INSERT INTO watchingSeries VALUES (?,'1','0')"
    c.execute(sql, t)
    conn.commit()
    conn.close()


def modifyEntry(args):
    database = getDataBaseName()
    name = " ".join(args)
    if searchEntry(name) == False:
        print(bcolors.FAIL + "ERROR: That entry doesn't exist" + bcolors.ENDC)
        return

    season = input(bcolors.BLUE + "Season: " + bcolors.ENDC)
    episode = input(bcolors.GREEN + "Episode: " + bcolors.ENDC)
    t = (season, episode, name,)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    sql = "UPDATE watchingSeries SET Season = ?, Episode = ?  WHERE Name = ?"
    c.execute(sql, t)
    conn.commit()
    conn.close()


def watchEntry(args):
    database = getDataBaseName()
    name = " ".join(args)
    if searchEntry(name) == False:
        print(bcolors.FAIL + "ERROR: That entry doesn't exist" + bcolors.ENDC)
        return

    entry = getEntry(name)
    name = entry[0]
    season = entry[1]
    episode = entry[2]

    print(bcolors.HEADER + "Name: " + name + bcolors.ENDC)
    print(bcolors.BLUE + "Season: " + str(season) + bcolors.ENDC)
    print(bcolors.GREEN + "Episode: " + str(episode) + bcolors.ENDC)
    print("")

    response = input("New Season? (y/n): ")
    if response == "y":
        t = (season + 1, 1, name,)
    elif response == "n":
        t = (season, episode + 1, name,)
    else:
        sys.exit(bcolors.FAIL + "ERROR: That answer is not valid. Aborting..." + bcolors.ENDC)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    sql = "UPDATE watchingSeries SET Season = ?, Episode = ?  WHERE Name = ?"
    c.execute(sql, t)
    conn.commit()
    conn.close()
    nEntry = getEntry(name)
    season = str(nEntry[1])
    episode = str(nEntry[2])
    print("")
    print(bcolors.WARNING + "Update" + bcolors.ENDC)
    print("")
    print(bcolors.HEADER + "\tName: " + name + bcolors.ENDC)
    print(bcolors.BLUE + "\tSeason: " + season + bcolors.ENDC)
    print(bcolors.GREEN + "\tEpisode: " + episode + bcolors.ENDC)
    print("")


def deleteEntry(args):
    database = getDataBaseName()
    name = " ".join(args)
    if searchEntry(name) == False:
        print(bcolors.FAIL + "ERROR: That entry doesn't exist" + bcolors.ENDC)
        return

    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql = "DELETE from watchingSeries WHERE Name = ?"
    c.execute(sql, t)
    conn.commit()
    conn.close()


def listEntry(args):
    database = getDataBaseName()
    name = "%" + " ".join(args) + "%"
    if searchEntry(name) == False:
        print(bcolors.FAIL + "ERROR: That entry doesn't exist" + bcolors.ENDC)
        return

    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql = "SELECT * from watchingSeries WHERE Name LIKE ? ORDER BY Name"
    print("")
    for row in c.execute(sql, t):
        name = row[0]
        season = str(row[1])
        episode = str(row[2])
        print(bcolors.HEADER + "Name: " + name + bcolors.ENDC)
        print(bcolors.BLUE + "Season: " + season + bcolors.ENDC)
        print(bcolors.GREEN + "Episode: " + episode + bcolors.ENDC)
        print("")
    conn.close()


def showHelp():
    print(bcolors.HEADER + "TVShowsBox v0.1" + bcolors.ENDC)
    print("A script written in python that manages all your TV Shows in a sqlite database.")
    print("")
    print("Options:")
    print("\tadd, -a \tNAME \tName of the show \tAdd a TV show")
    print("\tedit, -e \tNAME SEASON EPISODE \tName of the show, Season number, Episode number \tEdit a TV Show")
    print("\tdelete, -d \tNAME \tName of the show \tDelete a TV Show")
    print("\tlist, -l \tNAME \tName of the show \tList a TV Show (it shows partial results)")
    print("\tlistAll, -la \tNAME \tName of the show \tList all the TV Shows")
    print("\twatch, -w \tNAME \tName of the show \tMark watch the next episode")
    print("\thelp, -h \tShow this information")


def main(argv):
    args = argv[1:]

    if len(args) == 0:
        print(bcolors.FAIL +
              "Error: It's required at least 1 argument. Use the -h or help to see which options are available" +
              bcolors.ENDC)
        return

    arg = args[0]
    args = args[1:]

    if not os.path.exists(configFolder):
        sys.exit(bcolors.FAIL + "Error: create the folder TVShowsBox and create the config file based on the example" +
                 bcolors.ENDC)

    if checkDatabase() == False:
        createDatabase()

    if arg == "add" or arg == "-a":
        if not (len(args) > 0):
            sys.exit(bcolors.FAIL + "Error: This option needs the name of the TV Show" + bcolors.ENDC)
        listEntry(args)
        createEntry(args)
        return

    if arg == "edit" or arg == "-e":
        if not (len(args) > 0):
            sys.exit(bcolors.FAIL + "Error: This option needs the name of the TV Show" + bcolors.ENDC)
        listEntry(args)
        modifyEntry(args)
        return

    if arg == "delete" or arg == "-d":
        if not (len(args) > 0):
            sys.exit(bcolors.FAIL + "Error: This option needs the name of the TV Show" + bcolors.ENDC)
        listEntry(args)
        deleteEntry(args)
        return

    if arg == "list" or arg == "-l":
        if not (len(args) > 0):
            sys.exit(bcolors.FAIL + "Error: This option needs the name of the TV Show" + bcolors.ENDC)
        listEntry(args)
        return

    if arg == "listAll" or arg == "-la":
        if not (len(args) == 0):
            sys.exit(bcolors.FAIL + "Error: This option doesn't take arguments" + bcolors.ENDC)
        listEntry(args)
        return

    if arg == "watch" or arg == "-w":
        if not (len(args) > 0):
            sys.exit(bcolors.FAIL + "Error: This option needs the name of the TV Show" + bcolors.ENDC)
        listEntry(args)
        watchEntry(args)
        return

    if arg == "help" or arg == "-h":
        showHelp()
        return

    if arg == "debug":
        if checkDatabase() == False:
            createDatabase()
        return

    print("Invalid Option!")


if __name__ == "__main__":
    main(argv)
