import datetime
import time

import requests
import json
import bs4


class URL:
    w = 'https://www.instagram.com'
    w_graphql = w + '/graphql'
    w_web = w + '/web'
    w_graphql_query = w_graphql + '/query'
    w_web_likes = w_web + '/likes'


class PostOffset:
    def __init__(self, profile_id: str, offset: int, end_cursor: str):
        self.profile_id = profile_id
        self.offset = offset
        self.end_cursor = end_cursor


class UserInfo:
    def __init__(self, full_name, id, biography, username, post_offset, query_hash_offset, query_hash_post):
        self.full_name = full_name
        self.id = id
        self.biography = biography
        self.username = username
        self.post_offset = post_offset
        self.query_hash_offset = query_hash_offset
        self.query_hash_post = query_hash_post


class PostInfo:
    def __init__(self, id: str, short_code: str):
        self.id = id
        self.short_code = short_code


class PostInfoMore(PostInfo):
    def __init__(self, id, short_code, liked):
        super(PostInfoMore, self).__init__(
            id=id,
            short_code=short_code
        )
        self.liked = liked


class HeartCommands:
    LIKE = 'like'
    UNLIKE = 'unlike'


class Key:
    POST_OFFSET = 'postOffset'
    POSTS_INFO = 'postInfo'


# loads cookies
cookies = {}
with open('cookies.txt', 'r') as file:
    line = file.read()
    file.close()
    for cookie in line.split('; '):
        key, value = cookie.split('=')
        cookies.update({key: value})

# setup session
session = requests.session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'close',
    'Upgrade-Insecure-Requests': '1',
    'X-CSRFToken': cookies['csrftoken'],
}
session.headers = headers


# extract 'window._sharedData' data
def extract_shared_data(soup):
    scripts = soup.find_all('script', attrs={'type': 'text/javascript'})
    data = None
    for script in scripts:
        try:
            script = script.contents[0]
            key = None
            value = None
            for i in range(len(script)):
                if key is None:
                    if script[i] in '= ':
                        key = script[:i]
                elif script[i] == '{':
                    value = script[i:-1]
                    break
            if key == 'window._sharedData':
                data = json.loads(value)
                break
        except:
            continue
    if data is None:
        raise ValueError
    return data


def get_user_info(p_username: str):
    r = session.get(f'{URL.w}/{p_username}', cookies=cookies)
    if r.status_code != 200:
        raise ValueError
    soup = bs4.BeautifulSoup(r.text, 'html.parser')

    scripts = soup.find_all('script', attrs={'crossorigin': 'anonymous', 'type': 'text/javascript'})
    for script in scripts:
        if '/static/bundles/es6/Consumer.js' in script['src']:
            r = requests.get(URL.w + script['src'], headers=headers).text

            pos = r.find(".RETRY_TEXT,actionHandler:()=>s(o(t))}})}}Object.defineProperty(e,'__esModule',{value:!0});const s=\"") + 100
            query_hash_post = r[pos:pos + 32]

            pos = r.find("null===(l=t.profilePosts.byUserId.get(n))||void 0===l?void 0:l.pagination},queryId:\"") + 84
            query_hash_offset = r[pos:pos + 32]
            break

    data = extract_shared_data(soup)
    user = data['entry_data']['ProfilePage'][0]['graphql']['user']
    page_info = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['page_info']
    if page_info['has_next_page']:
        post_offset = PostOffset(
            profile_id=user['id'],
            offset=0,
            end_cursor=page_info['end_cursor']
        )
    else:
        post_offset = None
    return UserInfo(
        full_name=user['full_name'],
        id=user['id'],
        biography=user['biography'],
        username=user['username'],
        post_offset=post_offset,
        query_hash_post=query_hash_post,
        query_hash_offset=query_hash_offset
    )


def get_user_posts(p_user_info: UserInfo, p_post_offset: PostOffset = None):
    if p_post_offset is None:
        # requestout with offset
        r = session.get(f'{URL.w}/{p_user_info.username}', cookies=cookies)
        if r.status_code != 200:
            print(r.text)
            raise ValueError
        # extract shared data
        data = extract_shared_data(bs4.BeautifulSoup(r.text, 'html.parser'))
        data = data['entry_data']['ProfilePage'][0]['graphql']
    else:
        # request with offset
        params = {
            'query_hash': p_user_info.query_hash_offset,
            'variables': json.dumps({
                'id': p_post_offset.profile_id,
                'first': p_post_offset.offset,
                'after': p_post_offset.end_cursor
            })
        }
        r = session.get(URL.w_graphql_query, cookies=cookies, params=params)
        if r.status_code != 200:
            raise ValueError
        data = json.loads(r.text)['data']

    edge_owner_to_timeline_media = data['user']['edge_owner_to_timeline_media']

    # extract posts
    posts_info = []
    posts_data = edge_owner_to_timeline_media['edges']
    for post_data in posts_data:
        post_data = post_data['node']
        posts_info.append(PostInfo(
            id=post_data['id'],
            short_code=post_data['shortcode']
        ))

    # create new offset
    page_info = edge_owner_to_timeline_media['page_info']
    if page_info['has_next_page']:
        if p_post_offset is None:
            offset = 12
        else:
            offset = p_post_offset.offset + 12
        post_offset = PostOffset(
            profile_id=p_user_info.id,
            offset=offset,
            end_cursor=page_info['end_cursor']
        )
    else:
        post_offset = None

    return {
        Key.POST_OFFSET: post_offset,
        Key.POSTS_INFO: posts_info
    }


def get_post_info_more(p_user_info: UserInfo, p_short_code: str):
    params = {
        'query_hash': p_user_info.query_hash_post,
        'variables': json.dumps({
            'shortcode': p_short_code,
            'as_threaded_comments': False
        })
    }
    r = session.get(URL.w_graphql_query, cookies=cookies, params=params)
    if r.status_code != 200:
        print(r.text)
        raise ValueError
    data = json.loads(r.text)
    if data['status'] != 'ok':
        raise ValueError
    data = data['data']['shortcode_media']
    return PostInfoMore(
        id=data['id'],
        short_code=data['shortcode'],
        liked=data['viewer_has_liked']
    )


def heart_post(p_post_id, p_command=HeartCommands.LIKE):
    r = session.post(f'{URL.w_web_likes}/{p_post_id}/{p_command}/', cookies=cookies)
    if r.status_code != 200:
        print(r.text)
        raise ValueError


def get_now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    delay = 60*60
    elon = get_user_info('elonofficiall')
    while True:
        print(f'{get_now()}: Like cycle started!')

        post_offset = None
        while True:
            r = get_user_posts(elon, p_post_offset=post_offset)
            post_offset = r[Key.POST_OFFSET]
            # like until last liked
            for post in r[Key.POSTS_INFO]:
                post_info_more = get_post_info_more(p_user_info=elon, p_short_code=post.short_code)
                if post_info_more.liked:
                    # stop cycle
                    post_offset = None
                    break
                else:
                    # like
                    print(f'Like post {post_info_more.id}')
                    heart_post(p_post_id=post_info_more.id, p_command=HeartCommands.LIKE)
            # stop if last/liked post reached
            if post_offset is None:
                break

        print(f'{get_now()}: Like cycle end! Sleep {delay/60}h')
        time.sleep(delay)
