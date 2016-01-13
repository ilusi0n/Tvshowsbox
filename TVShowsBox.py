#!/usr/bin/env python

###########################
# Developer: Hugo Cabrita #
###########################

import sys
import os.path
from sys import argv
import sqlite3

from os.path import expanduser
home = expanduser("~")
CONFIG_FOLDER = home + '/.config/TVShowsBox'
DATABASE_URL = CONFIG_FOLDER + '/tvshows.db'
ANIME_DB = 'Animes'
SERIES_DB = 'Series'
WANTED_DB = 'Wanted'


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
    return os.path.exists(DATABASE_URL)


def createDatabase():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    sql = 'CREATE TABLE {tn} (Name text PRIMARY KEY, Season integer, Episode integer)'.format(tn=SERIES_DB)
    c.execute(sql)
    sql = 'CREATE TABLE {tn} (Name text PRIMARY KEY, Episode integer)'.format(tn=ANIME_DB)
    c.execute(sql)
    sql = 'CREATE TABLE {tn} (Name text PRIMARY KEY)'.format(tn=WANTED_DB)
    c.execute(sql)
    conn.commit()
    conn.close()


def searchEntry(name, table_name):
    result = True
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    t = (name,)
    sql = "SELECT rowid FROM {tn} WHERE Name LIKE ?".format(tn=table_name)
    c.execute(sql, t)
    data = c.fetchall()
    if len(data) == 0:
        result = False
    conn.close()
    return result


def getEntry(name, table_name):
    result = True
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    t = (name,)
    sql = "SELECT * FROM {tn} WHERE Name = ?".format(tn=table_name)
    for row in c.execute(sql, t):
        result = row
    conn.close()
    return result


def createShow(args, table_name):
    name = " ".join(args)
    if searchEntry(name, table_name) == True:
        message = printErrorMessage("The %s is already %s" % (name, table_name.lower()))
        sys.exit(message)

    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    t = (name,)

    if (searchEntry(name, SERIES_DB) or searchEntry(name, ANIME_DB)):
        sys.exit(printErrorMessage("Error: You are already watching %s") % (name))

    if (table_name == SERIES_DB):
        sql = "INSERT INTO {tn} VALUES (?,'1','0')".format(tn=table_name)
    elif table_name == ANIME_DB:
        sql = "INSERT INTO {tn} VALUES (?,'0')".format(tn=table_name)
    else:
        sql = "INSERT INTO {tn} VALUES (?)".format(tn=table_name)

    c.execute(sql, t)
    conn.commit()
    conn.close()
    message = printHeader("%s was added to the %s list" % (name, table_name.lower()))

    if (table_name != WANTED_DB):
        deleteShow(name, False)

    print(message)


def deleteShow(name, message):
    name = " ".join(name)
    table_name = ""

    if searchEntry(name, SERIES_DB):
        table_name = SERIES_DB
    elif searchEntry(name, ANIME_DB):
        table_name = ANIME_DB
    else:
        table_name = WANTED_DB

    if table_name == "" and message == True:
        sys.exit(printErrorMessage("Error: %s doesn't exist" % (name)))

    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    t = (name,)
    sql = "DELETE from {tn} WHERE Name = ?".format(tn=table_name)
    nha = c.execute(sql, t)
    conn.commit()
    conn.close()

    if message:
        print(printHeader("%s was deleted from the %s list" % (name, table_name.lower())))


def modifyEntry(args):
    name = " ".join(args)
    if searchEntry(name) == False:
        message = printErrorMessage("Error: That TV Show doesn't exist")
        print(message)
        return

    season = input(bcolors.BLUE + "Season: " + bcolors.ENDC)
    episode = input(bcolors.GREEN + "Episode: " + bcolors.ENDC)
    t = (season, episode, name,)

    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    sql = "UPDATE {tn} SET Season = ?, Episode = ?  WHERE Name = ?".format(tn=SERIES_DB)
    c.execute(sql, t)
    conn.commit()
    conn.close()


def watchAnime(name):
    entry = getEntry(name, ANIME_DB)
    name = entry[0]
    episode = entry[1]

    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    t = (episode + 1, name,)
    sql = "UPDATE {tn} SET Episode = ?  WHERE Name = ?".format(tn=ANIME_DB)
    c.execute(sql, t)
    conn.commit()
    conn.close()
    nEntry = getEntry(name, ANIME_DB)
    episode = str(nEntry[1])
    print("")
    print(printWarningMessage("Update\n"))
    print(printHeader("Name: %s" % (name)))
    print(printGreen("Episode: %s\n" % (episode)))


def watchSerie(name):
    entry = getEntry(name, SERIES_DB)
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
        message = printErrorMessage("Error: That answer is not valid. Aborting...")
        sys.exit(message)

    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    sql = "UPDATE {tn} SET Season = ?, Episode = ?  WHERE Name = ?".format(tn=SERIES_DB)
    c.execute(sql, t)
    conn.commit()
    conn.close()
    nEntry = getEntry(name, SERIES_DB)
    season = str(nEntry[1])
    episode = str(nEntry[2])
    print("")
    print(printWarningMessage("Update\n"))
    print(printHeader("Name: %s" % (name)))
    print(printBlue("Season: %s" % (season)))
    print(printGreen("Episode: %s\n" % (episode)))


def watchEntry(args):
    name = " ".join(args)
    seriesExists = searchEntry(name, SERIES_DB)
    animeExists = searchEntry(name, ANIME_DB)

    if seriesExists == False and animeExists == False:
        message = printErrorMessage("Error: That TV Show or Anime doesn't exist")
        sys.exit(message)

    if (seriesExists == True):
        watchSerie(name)
    else:
        watchAnime(name)


def listAnimes(args):
    name = "%" + "".join(args) + "%"
    animeExists = searchEntry(name, ANIME_DB)

    print("")
    print(printBoldBlue(ANIME_DB + "\n"))

    if (animeExists == True):
        conn = sqlite3.connect(DATABASE_URL)
        c = conn.cursor()
        t = (name,)
        sql = 'SELECT * from {tn} WHERE Name LIKE ? ORDER BY Name'.format(tn=ANIME_DB)
        for row in c.execute(sql, t):
            name = row[0]
            episode = str(row[1])
            print(printHeader("Name: %s" % (name)))
            print(printBlue("Episode: %s\n" % (episode)))
        conn.close()

    else:
        if name == "":
            print(printErrorMessage("No Animes on the database\n"))
        else:
            print(printErrorMessage("No Animes with that name\n"))


def listSeries(args):
    name = "%" + "".join(args) + "%"
    seriesExists = searchEntry(name, SERIES_DB)

    print(printBoldBlue(SERIES_DB) + "\n")

    if (seriesExists == True):
        conn = sqlite3.connect(DATABASE_URL)
        c = conn.cursor()
        t = (name,)
        sql = 'SELECT * from {tn} WHERE Name LIKE ? ORDER BY Name'.format(tn=SERIES_DB)
        for row in c.execute(sql, t):
            name = row[0]
            season = str(row[1])
            episode = str(row[2])
            print(printHeader("Name: %s" % (name)))
            print(printBlue("Season: %s" % (season)))
            print(printGreen("Episode: %s\n" % (episode)))
        conn.close()
    else:
        if name == "":
            print(printErrorMessage("No TV Shows on the database\n"))
        else:
            print(printErrorMessage("No TV Shows with that name\n"))


def listWanted(args):
    name = "%" + " ".join(args) + "%"
    wantedListExists = searchEntry(name, WANTED_DB)
    if wantedListExists == False:
        message = printWarningMessage("Warning: The wanted list is empty")
        sys.exit(message)

    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    t = (name,)

    print("")
    print(printBoldBlue("Wanted List\n"))

    sql = 'SELECT * from {tn} WHERE Name LIKE ? ORDER BY Name'.format(tn=WANTED_DB)
    for row in c.execute(sql, t):
        name = row[0]
        print(printHeader("%s" % (name)))
    conn.close()


def showHelp():
    print(bcolors.HEADER + "TVShowsBox v0.1" + bcolors.ENDC)
    print("A script written in python that manages all your TV Shows in a sqlite database.\n")
    print("Options:")
    print("\tadd-TVShow \tNAME \tName of the TV Show \tAdd a TV Show")
    print("\tadd-anime \tNAME \tName of the Anime \tAdd a Anime")
    print("\twant, -aw \tNAME \tName of the show \tAdd the Show to the Wanted List")
    print("\tedit, -e \tNAME SEASON EPISODE \tName of the show, Season number, Episode number \tEdit a TV Show")
    print("\tdelete, -d \tNAME \tName of the show \tDelete a TV Show")
    print("\tlist, -l \tNAME \tName of the show \tList a TV Show (it shows partial results)")
    print("\tlist-all, -la \tNAME \tName of the show \tList all the TV Shows (except the wanted ones)")
    print("\tlist-wanted, -lw \tNAME \tName of the show \tList all the Shows on Wanted List")
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

    if not os.path.exists(CONFIG_FOLDER):
        message = printErrorMessage("Error: create the folder TVShowsBox on your home directory")
        sys.exit(message)

    if checkDatabase() == False:
        createDatabase()

    if arg == "add-TVShow":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name of the TV Show")
            sys.exit(message)
        createShow(args, SERIES_DB)
        return

    if arg == "add-anime":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name of the Anime")
            sys.exit(message)
        createShow(args, ANIME_DB)
        return

    if arg == "add-wanted" or arg == "-aw":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name Show")
            sys.exit(message)
        createShow(args, WANTED_DB)
        return

    if arg == "edit" or arg == "-e":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name of Show")
            sys.exit(message)
        modifyEntry(args)
        return

    if arg == "delete" or arg == "-d":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name of Show")
            sys.exit(message)
        deleteShow(args, True)
        return

    if arg == "list" or arg == "-l":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name of Show")
            sys.exit(message)
        listAnimes(args)
        listSeries(args)
        return

    if arg == "list-all" or arg == "-la":
        if not (len(args) == 0):
            message = printErrorMessage("Error: This option doesn't take arguments")
            sys.exit(message)
        listAnimes(args)
        listSeries(args)
        return

    if arg == "list-wanted" or arg == "-lw":
        if not (len(args) == 0):
            message = printErrorMessage("Error: This option doesn't take arguments")
            sys.exit(message)
        listWanted(args)
        return

    if arg == "watch" or arg == "-w":
        if not (len(args) > 0):
            message = printErrorMessage("Error: This option needs the name of the Show")
            sys.exit(message)
        watchEntry(args)
        return

    if arg == "help" or arg == "-h":
        showHelp()
        return

    message = printErrorMessage("Error: Invalid Option! Use the -h or help to see which options are available")
    sys.exit(message)


if __name__ == "__main__":
    main(argv)
