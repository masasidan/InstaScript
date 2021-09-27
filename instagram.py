import time
from datetime import datetime
import json
import os
from bs4 import BeautifulSoup
import requests

os.system('cls')

link = 'https://www.instagram.com/accounts/login/'
login_url = 'https://www.instagram.com/accounts/login/ajax/'

currTime = int(datetime.now().timestamp())

username = input('Username: ')
password = input('Password: ')

payload = {
    'username': username,
    'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{currTime}:{password}',
    'queryParams': {},
    'optIntoOneTap': 'false'
}


def sendRequests(sessionid, csrf, userId):
    followersList = []

    followersNotFollowingBack = []

    payload = f'{{"id": "{userId}", "first": 1}}'

    print('Sending request..')
    r = requests.Session().get(f'https://www.instagram.com/graphql/query/?query_hash=3dec7e2c57367ef3da3d987d89f9dbc8&variables={payload}', headers={
        "x-csrftoken": csrf,
        "cookie": f"csrftoken={csrf}; sessionid={sessionid};"
    })

    followers = json.loads(r.text)['data']['user']['edge_follow']['count']

    payload = f'{{"id": "{userId}", "first": {followers}}}'

    r = requests.Session().get(f'https://www.instagram.com/graphql/query/?query_hash=3dec7e2c57367ef3da3d987d89f9dbc8&variables={payload}', headers={
        "x-csrftoken": csrf,
        "cookie": f"csrftoken={csrf}; sessionid={sessionid};"
    })

    hasNextPage = json.loads(
        r.text)['data']['user']['edge_follow']['page_info']['has_next_page']

    for user in json.loads(r.text)['data']['user']['edge_follow']['edges']:
        followersList.append(
            {"username": user['node']['username'], "id": user['node']['id']})

        if user['node']['follows_viewer'] == False:
            followersNotFollowingBack.append(
                {"username": user['node']['username'], "id": user['node']['id']})

    while hasNextPage == True:
        nextPageCode = json.loads(
            r.text)['data']['user']['edge_follow']['page_info']['end_cursor']

        payload = f'{{"id": "{userId}", "first": {followers}, "after": "{nextPageCode}"}}'

        r = requests.Session().get(f'https://www.instagram.com/graphql/query/?query_hash=3dec7e2c57367ef3da3d987d89f9dbc8&variables={payload}', headers={
            "x-csrftoken": csrf,
            "cookie": f"csrftoken={csrf}; sessionid={sessionid};"
        })

        for user in json.loads(r.text)['data']['user']['edge_follow']['edges']:
            followersList.append(
                {"username": user['node']['username'], "id": user['node']['id']})

            if user['node']['follows_viewer'] == False:
                followersNotFollowingBack.append(
                    {"username": user['node']['username'], "id": user['node']['id']})

        hasNextPage = json.loads(
            r.text)['data']['user']['edge_follow']['page_info']['has_next_page']
    else:
        print(
            f'Done! {len(followersNotFollowingBack)} users does not follow you back.\n')
        print(followersNotFollowingBack)

        yorn = input(
            '\nDo you want to un-follow everyone that does not follow you back? y/n - ')

        if yorn == "y":
            numOfReq = 0

            removedFollowers = 0

            for user in followersNotFollowingBack:
                userID = user['id']

                numOfReq += 1

                print(numOfReq)

                # Trying to bypass instagram's rate-limit
                if numOfReq == 6:
                    numOfReq = 0

                    time.sleep(15)

                    r = requests.Session().post(f'https://www.instagram.com/web/friendships/{userID}/unfollow/', headers={
                        "x-csrftoken": csrf,
                        "cookie": f"csrftoken={csrf}; sessionid={sessionid};"
                    })

                    if "ok" in r.text:
                        print("Un-following " + user['username'] + "...")
                        removedFollowers += 1
                    elif "wait" in r.text:
                        print(
                            "Rate limited: Instagram has blocked your account's actions. Please wait a few minutes and try again.")

                else:
                    r = requests.Session().post(f'https://www.instagram.com/web/friendships/{userID}/unfollow/', headers={
                        "x-csrftoken": csrf,
                        "cookie": f"csrftoken={csrf}; sessionid={sessionid};"
                    })

                    if "ok" in r.text:
                        removedFollowers += 1
                        print("Un-following " + user['username'] + "...")
                    elif "wait" in r.text:
                        print(
                            "Rate limited: Instagram has blocked your account's actions. Please wait a few minutes and try again.")

            print(
                f'\nDone! Successfully removed {removedFollowers} out of {len(followersNotFollowingBack)}. Exiting program...')
        else:
            print('Exiting program...')


with requests.Session() as s:
    r = s.post(login_url, data="", headers={
        "user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://www.instagram.com/accounts/login/",
    })
    csrf = r.cookies['csrftoken']
    r = s.post(login_url, data=payload, headers={
        "user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://www.instagram.com/accounts/login/",
        "x-csrftoken": csrf
    })
    print(r.status_code)
    print(r.url)
    print(r.text)

    sessionid = s.cookies['sessionid']

    userId = json.loads(r.text)['userId']

    print(sessionid + " - sessionid, " + csrf +
          " - x-csrftoken, " + userId + " - userId")

    sendRequests(sessionid, csrf, userId)
