import requests
import json
from configparser import SafeConfigParser
from time import sleep
import sys
import get_posts


def getComments(settings, blogID, postID, timestamp):

    if timestamp:
        payload = {'maxResults': settings['MAX_POSTS'],
                   'key': settings['API_KEY'],
                   'endDate': timestamp}
    else:
        payload = {'maxResults': settings['MAX_POSTS'],
                   'key': settings['API_KEY']}

    comments = requests.get('https://www.googleapis.com/blogger/v3/blogs/{}/posts/{}/comments?'
                            .format(blogID, postID), params=payload)

    return(comments)


if __name__ == '__main__':

    config = SafeConfigParser()
    config.read('../settings.cfg')

    settings = get_posts.setup(config)

    blogID, postsInBlog = get_posts.getBlogID(settings)

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

                comments = []

                while grabbedComments < totalComments:

                    try:
                        if grabbedComments == 0:
                            newComments = getComments(settings,
                                                      blogID, postID, '')
                            newComments.raise_for_status()

                        else:
                            lastPost = comments[-1]
                            timestamp = lastPost['published']

                            newComments = getComments(settings,
                                                      blogID, postID, '')
                            newComments.raise_for_status()

                    except requests.exceptions.HTTPError as e:
                        if newComments.status_code == 400:
                            print(e)
                            sys.exit(1)
                        elif newComments.status_code == 403:

                            try:
                                print('Ratelimit exceeded, sleeping for 30 seconds')
                                sleep(30)
                                if grabbedComments == 0:
                                    newComments = getComments(settings,
                                                              blogID, postID, '')

                                else:
                                    lastPost = comments[-1]
                                    timestamp = lastPost['published']

                                    newComments = getComments(settings,
                                                              blogID, postID, '')
                                    newComments.raise_for_status()

                            except newComments.status_code as e:

                                if newComments.status_code == 403:

                                    print("Ratelimit exceeded, sleeping for one day")
                                    sleep(60 * 60 * 24)

                                    if grabbedComments == 0:
                                        newComments = getComments(settings,
                                                                  blogID, postID, '')

                                    else:
                                        lastPost = comments[-1]
                                        timestamp = lastPost['published']

                                        newComments = getComments(settings,
                                                                  blogID, postID, '')

                    data = newComments.json()
                    tmpComments = data['items']

                    if grabbedComments == 0:
                        comments = tmpComments
                        grabbedComments += len(tmpComments)
                    else:
                        for comment in tmpComments:
                            comments.append(comment)
                        grabbedComments += len(tmpComments)

                print("{} comments grabbed".format(grabbedComments))

                post['replies'].update({'comments': comments})

        with open('../data/completeData.json', 'w'):
            json.dump(blogData)
