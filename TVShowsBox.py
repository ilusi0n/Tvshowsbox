#!/usr/bin/env python
from sys import argv
import sqlite3

database="tvshows.db"

def searchEntry(name):
    result=True
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute("SELECT rowid FROM watchingSeries WHERE Name = ?", (name,))
    data=c.fetchall()
    if len(data)==0:
        result=False
    conn.close()
    return result


def createEntry(args):
    name=" ".join(args)
    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql="INSERT INTO watchingSeries VALUES (?,'0','0')"
    c.execute(sql,t)
    conn.commit()
    conn.close()

def modifyEntry(args):
    name=" ".join(args)
    if searchEntry(name)==False:
        print("That entry doesn't exist")
        return

    season = input("Season: ")
    episode = input("Episode: ")
    t = (season,episode,name,)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    sql = "UPDATE watchingSeries SET Season = ?, Episode = ?  WHERE Name = ?"
    c.execute(sql,t)
    conn.commit()
    conn.close()

def deleteEntry(args):
    name=" ".join(args)
    if searchEntry(name)==False:
        print("That entry doesn't exist")
        return

    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql = "DELETE from watchingSeries WHERE Name = ?"
    c.execute(sql,t)
    conn.commit()
    conn.close()

def listEntry(args):
    name=" ".join(args)
    if searchEntry(name)==False:
        print("That entry doesn't exist")
        return

    conn = sqlite3.connect(database)
    c = conn.cursor()
    t = (name,)
    sql = "SELECT * from watchingSeries WHERE Name = ?"
    c.execute(sql,t)
    aList=c.fetchone()
    season=str(aList[1])
    episode=str(aList[2])
    print("Name: "+name)
    print("Season: "+season)
    print("Episode: "+episode)
    conn.close()

def listAllEntry():
    conn = sqlite3.connect(database)
    c = conn.cursor()
    sql = "SELECT * from watchingSeries"
    for row in c.execute(sql):
        name = row[0]
        season=str(row[1])
        episode=str(row[2])
        print("Name: "+name)
        print("Season: "+season)
        print("Episode: "+episode)
        print("")
    conn.close()


def showHelp():
    print("hue")


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

    print("Invalid Option!")

if __name__ == "__main__":
    main(argv)
