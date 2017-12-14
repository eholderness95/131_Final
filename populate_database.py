from pymongo import MongoClient
import os, re, sys, csv, json, ctypes

client = MongoClient()
db = client.comment_corpus
print(db.command("serverStatus"))

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
    try:
        # Write a record
        with open(filepath) as json_data:
            doc = json.load(json_data)
            fun(doc, doc, upsert=True)
    except Exception as e:
        print("error inserting document")

def populate_database():
    for dir in os.listdir(root_dir):
        if not is_hidden(dir):
            print('Working on ' + dir + '....')
            dir_path = root_dir+os.sep+dir
            for subdir in os.listdir(dir_path):
                subdir_path = dir_path+os.sep+subdir
                if not is_hidden(subdir):
                    if subdir.endswith(".json"):
                        write_record(subdir_path,db.posts.update)
                    elif os.path.isdir(subdir_path):
                        for comment in os.listdir(subdir_path):
                            comm_path = subdir_path+os.sep+comment
                            if not is_hidden(comment):
                    else:
                        continue

populate_database()