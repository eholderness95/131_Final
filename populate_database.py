from pymongo import MongoClient
import os, re, sys, csv, json, ctypes

client = MongoClient()
db = client.comment_corpus
print(db.command("serverStatus"))

root_dir = os.getcwd()+os.sep+'comments'

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

def populate_database():
    for dir in os.listdir(root_dir):
        if not is_hidden(dir):
            dir_path = root_dir+os.sep+dir
            for subdir in os.listdir(dir_path):
                if subdir.endswith(".json") and not is_hidden(subdir):
                    print(subdir)
                    try:
                        # Write a record
                        with open(dir_path+os.sep+subdir) as json_data:
                            doc = json.load(json_data)
                            db.posts.update(doc, doc, upsert=True)
                            print('post added succesfully')
                    except Exception as e:
                        print("error inserting post")
                else:
                    comm_path = dir_path+os.sep+subdir
                    for comment in os.listdir(comm_path):
                        if not is_hidden(comment):
                            print(comment)
                            try:
                                # Write a record
                                with open(comm_path+os.sep+comment) as json_data:
                                    doc = json.load(json_data)
                                    db.comments.update(doc, doc, upsert=True)
                                    print('comment added succesfully')
                            except Exception as e:
                                print(e)
                                print("error inserting comment")

populate_database()