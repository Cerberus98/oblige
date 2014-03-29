#!/usr/bin/python

import re
import os
import sys
import MySQLdb

def get_file(file_path):
    return [line.strip() for line in open(file_path, 'r')]

# print get_file('oblige_debug.log')

conn = MySQLdb.connect(host='',
                user='',
                passwd='',
                db='')

cursor = conn.cursor()

cursor.execute('query')
conn.commit()
cursor.close()
conn.close()
