from pymongo import MongoClient
from platform import system
import os, re, sys, csv, json, ctypes

client = MongoClient()
db = client.comment_corpus
bulk = db.comments.initialize_unordered_bulk_op()
print(db.command("serverStatus"))
count = 0

root_dir = os.getcwd()+os.sep+'Comments'

def is_hidden(filepath):
    name = os.path.basename(os.path.abspath(filepath))
    return name.startswith('.') or has_hidden_attribute(filepath)

def has_hidden_attribute(filepath):
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(unicode(filepath))
        assert attrs != -1
        result = bool(attrs & 2)
    except (AttributeError, AssertionError):
        result = False
    return result

def write_record(filepath,fun):
    global count, bulk
    count += 1
    try:
        # Write a record
        with open(filepath) as json_data:
            doc = json.load(json_data)
            if fun == db.comments.update:
                bulk.insert(doc)
            else:
                fun(doc, doc, upsert=True)
    except Exception as e:
        print("error inserting document")
    if count % 500 == 0:
        bulk.execute()
        bulk = db.comments.initialize_unordered_bulk_op()

def populate_database():
    for directory in os.listdir(root_dir):
        dir_path = root_dir + os.sep + directory
        if not is_hidden(directory) and os.path.isdir(dir_path):
            print('Working on ' + directory + '....')
            for subdir in os.listdir(dir_path):
                subdir_path = dir_path+os.sep+subdir
                if not is_hidden(subdir):
                    if subdir.endswith(".json"):
                        write_record(subdir_path,db.posts.update)
                    elif os.path.isdir(subdir_path):
                        for comment in os.listdir(subdir_path):
                            comm_path = subdir_path+os.sep+comment
                            if not is_hidden(comment) and comment.endswith(".json"):
                                write_record(comm_path,db.comments.update)
        else:
            continue

populate_database()