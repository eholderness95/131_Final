from pymongo import MongoClient
import os, json, ctypes, helpers, atexit

client = MongoClient()
db = client.comment_corpus
bulk = db.comments.initialize_unordered_bulk_op()
print(db.command("serverStatus"))
count = 1
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

def write_record(filepath, fun):
    global count, bulk
    try:
        # Write a record
        with open(filepath) as json_data:
            doc = json.load(json_data)
            if fun == db.comments.update:
                count += 1
                bulk.insert(doc)
            else:
                fun(doc, doc, upsert=True)
    except Exception as e:
        print("error inserting document")
    if count % 800 == 0:
        bulk.execute()
        bulk = db.comments.initialize_unordered_bulk_op()

def parse_dir(dir, fun):
    for subdir in os.listdir(dir):
        dir_path = dir + os.sep + subdir
        subdir_path = dir_path + os.sep + subdir
        if not is_hidden(subdir):
            if subdir.endswith(".json"):
                write_record(subdir_path, fun)
            elif os.path.isdir(subdir_path):
                parse_dir(subdir_path, db.comments.update)

def populate_database():
    for directory in os.listdir(root_dir):
        dir_path = root_dir + os.sep + directory
        if not is_hidden(directory) and os.path.isdir(dir_path) and directory not in helpers.visited:
            print('Working on ' + directory + '....')
            parse_dir(dir_path, db.posts.update)
        helpers.visited[directory] = True

atexit.register(helpers.save_progress)


populate_database()