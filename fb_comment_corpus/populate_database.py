from pymongo import MongoClient
import os
import sys
import json
import ctypes
import atexit
import helpers

client = MongoClient()
db = client.comment_corpus
bulk = db.comments.initialize_unordered_bulk_op()
print(db.command("serverStatus"))
count = 1
root_dir = os.getcwd()+os.sep+'comments'

# Checking if passed file is hidden....
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

def write_record(filepath, fun):
    global count, bulk
    try:
        # Write a record, tokenizing the message if indicated by user
        with open(filepath) as json_data:
            doc = json.load(json_data)
            if helpers.tokenize:
                doc['data']['message'] = helpers.tokenizer(doc['data']['message'])
            if fun == db.comments.update:
                count += 1
                bulk.insert(doc)
            else:
                fun(doc, doc, upsert=True)
    except Exception as e:
        print(e)
        print("error inserting document")
    # Comments are inserted in batches of 800
    if count % 800 == 0:
        bulk.execute()
        bulk = db.comments.initialize_unordered_bulk_op()

# Loops through all files/directories in passed dir, checking for JSON objects and nested directories
def parse_dir(dir, fun):
    for subdir in os.listdir(dir):
        dir_path = dir + os.sep + subdir
        if not is_hidden(subdir):
            if subdir.endswith(".json"):
                write_record(dir_path, fun)
            elif os.path.isdir(dir_path):
                parse_dir(dir_path, db.comments.update)

def populate_database():
    # Iterates over top-level directory of page ids
    for directory in os.listdir(root_dir):
        dir_path = root_dir + os.sep + directory
        # Checking that subdirectory hasn't already been added to database and that it is not hidden
        if not is_hidden(directory) and os.path.isdir(dir_path) and directory in helpers.visited:
            helpers.working_on(directory)
            parse_dir(dir_path, db.posts.update)
        helpers.visited[directory] = False
    # Final bulk insertion of any lingering documents before program termination
    bulk.execute()
    print('Database populated! Corpus creation complete.\n')
    sys.exit()

# Pickle progress
atexit.register(helpers.save_progress)
