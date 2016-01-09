#!/usr/bin/env python
from sys import argv
import sqlite3

database="tvshows.db"

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def searchEntry(name):
    result=True
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute("SELECT rowid FROM watchingSeries WHERE Name LIKE ?", (name,))
    data=c.fetchall()
    if len(data)==0:
        result=False
    conn.close()
    return result

#this entry must exist!
def getEntry(name):
    result=True
    conn = sqlite3.connect(database)
    c = conn.cursor()
    t=(name,)
    sql = "SELECT * FROM watchingSeries WHERE Name = ?"
    for row in c.execute(sql,t):
        result = row
    conn.close()
    return result


def createEntry(args):
    name=" ".join(args)
    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql="INSERT INTO watchingSeries VALUES (?,'1','0')"
    c.execute(sql,t)
    conn.commit()
    conn.close()

def modifyEntry(args):
    name=" ".join(args)
    if searchEntry(name)==False:
        print(bcolors.FAIL + "ERROR: That entry doesn't exist" + bcolors.ENDC)
        return

    season = input(bcolors.BLUE + "Season: " + bcolors.ENDC)
    episode = input(bcolors.GREEN + "Episode: " + bcolors.ENDC)
    t = (season,episode,name,)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    sql = "UPDATE watchingSeries SET Season = ?, Episode = ?  WHERE Name = ?"
    c.execute(sql,t)
    conn.commit()
    conn.close()

def watchEntry(args):
    name=" ".join(args)
    if searchEntry(name)==False:
        print(bcolors.FAIL + "ERROR: That entry doesn't exist" + bcolors.ENDC)
        return

    entry=getEntry(name)
    name = entry[0]
    season = entry[1]
    episode = entry[2]

    print(bcolors.HEADER + "Name: "+name + bcolors.ENDC)
    print(bcolors.BLUE + "Season: "+str(season) + bcolors.ENDC)
    print(bcolors.GREEN + "Episode: "+str(episode) + bcolors.ENDC)
    print("")

    response = input("New Season? (y/n): ")
    if response == "y":
        t = (season+1,1,name,)
    else:
        t = (season,episode+1,name,)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    sql = "UPDATE watchingSeries SET Season = ?, Episode = ?  WHERE Name = ?"
    c.execute(sql,t)
    conn.commit()
    conn.close()
    nEntry=getEntry(name)
    season = str(nEntry[1])
    episode = str(nEntry[2])
    print("")
    print("Update")
    print(bcolors.HEADER + "Name: "+name + bcolors.ENDC)
    print(bcolors.BLUE + "Season: "+season + bcolors.ENDC)
    print(bcolors.GREEN + "Episode: "+episode + bcolors.ENDC)
    print("")

def deleteEntry(args):
    name=" ".join(args)
    if searchEntry(name)==False:
        print(bcolors.FAIL + "ERROR: That entry doesn't exist" + bcolors.ENDC)
        return

    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql = "DELETE from watchingSeries WHERE Name = ?"
    c.execute(sql,t)
    conn.commit()
    conn.close()

def listEntry(args):
    name="%"+" ".join(args)+"%"
    if searchEntry(name)==False:
        print(bcolors.FAIL + "ERROR: That entry doesn't exist" + bcolors.ENDC)
        return

    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql = "SELECT * from watchingSeries WHERE Name LIKE ?"
    for row in c.execute(sql,t):
        name=row[0]
        season=str(row[1])
        episode=str(row[2])
        print(bcolors.HEADER + "Name: "+name + bcolors.ENDC)
        print(bcolors.BLUE +"Season: "+season + bcolors.ENDC)
        print(bcolors.GREEN + "Episode: "+episode + bcolors.ENDC)
        print("")
    conn.close()

def listAllEntry():
    conn = sqlite3.connect(database)
    c = conn.cursor()
    sql = "SELECT * from watchingSeries ORDER BY Name"
    for row in c.execute(sql):
        name = row[0]
        season=str(row[1])
        episode=str(row[2])
        print(bcolors.HEADER + "Name: "+name + bcolors.ENDC)
        print(bcolors.BLUE + "Season: "+season + bcolors.ENDC)
        print(bcolors.GREEN + "Episode: "+episode + bcolors.ENDC)
        print("")
    conn.close()


def showHelp():
    print(bcolors.HEADER+ "TVShowsBox v0.1"+ bcolors.ENDC)
    print("A script written in python that manages all your TV Shows in a sqlite database.")
    print("")
    print("Options:")
    print("\tadd, -a \tNAME \tName of the show \tAdd a TV show" )
    print("\tedit, -e \tNAME SEASON EPISODE \tName of the show, Season number, Episode number \tEdit a TV Show")
    print("\tdelete, -d \tNAME \tName of the show \tDelete a TV Show")
    print("\tlist, -l \tNAME \tName of the show \tList a TV Show (it shows partial results)")
    print("\tlistAll, -l \tNAME \tName of the show \tList all the TV Shows")
    print("\twatch, -w \tNAME \tName of the show \tMark watch the next episode")
    print("\thelp, -h \tShow this information")


def main(argv):
    args = argv[1:]

    if len(args)==0:
        print("Error: It is required at least 1 argument. Use the --h or help to see which options are available")
        return

    arg = args[0]
    args = args[1:]

    if arg == "add" or arg=="-a":
        createEntry(args)
        return

    if arg == "edit" or arg=="-e":
        modifyEntry(args)
        return

    if arg == "delete" or arg=="-d":
        deleteEntry(args)
        return

    if arg == "list" or arg=="-l":
        listEntry(args)
        return

    if arg == "listAll" or arg=="-la":
        listAllEntry()
        return

    if arg == "watch" or arg=="-w":
        watchEntry(args)
        return

    if arg == "help" or arg=="-h":
        showHelp()
        return

    print("Invalid Option!")

if __name__ == "__main__":
    main(argv)
