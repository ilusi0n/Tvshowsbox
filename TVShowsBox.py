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
    #print(result)
    return result


def createEntry(args):
    name=" ".join(args)
    conn = sqlite3.connect(database)
    c = conn.cursor()
    sql="INSERT INTO watchingSeries VALUES ("+ "'" + name + "'," + "'0','0')"
    c.execute(sql)
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


if __name__ == "__main__":
    args = argv[1:]

    while len(args) > 0:
        arg = args[0]
        args = args[1:]

        if arg == "add" or arg=="-a":
            createEntry(args)
            break

        if arg == "search" or arg=="-s":
            searchEntry(args[0])
            break

        if arg == "edit" or arg=="-e":
            modifyEntry(args)
            break

        if arg == "delete" or arg=="-d":
            deleteEntry(args)
            break

        if arg == "list" or arg=="-l":
            listEntry(args)
            break

        if arg == "listall" or arg=="-la":
            listAllEntry()
            break

        showHelp()
        break
