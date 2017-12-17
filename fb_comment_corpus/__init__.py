import grab_posts
import sys

try:
    pages = sys.argv[1]
except IndexError:
    print('Make sure to include the name of the page-containing .csv file in the command line when executing')
    sys.exit()
print('Facebook Comment Corpus initialized.\n\n')

grab_posts.parse_pages(pages)

