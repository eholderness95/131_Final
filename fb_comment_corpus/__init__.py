import sys
import helpers
import create_directory


try:
    pages = sys.argv[1]
except IndexError:
    print('Make sure to include the name of the page-containing .csv file in the command line when executing')
    sys.exit()
print('Facebook Comment Corpus initialized.\n\n')
helpers.visited = {}
create_directory.parse_pages(pages)
