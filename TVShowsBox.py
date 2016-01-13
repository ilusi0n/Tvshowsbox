#!/usr/bin/env python

###########################
# Developer: Hugo Cabrita #
###########################

import sys
import os.path
from sys import argv
import sqlite3
from clint.textui import puts, colored, indent, columns

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


def printBoldHeader(message):
    return bcolors.BOLD + bcolors.HEADER + message + bcolors.ENDC + bcolors.ENDC


def printBoldBlue(message):
    return bcolors.BOLD + bcolors.BLUE + message + bcolors.ENDC + bcolors.ENDC


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
        message = colored.red("The %s is already %s" % (name, table_name.lower()))
        sys.exit(message)

    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    t = (name,)

    if (searchEntry(name, SERIES_DB) or searchEntry(name, ANIME_DB)):
        sys.exit(colored.red("Error: You are already watching %s") % (name))

    if (table_name == SERIES_DB):
        sql = "INSERT INTO {tn} VALUES (?,'1','0')".format(tn=table_name)
    elif table_name == ANIME_DB:
        sql = "INSERT INTO {tn} VALUES (?,'0')".format(tn=table_name)
    else:
        sql = "INSERT INTO {tn} VALUES (?)".format(tn=table_name)

    c.execute(sql, t)
    conn.commit()
    conn.close()
    message = colored.cyan("%s was added to the %s list" % (name, table_name.lower()))

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
        sys.exit(colored.red("Error: %s doesn't exist" % (name)))

    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    t = (name,)
    sql = "DELETE from {tn} WHERE Name = ?".format(tn=table_name)
    nha = c.execute(sql, t)
    conn.commit()
    conn.close()

    if message:
        print(colored.cyan("%s was deleted from the %s list" % (name, table_name.lower())))


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
    puts(colored.yellow("Update:\n"))
    with indent(4):
        puts(colored.magenta("Name: %s" % (name)))
        puts(colored.green("Episode: %s\n" % (episode)))


def watchSerie(name):
    entry = getEntry(name, SERIES_DB)
    name = entry[0]
    season = entry[1]
    episode = entry[2]

    puts(colored.yellow("Current:\n"))
    with indent(4):
        puts(colored.magenta("Name: %s" % (name)))
        puts(colored.blue("Season: %s" % (season)))
        puts(colored.green("Episode: %s\n" % (episode)))

    response = input(colored.cyan("New Season? (y/n): "))
    if response == "y":
        t = (season + 1, 1, name,)
    elif response == "n":
        t = (season, episode + 1, name,)
    else:
        message = colored.red("Error: That answer is not valid. Aborting...")
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
    puts(colored.yellow("Update:\n"))
    with indent(4):
        puts(colored.magenta("Name: %s" % (name)))
        puts(colored.blue("Season: %s" % (season)))
        puts(colored.green("Episode: %s\n" % (episode)))


def watchEntry(args):
    name = " ".join(args)
    seriesExists = searchEntry(name, SERIES_DB)
    animeExists = searchEntry(name, ANIME_DB)

    if seriesExists == False and animeExists == False:
        message = colored.red("Error: That TV Show or Anime doesn't exist")
        sys.exit(message)

    if (seriesExists == True):
        watchSerie(name)
    else:
        watchAnime(name)


def listAnimes(args):
    name = "%" + "".join(args) + "%"
    animeExists = searchEntry(name, ANIME_DB)

    print("")
    puts(colored.blue(ANIME_DB + "\n"))

    if (animeExists == True):
        conn = sqlite3.connect(DATABASE_URL)
        c = conn.cursor()
        t = (name,)
        sql = 'SELECT * from {tn} WHERE Name LIKE ? ORDER BY Name'.format(tn=ANIME_DB)
        for row in c.execute(sql, t):
            name = row[0]
            episode = str(row[1])
            puts(colored.magenta("Name: %s" % (name)))
            puts(colored.green("Episode: %s\n" % (episode)))
        conn.close()

    else:
        if name == "":
            puts(colored.red("No Animes on the database\n"))
        else:
            puts(colored.red("No Animes with that name\n"))


def listSeries(args):
    name = "%" + "".join(args) + "%"
    seriesExists = searchEntry(name, SERIES_DB)

    puts(colored.blue(SERIES_DB) + "\n")

    if (seriesExists == True):
        conn = sqlite3.connect(DATABASE_URL)
        c = conn.cursor()
        t = (name,)
        sql = 'SELECT * from {tn} WHERE Name LIKE ? ORDER BY Name'.format(tn=SERIES_DB)
        for row in c.execute(sql, t):
            name = row[0]
            season = str(row[1])
            episode = str(row[2])
            puts(colored.magenta("Name: %s" % (name)))
            puts(colored.cyan("Season: %s" % (season)))
            puts(colored.green("Episode: %s\n" % (episode)))
        conn.close()
    else:
        if name == "":
            puts(colored.red("No TV Shows on the database\n"))
        else:
            puts(colored.red("No TV Shows with that name\n"))


def listWanted(args):
    name = "%" + " ".join(args) + "%"
    wantedListExists = searchEntry(name, WANTED_DB)
    if wantedListExists == False:
        message = colored.yellow("Warning: The wanted list is empty")
        sys.exit(message)

    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    t = (name,)

    print("")
    put(colored.cyan("Wanted List\n"))

    sql = 'SELECT * from {tn} WHERE Name LIKE ? ORDER BY Name'.format(tn=WANTED_DB)
    for row in c.execute(sql, t):
        name = row[0]
        print(colored.magenta("%s" % (name)))
    conn.close()


def showHelp():
    col1 = 17
    col2 = 20
    col3 = 80

    puts(columns([(colored.magenta('TVShowsBox v0.1')), col3]))
    puts(columns([('A script written in python that manages all your TV Shows in a sqlite database.'), col3]))
    print("")
    puts(columns([('Options:'), col3]))
    print("")
    puts(columns(['-add-TVShow', col1], ['NAME', col2], ['Add a TV Show', None]))
    puts(columns(['-add-anime', col1], ['NAME', col2], ['Add a Anime', None]))
    puts(columns(['-want, --aw', col1], ['NAME', col2], ['Add the Show to the Wanted List', None]))
    puts(columns(['-delete, --d', col1], ['NAME', col2], ['Delete a TV Show', None]))
    puts(columns(['-list, --l', col1], ['NAME', col2], ['List a TV Show (it shows partial results)', None]))
    puts(columns(['-list-all, --la', col1], ['NAME', col2], ['List all the TV Shows (except the wanted ones)', None]))
    puts(columns(['-list-wanted, --lw', col1], ['NAME', col2], ['List all the Shows on Wanted List', None]))
    puts(columns(['-watch, --w', col1], ['NAME', col2], ['Mark watch the next episode', None]))
    puts(columns(['-help, --h', col1], ['NAME', col2], ['Show this information', None]))


def main(argv):
    args = argv[1:]

    if not args:
        message = colored.red(
            "Error: It's required at least 1 argument. Use the -h or help to see which options are available")
        sys.exit(message)

    arg = args[0]
    args = args[1:]

    if not os.path.exists(CONFIG_FOLDER):
        message = colored.red("Error: create the folder TVShowsBox on your home directory")
        sys.exit(message)

    if checkDatabase() == False:
        createDatabase()

    if arg == "-add-TVShow":
        if not args:
            message = colored.red("Error: This option needs the name of the TV Show")
            sys.exit(message)
        createShow(args, SERIES_DB)
        return

    if arg == "-add-anime":
        if not args:
            message = colored.red("Error: This option needs the name of the Anime")
            sys.exit(message)
        createShow(args, ANIME_DB)
        return

    if arg == "-add-wanted" or arg == "--aw":
        if not args:
            message = colored.red("Error: This option needs the name Show")
            sys.exit(message)
        createShow(args, WANTED_DB)
        return

    if arg == "-delete" or arg == "--d":
        if not args:
            message = colored.red("Error: This option needs the name of Show")
            sys.exit(message)
        deleteShow(args, True)
        return

    if arg == "-list" or arg == "--l":
        if not args:
            message = colored.red("Error: This option needs the name of Show")
            sys.exit(message)
        listAnimes(args)
        listSeries(args)
        return

    if arg == "-list-all" or arg == "--la":
        if args:
            message = colored.red("Error: This option doesn't take arguments")
            sys.exit(message)
        listAnimes(args)
        listSeries(args)
        return

    if arg == "-list-wanted" or arg == "--lw":
        if args:
            message = colored.red("Error: This option doesn't take arguments")
            sys.exit(message)
        listWanted(args)
        return

    if arg == "-watch" or arg == "--w":
        if not args:
            message = colored.red("Error: This option needs the name of the Show")
            sys.exit(message)
        watchEntry(args)
        return

    if arg == "-help" or arg == "--h":
        showHelp()
        return

    message = colored.red("Error: Invalid Option! Use the -h or help to see which options are available")
    sys.exit(message)


if __name__ == "__main__":
    main(argv)
