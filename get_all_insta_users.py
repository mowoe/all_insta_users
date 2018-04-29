import requests
import random 
from urllib import quote
import time

nav_id = ""
count = 0
safety_delay = 1 #Delay between each request, to not get banned (in seconds)
accounts = [("username","password")]
accbac = accounts


def update_headers(csrf,sessid):
    global headers
    headers = {
            "Accept":"*/*",
            "Content-Type":"application/x-www-form-urlencoded",
            "Origin":"https://www.instagram.com",
            "Referer":"https://www.instagram.com/",
            "User-Agent":"Mozilla/5.0",
            "X-CSRFToken":csrf,
            "X-Instagram-AJAX":"1",
            "X-Requested-With":"XMLHttpRequest",
            "cookie": "csrftoken="+csrf+"; sessionid="+sessid
        }

def generate_csrf():
    try:
        resp = requests.get("http://instagram.com")
        return resp.cookies["csrftoken"]
    except Exception,e:
        print ""
        print e
        print "generating csrf failed:"
        generate_csrf()

def login((user,pw),csrf):
    try:
        url = "https://www.instagram.com/accounts/login/ajax/"
        payload = "username="+user+"&password="+quote(pw)
        headers = {
            'cookie': "csrftoken="+csrf+";",
            'referer': "https://www.instagram.com/",
            'x-csrftoken': csrf,
            'Content-Type': "application/x-www-form-urlencoded"
            }
        response = requests.request("POST", url, data=payload, headers=headers)
        return response.cookies["sessionid"]

    except Exception,e:
        print "login failed:"
        if response.json()["message"] == "rate limited":
                print "rate limit"
                print "changing ip and user..."
        elif response.json()["message"] == "checkpoint_required":
            print "account unusable, checkpoint"
            print response.json()
            return 0
        elif response.json()["message"] == "Please wait a few minutes before you try again.":
            print "account delayed"
            return 0
        elif "Your account has been disabled for violating our terms" in response.json()["message"]:
            print "account disabled"
            return 0
        else:
            print response.text
            print e
            login((user,pw),csrf)


def get_followers(suid,proxies={}):   
    global nav_id 
    global headers 
    next_page = True
    while next_page:
        try:
            url = "https://www.instagram.com/graphql/query/?query_hash=37479f2b8209594dde7facb0d904896a&variables={\"id\":\""+str(suid)+"\",\"first\":50, \"after\":\""+nav_id+"\"}"
            time.sleep(safety_delay)
            resp = requests.get(url,headers=headers)
            for user in  resp.json()["data"]["user"]["edge_followed_by"]["edges"]:
                nav_id = resp.json()["data"]["user"]["edge_followed_by"]["page_info"]["end_cursor"]
                yield {
                    "uname":user["node"]["username"],
                    "uid":user["node"]["id"],
                    "nav_id":nav_id,
                    "full_name":user["node"]["full_name"],
                    "profile_pic_url":user["node"]["profile_pic_url"]
                }
        except Exception,e:
            print resp.text
            print e
            if resp.json()["message"] == "rate limited":
                print "rate limit"
                print "changing ip and user..."
                download_all(suid)
            elif resp.json()["message"] == "checkpoint_required":
                print "account unusable, checkpoint"
                download_all(suid)


def download_all(uid,nav_id=""):
    global count
    global accounts
    global accbac
    if len(accounts) > 0:
        us = random.choice(accounts)
        accounts.pop(accounts.index(us))
    else:
        accounts = accbac
        time.sleep(50)
        download_all(uid,nav_id)
    print "logging in as:", us
    ccsrf = generate_csrf()
    print "new csrf:", ccsrf
    sessid = login(us,ccsrf)
    if sessid != 0:
        print "new sessid:", sessid
        update_headers(ccsrf,sessid)
        for user in get_followers(uid):
            count += 1
            print count
            yield user
    else:
        download_all(uid,nav_id)


for us in download_all("22612307"):
    print us




