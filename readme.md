# Facebook Corpus Constructor

This is a simple Python package that takes a .csv file of Facebook page URLs and generates a hierarchical directory of JSON objects corresponding to all posts and comments from January, 2016 onwards for each page provided. The package can then optionally populate a Mongo database that can be used for high-speed query by any field in the JSON objects. 

All posts and comments receive their own JSON object. Each object is structured into either two parts (for posts) or three parts (for comments): a ‘data’ field, which contains a timestamp, message content, and ID number; a ‘reactions’ field, which lists counts for each Facebook reaction (‘like’, ‘love’, ‘haha’, ‘angry’, ‘sad’, and ‘wow’); and for comments, a ‘replies’ field, which contains all replies to that comment. 

This package can be used for a number of purposes. Particular focus has been placed on its modularity and potential for application to NLP. By creating a file directory of JSON objects, the corpus can easily be duplicated across machines, split into smaller sub-corpora, and directly accessed using the system GUI without any coding knowledge. Additionally, JSON objects behave like a Python dictionary, making queries by parameter much easier. 

### Prerequisites

This package relies on the Requests library for making calls to Facebook’s Graph API. The optional database populator additionally relies on the PyMongo API and NLTK platform. It is only compatible with Python 3.0 and later. 

You will also need an app or user access token from Facebook in order for the script to make API calls. To get an access token, navigate to https://developers.facebook.com, login with your Facebook account, and select ‘Add a New App’ from the My Apps dropdown menu in the upper right corner of the page. Once you have a dummy app created, navigate to https://developers.facebook.com/tools/accesstoken/. Copy the ‘App Token’ value and paste it where indicated in create_directory.py. 

For the optional Mongo database population, the current version of the package requires that you have a MongoD instance running. If you do not have a mongod instance running, the database will not be operational and thus cannot have elements inserted. Populating the database is very fast, thanks to Mongo’s batch insertion feature. A test corpus of 1.3 million JSON objects was inserted into the database in about 15 minutes.  

## Deployment

When ready to execute, begin by cd-ing to the directory that you wish to have the corpus generated in. Execute the __init__.py script, passing the filepath of the .csv of page urls as a console parameter. The comment-aggregation process will take some time: most personal computers will be able to process 1-2 posts worth of comments per minute (200-500 JSON objects). This equates to ~30,000 comments per hour in the current version. In future version, we hope to integrate the Graph API batch request feature for more time efficient API calls. 

Please note that the package cannot currently parse anything but public Facebook pages. Groups (public and private) and user profiles cannot be parsed and trying to will result in the program crashing. 

## Known Bugs

— There is currently a fairly major Facebook-side bug that results in some data being omitted in API responses. The bug is unpredictable, but mostly impacts posts/comments farther back in time. See: https://developers.facebook.com/bugs/1838195226492053/. 

— If the database population script crashes during execution, some documents may not be inserted and some may be inserted multiple times. Currently working on figuring out how to batch update in Mongo with upsert=True. 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

