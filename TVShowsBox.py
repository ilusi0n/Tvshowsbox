#!/usr/bin/env python

import sys
import os.path
from sys import argv
import sqlite3

from os.path import expanduser
home = expanduser("~")
configFile = home + "/.config/TVShowsBox/TVShowsBox.conf"
configFolder = home + "/.config/TVShowsBox"
AnimeDB = 'Animes'
SeriesDB = 'Series'
WantedDB = 'Wanted'


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def printWarningMessage(message):
    return bcolors.WARNING + message + bcolors.ENDC


def printErrorMessage(message):
    return bcolors.FAIL + message + bcolors.ENDC


def printHeader(message):
    return bcolors.HEADER + message + bcolors.ENDC


def printBoldHeader(message):
    return bcolors.BOLD + bcolors.HEADER + message + bcolors.ENDC + bcolors.ENDC


def printBlue(message):
    return bcolors.BLUE + message + bcolors.ENDC


def printBoldBlue(message):
    return bcolors.BOLD + bcolors.BLUE + message + bcolors.ENDC + bcolors.ENDC


def printGreen(message):
    return bcolors.GREEN + message + bcolors.ENDC


def checkDatabase():
    database = getDataBaseName()
    if (database == ""):
        message = printErrorMessage("Error: Edit the configuration file and give the database a name")
        sys.exit(message)

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
            if databaseName == "":
                message = printErrorMessage(
                    "ERROR: You forgot to give a name to the database. Edit the configuration file")
                sys.exit(message)
            return "%s/.config/TVShowsBox/%s%s" % (home, databaseName, ".db")


def createDatabase():
    database = getDataBaseName()
    if (database == ""):
        message = printErrorMessage("Error: Edit the configuration file and give the database a name")
        sys.exit(message)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    sql = 'CREATE TABLE {tn} (Name text PRIMARY KEY, Season integer, Episode integer)'.format(tn=SeriesDB)
    c.execute(sql)
    sql = 'CREATE TABLE {tn} (Name text PRIMARY KEY, Episode integer)'.format(tn=AnimeDB)
    c.execute(sql)
    sql = 'CREATE TABLE {tn} (Name text PRIMARY KEY)'.format(tn=WantedDB)
    c.execute(sql)
    conn.commit()
    conn.close()


def searchEntry(name, tableName):
    database = getDataBaseName()
    result = True
    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql = "SELECT rowid FROM {tn} WHERE Name LIKE ?".format(tn=tableName)
    c.execute(sql, t)
    data = c.fetchall()
    if len(data) == 0:
        result = False
    conn.close()
    return result


#this entry must exist!
def getEntry(name, tableName):
    database = getDataBaseName()
    result = True
    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql = "SELECT * FROM {tn} WHERE Name = ?".format(tn=tableName)
    for row in c.execute(sql, t):
        result = row
    conn.close()
    return result


def createWantedEntry(args):
    database = getDataBaseName()
    name = " ".join(args)

    if searchEntry(name, WantedDB) == True:
        message = printErrorMessage("The %s is already wanted" % (name))
        sys.exit(message)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql = "INSERT INTO {tn} VALUES (?)".format(tn=WantedDB)
    c.execute(sql, t)
    conn.commit()
    conn.close()
    message = printHeader("%s was added to the wanted list" % (name))
    print(message)


def createAnimeEntry(args):
    database = getDataBaseName()
    name = " ".join(args)

    if searchEntry(name, AnimeDB) == True:
        message = printErrorMessage("The Anime %s already exists on the database" % (name))
        sys.exit(message)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql = "INSERT INTO {tn} VALUES (?,'0')".format(tn=AnimeDB)
    c.execute(sql, t)
    conn.commit()
    conn.close()
    message = printHeader("The Anime %s was added to the database" % (name))
    print(message)


def createEntry(args):
    database = getDataBaseName()
    name = " ".join(args)

    if searchEntry(name, SeriesDB) == True:
        message = printErrorMessage("The TV Show %s already exists on the database" % (name))
        sys.exit(message)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql = "INSERT INTO {tn} VALUES (?,'1','0')".format(tn=SeriesDB)
    c.execute(sql, t)
    conn.commit()
    conn.close()
    message = printHeader("The TV Show %s was added to the database" % (name))
    print(message)


def deleteEntry(args):
    database = getDataBaseName()
    name = " ".join(args)
    animeExists = searchEntry(name, AnimeDB)
    seriesExists = searchEntry(name, SeriesDB)

    if animeExists == False and seriesExists == False:
        message = printErrorMessage("ERROR: That TVShow or Anime called %s doesn't exist" % (name))
        sys.exit(message)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    if (animeExists == True):
        sql = "DELETE from {tn} WHERE Name = ?".format(tn=AnimeDB)
        c.execute(sql, t)
    else:
        sql = "DELETE from {tn} WHERE Name = ?".format(tn=SeriesDB)
        c.execute(sql, t)

    conn.commit()
    conn.close()
    message = printHeader("%s was deleted from the database" % (name))
    print(message)


def modifyEntry(args):
    database = getDataBaseName()
    name = " ".join(args)
    if searchEntry(name) == False:
        message = printErrorMessage("ERROR: That TV Show doesn't exist")
        print(message)
        return

    season = input(bcolors.BLUE + "Season: " + bcolors.ENDC)
    episode = input(bcolors.GREEN + "Episode: " + bcolors.ENDC)
    t = (season, episode, name,)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    sql = "UPDATE {tn} SET Season = ?, Episode = ?  WHERE Name = ?".format(tn=SeriesDB)
    c.execute(sql, t)
    conn.commit()
    conn.close()


def watchAnime(name):

    database = getDataBaseName()
    entry = getEntry(name, AnimeDB)
    name = entry[0]
    episode = entry[1]

    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (episode + 1, name,)
    sql = "UPDATE {tn} SET Episode = ?  WHERE Name = ?".format(tn=AnimeDB)
    c.execute(sql, t)
    conn.commit()
    conn.close()
    nEntry = getEntry(name, AnimeDB)
    episode = str(nEntry[1])
    print("")
    print(printWarningMessage("Update\n"))
    print(printHeader("Name: %s" % (name)))
    print(printGreen("Episode: %s\n" % (episode)))


def watchSerie(name):
    database = getDataBaseName()
    entry = getEntry(name, SeriesDB)
    name = entry[0]
    season = entry[1]
    episode = entry[2]

    print(printHeader("Name: %s" % (name)))
    print(printBlue("Season: %s" % (season)))
    print(printGreen("Episode: %s\n" % (episode)))

    response = input("New Season? (y/n): ")
    if response == "y":
        t = (season + 1, 1, name,)
    elif response == "n":
        t = (season, episode + 1, name,)
    else:
        message = printErrorMessage("ERROR: That answer is not valid. Aborting...")
        sys.exit(message)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    sql = "UPDATE {tn} SET Season = ?, Episode = ?  WHERE Name = ?".format(tn=SeriesDB)
    c.execute(sql, t)
    conn.commit()
    conn.close()
    nEntry = getEntry(name, SeriesDB)
    season = str(nEntry[1])
    episode = str(nEntry[2])
    print("")
    print(printWarningMessage("Update\n"))
    print(printHeader("Name: %s" % (name)))
    print(printBlue("Season: %s" % (season)))
    print(printGreen("Episode: %s\n" % (episode)))


def watchEntry(args):
    database = getDataBaseName()
    name = " ".join(args)
    seriesExists = searchEntry(name, SeriesDB)
    animeExists = searchEntry(name, AnimeDB)

    if seriesExists == False and animeExists == False:
        message = printErrorMessage("ERROR: That TV Show or Anime doesn't exist")
        sys.exit(message)

    if (seriesExists == True):
        watchSerie(name)
    else:
        watchAnime(name)


def listEntry(args):
    database = getDataBaseName()
    name = "%" + " ".join(args) + "%"
    animeExists = searchEntry(name, AnimeDB)
    seriesExists = searchEntry(name, SeriesDB)
    if animeExists == False and seriesExists == False:
        message = printWarningMessage("Warning: Database is empty")
        sys.exit(message)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)

    print("")
    print(printBoldBlue(AnimeDB + "\n"))

    if (animeExists == True):
        sql = 'SELECT * from {tn} WHERE Name LIKE ? ORDER BY Name'.format(tn=AnimeDB)
        for row in c.execute(sql, t):
            name = row[0]
            episode = str(row[1])
            print(printHeader("Name: %s" % (name)))
            print(printBlue("Episode: %s\n" % (episode)))
    else:
        print(printErrorMessage("No Animes on the database\n"))

    print(printBoldBlue(SeriesDB))
    print("")

    if (seriesExists == True):
        sql = 'SELECT * from {tn} WHERE Name LIKE ? ORDER BY Name'.format(tn=SeriesDB)
        for row in c.execute(sql, t):
            name = row[0]
            season = str(row[1])
            episode = str(row[2])
            print(printHeader("Name: %s" % (name)))
            print(printBlue("Season: %s" % (season)))
            print(printGreen("Episode: %s\n" % (episode)))
    else:
        print(printErrorMessage("No TV Shows on the database\n"))

    if (animeExists == True or seriesExists == True):
        conn.close()


def listWantedEntries(args):
    database = getDataBaseName()
    name = "%" + " ".join(args) + "%"
    wantedListExists = searchEntry(name, WantedDB)
    if wantedListExists == False:
        message = printWarningMessage("Warning: No Animes/TV Shows/Movies on wanted list")
        sys.exit(message)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)

    print("")
    print(printBoldBlue("Wanted List\n"))

    sql = 'SELECT * from {tn} WHERE Name LIKE ? ORDER BY Name'.format(tn=WantedDB)
    for row in c.execute(sql, t):
        name = row[0]
        print(printHeader("Name: %s" % (name)))

    if (wantedListExists == True):
        conn.close()


def showHelp():
    print(bcolors.HEADER + "TVShowsBox v0.1" + bcolors.ENDC)
    print("A script written in python that manages all your TV Shows in a sqlite database.\n")
    print("Options:")
    print("\taddTVShow \tNAME \tName of the TV Show \tAdd a TV Show")
    print("\taddAnime \tNAME \tName of the Anime \tAdd a Anime")
    print("\tedit, -e \tNAME SEASON EPISODE \tName of the show, Season number, Episode number \tEdit a TV Show")
    print("\tdelete, -d \tNAME \tName of the show \tDelete a TV Show")
    print("\tlist, -l \tNAME \tName of the show \tList a TV Show (it shows partial results)")
    print("\tlistAll, -la \tNAME \tName of the show \tList all the TV Shows")
    print("\twatch, -w \tNAME \tName of the show \tMark watch the next episode")
    print("\thelp, -h \tShow this information")


def main(argv):
    args = argv[1:]

    if len(args) == 0:
        message = printErrorMessage(
            "Error: It's required at least 1 argument. Use the -h or help to see which options are available")
        sys.exit(message)

    arg = args[0]
    args = args[1:]

    if not os.path.exists(configFolder):
        message = printErrorMessage(
            "Error: create the folder TVShowsBox and create the config file based on the example")
        sys.exit(message)

    if checkDatabase() == False:
        createDatabase()

    if args == "addTVShow":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name of the TV Show")
            sys.exit(message)
        createEntry(args)
        return

    if arg == "addAnime":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name of the Anime")
            sys.exit(message)
        createAnimeEntry(args)
        return

    if arg == "edit" or arg == "-e":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name of the TV Show")
            sys.exit(message)
        modifyEntry(args)
        return

    if arg == "delete" or arg == "-d":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name of the TV Show or Anime")
            sys.exit(message)
        deleteEntry(args)
        return

    if arg == "list" or arg == "-l":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name of the TV Show or the Anime")
            sys.exit(message)
        listEntry(args)
        return

    if arg == "listAll" or arg == "-la":
        if not (len(args) == 0):
            message = printErrorMessage("Error: This option doesn't take arguments")
            sys.exit(message)
        listEntry(args)
        return

    if arg == "listWanted" or arg == "-lw":
        if not (len(args) == 0):
            message = printErrorMessage("Error: This option doesn't take arguments")
            sys.exit(message)
        listWantedEntries(args)
        return

    if arg == "watch" or arg == "-w":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name of the TV Show or the Anime")
            sys.exit(message)
        watchEntry(args)
        return

    if arg == "want":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name of the TV Show or the Anime")
            sys.exit(message)
        createWantedEntry(args)
        return

    if arg == "help" or arg == "-h":
        showHelp()
        return

    if arg == "debug":
        getDataBaseName()
        sys.exit("nha")
        if checkDatabase() == False:
            createDatabase()
        return

    message = printErrorMessage("Error: Invalid Option! Use the -h or help to see which options are available")
    sys.exit(message)


if __name__ == "__main__":
    main(argv)
