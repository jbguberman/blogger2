import requests
import json
from configparser import SafeConfigParser
from datetime import datetime, timezone
from time import sleep
import sys


def setup(config):

    settings = {}
    settings['API_KEY'] = config.get('keys', 'api_key')
    settings['BLOG_URL'] = config.get('settings', 'blog_url')
    settings['MAX_POSTS'] = config.get('settings', 'max_posts')
    settings['MAX_COMMENTS'] = config.get('settings', 'max_comments')

    return(settings)


def getBlogID(settings):

    r = requests.get('https://www.googleapis.com/blogger/'
                     'v3/blogs/byurl?url={}%2F&key={}'
                     .format(settings['BLOG_URL'], settings['API_KEY']))

    blog_Data = r.json()
    blogID = blog_Data['id']
    postsInBlog = blog_Data['posts']['totalItems']

    return(blogID, postsInBlog)


def getPosts(settings, blogID, timestamp):

    payload = {'maxResults': settings["MAX_POSTS"],
               'key': settings['API_KEY'], 'endDate': timestamp}

    posts = requests.get(
        'https://www.googleapis.com/blogger/v3/blogs/{}/posts?'
        .format(blogID), params=payload)

    return(posts)


if __name__ == '__main__':

    config = SafeConfigParser()
    config.read('../settings.cfg')

    settings = setup(config)

    local_time = datetime.now(timezone.utc).astimezone()
    local_time.isoformat()
    localTime = str(local_time)
    localTime = localTime.replace(' ', 'T')

    blogID, postsInBlog = getBlogID(settings)

    postsGrabbed = 0
    firstCall = True

    posts = []

    while postsGrabbed < postsInBlog:

        if firstCall:
            try:
                firstPosts = getPosts(settings, blogID, localTime)
                firstPosts.raise_for_status()

            except requests.exceptions.HTTPError as e:
                if firstPosts.status_code == 400:
                    print(e)
                    sys.exit(1)
                elif firstPosts.status_code == 403:
                    print("Ratelimit exceeded, sleeping for one day")
                    sleep(60 * 60 * 24)
                    firstPosts = getPosts(settings, blogID, 44)

            data = firstPosts.json()
            posts = data['items']
            postsGrabbed += len(posts)
            firstCall = False

        else:

            lastPost = posts[-1]
            timestamp = lastPost['published']
            print(timestamp)

            try:
                newPosts = getPosts(settings, blogID, timestamp)
                newPosts.raise_for_status()

            except requests.exceptions.HTTPError as e:
                if newPosts.status_code == 400:
                    print(e)
                    sys.exit(1)
                elif firstPosts.status_code == 403:
                    print("Ratelimit exceeded, sleeping for one day")
                    sleep(60 * 60 * 24)
                    newPosts = getPosts(settings, blogID, timestamp)

            data = newPosts.json()
            postList = data['items']
            for post in postList:
                posts.append(post)

            postsGrabbed += len(postList)
            print(postsGrabbed)

    with open('../data/posts.json', 'w') as outfile:
        json.dump(posts, outfile)
