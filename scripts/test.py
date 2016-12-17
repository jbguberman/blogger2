import requests
import json
from configparser import SafeConfigParser
from time import sleep
import sys
import get_posts


def getComments(settings, keys, blogID, postID, timestamp, jumper):

    key = keys[jumper]

    if timestamp:
        payload = {'maxResults': settings['MAX_POSTS'],
                   'key': key,
                   'endDate': timestamp}
    else:
        payload = {'maxResults': settings['MAX_POSTS'],
                   'key': key}

    comments = requests.get('https://www.googleapis.com/blogger/v3/blogs/{}/posts/{}/comments?'
                            .format(blogID, postID), params=payload)

    return(comments)


def getBlogID(settings, keys, jumper):

    key = keys[jumper]

    r = requests.get('https://www.googleapis.com/blogger/'
                     'v3/blogs/byurl?url={}%2F&key={}'
                     .format(settings['BLOG_URL'], key))

    blog_Data = r.json()
    blogID = blog_Data['id']
    postsInBlog = blog_Data['posts']['totalItems']

    return(blogID, postsInBlog)


if __name__ == '__main__':

    keys = ['AIzaSyA46oExWtnWuzXamBhyW9yJlMtCXz0fV5Q',
            'AIzaSyDSqlS61HeyhTm93k_ypjSPgHjHnIoybzo',
            'AIzaSyBeV_UsBAmZkCXsP5GpWNqqmP9X9Zfx1SA']

    jumper = 0

    config = SafeConfigParser()
    config.read('../settings.cfg')

    settings = get_posts.setup(config)

    blogID, postsInBlog = getBlogID(settings, keys, jumper)

    totalCalls = 0

    with open('../data/posts.json') as blog_posts:
        blogData = json.load(blog_posts)

        for post in blogData:

            postID = post['id']

            for key, value in post['replies'].items():
                if key == 'totalItems':
                    totalComments = int(value)

            grabbedComments = 0

            print("post {} has {} comments".format(postID, totalComments))

            if totalComments > 0:

                if totalCalls > 4000:
                    print('sleeping to avoid hitting the ratelimit')
                    sleep(60 * 4)
                    totalCalls = 0
                    if jumper == 3:
                        jumper = 0
                    else:
                        jumper += 1

                comments = []

                while grabbedComments < totalComments:

                    try:
                        if grabbedComments == 0:
                            totalCalls += 1
                            newComments = getComments(settings, keys,
                                                      blogID, postID, '', jumper)
                            newComments.raise_for_status()

                        else:
                            totalCalls += 1
                            lastPost = comments[-1]
                            timestamp = lastPost['published']

                            newComments = getComments(settings, keys,
                                                      blogID, postID, timestamp, jumper)
                            newComments.raise_for_status()

                    except requests.exceptions.HTTPError as e:
                        if newComments.status_code == 400:
                            print(e)
                            sys.exit(1)
                        elif newComments.status_code == 403:
                            sleep(60 * 3)
                            continue

                    try:
                        data = newComments.json()
                        tmpComments = data['items']

                        if grabbedComments == 0:
                            comments = tmpComments
                            grabbedComments += len(tmpComments)
                        else:
                            for comment in tmpComments:
                                comments.append(comment)
                            grabbedComments += len(tmpComments)
                    except KeyError as e:
                        print(e)
                        sleep(45)
                        continue

                print("{} comments grabbed".format(grabbedComments))

                post['replies'].update({'comments': comments})

            else:
                post['replies'].update({'comments': 'null'})

        with open('../data/completeData.json', 'w'):
            json.dump(blogData)
