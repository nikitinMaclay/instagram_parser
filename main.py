import dropbox
import fgrequests
import threading
import asyncio
import aiofiles
import os
import secrets
import shutil
import string
import time
import zipfile
from datetime import datetime

import boto3
import requests
from botocore.config import Config

from database_manage.db_creation import create_database_local_connection
from dropbox_management.get_short_live_access_key import get_access_token
from parsing.instagram_classes import Post, PostMedia, Reel, Story


proxies = {
    "http": "http://aAnD9etY:5iYLwNwe@176.118.38.219:62240",
    "https": "http://aAnD9etY:5iYLwNwe@176.118.38.219:62240"
}


s3 = boto3.client(
    's3',
    endpoint_url='https://s3.timeweb.cloud',
    region_name='ru-1',
    aws_access_key_id='R1ZWBQWDJ44WUXQGUF5A',
    aws_secret_access_key='t5nHJ1K1aisTgOuDVLZlgSA5bwUhvip68CCBNx6w',
    config=Config(s3={'addressing_style': 'path'})
)

bucket_name = "49a2f75b-d806e76b-e741-49be-a128-315f48f934c4"


async def save_files(file_paths):
    tasks = []
    for file_path, content in file_paths.items():
        tasks.append(save_file(file_path, content))
    await asyncio.gather(*tasks)


async def save_file(file_path, content):
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
            print(f"File '{file_path}' saved successfully.")
    except:
        print("ERROR WHILE SAVING!!!")
        return


def upload_files_dropbox(account_name):
    access_token = get_access_token()["access_token"]
    dbx = dropbox.Dropbox(access_token)

    for folder_name in os.listdir(account_name):
        folder_path = f"{account_name}/{folder_name}"
        for file_name in os.listdir(folder_path):
            file_path = f"{account_name}/{folder_name}/{file_name}"
            try:
                if "preview" in file_name:
                    continue
                elif folder_name == "stories":
                    if file_name.endswith("img.jpg"):
                        file_name_to_check = file_name[:-8]
                        if (file_name_to_check + "_vid.mp4") in os.listdir(f"{account_name}/{folder_name}"):
                            continue
                with open(file_path, "rb") as f:
                    data_dbx = f.read()
                    dbx.files_upload(data_dbx, "/" + file_path)
                print(f"{file_path} - has been uploaded")
            except Exception as e:
                print(e)
                print(f"{file_path} - hasn't been uploaded")


def upload_to_s3_threaded(account_name):
    def upload_file(file_path):
        try:
            s3.upload_file(file_path, bucket_name, file_path)
            print(f"{file_path} - has been uploaded")
        except Exception as e:
            print(e)
            print(f"{file_path} - hasn't been uploaded")

    threads = []
    for folder_name in os.listdir(account_name):
        folder_path = f"{account_name}/{folder_name}"
        for file_name in os.listdir(folder_path):
            file_path = f"{account_name}/{folder_name}/{file_name}"
            thread = threading.Thread(target=upload_file, args=(file_path,))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return random_string


def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))


def media_downloading_sync(link, local_path):
    try:
        response = requests.get(link)

        if response.status_code == 200:
            with open(f"{local_path}", "wb") as file:
                file.write(response.content)
            print("Файл успешно скачан")
        else:
            print("Ошибка при скачивании файла:", response.status_code)
    except Exception as e:
        print(e)


def instagram_accounts_parsing(group_id, account_name, iterations):
    global undownloaded_files
    undownloaded_files = []

    try:
        s3.download_file(bucket_name, f"{account_name}/{account_name}.zip", f"{account_name}.zip")
        with zipfile.ZipFile(f"{account_name}.zip", 'r') as zip_ref:
            zip_ref.extractall(f"{account_name}/")
        os.remove(f"{account_name}.zip")
    except Exception as e:
        print(e)
    os.makedirs(f"{account_name}/", exist_ok=True)
    os.makedirs(f"{account_name}/posts", exist_ok=True)
    os.makedirs(f"{account_name}/reels", exist_ok=True)
    os.makedirs(f"{account_name}/stories", exist_ok=True)
    os.makedirs(f"{account_name}/profile_pic", exist_ok=True)
    print(f"Creating local folders for {account_name}...")
    url = "https://instagram-scraper-2022.p.rapidapi.com/ig/posts_username/"
    querystring = {"user": f"{account_name}"}
    headers = {
        "X-RapidAPI-Key": "1c462312edmsh1ec8f2d3119f648p1beb45jsna5c4bf12a219",
        "X-RapidAPI-Host": "instagram-scraper-2022.p.rapidapi.com",
    }

    posts_list = []

    reels_list = []

    posts_media_list = []

    db_con, cursor = create_database_local_connection()

    cursor.execute(f"SELECT account_id FROM `accounts` WHERE account_name = '{account_name}'")
    account_id = cursor.fetchone()
    if account_id is None:
        account_id = account_name + "_" + generate_random_string(32)
    else:
        account_id = account_id[0]

    for _ in range(iterations):
        n = 0
        while n < 20:
            try:
                response = requests.get(url, headers=headers, params=querystring)
                answer = response.json()
                end_cursor = (
                    answer)['data']['xdt_api__v1__feed__user_timeline_graphql_connection']['page_info']['end_cursor']
                break
            except Exception as e:
                print(e)
                print("ERROR", n)
                time.sleep(10)
                n += 1

        edges = answer['data']['xdt_api__v1__feed__user_timeline_graphql_connection']['edges']

        for edge in edges:
            edge_node = edge['node']
            if edge_node['video_versions']:
                continue
            post = Post()
            post.post_id = edge_node['id']
            cursor.execute(f"SELECT post_id FROM `posts` WHERE post_id = '{post.post_id}'")
            post_in_db = cursor.fetchone()
            if post_in_db:
                continue
            post.account_id = account_id
            try:
                post.post_text = edge_node['caption']['text']
                post.post_text = post.post_text.replace("'", "").replace('"', "")
            except:
                post.post_text = "No caption"
            date_taken = edge_node['taken_at']
            date_of_release = datetime.fromtimestamp(date_taken)
            post.date_of_release = date_of_release
            post.link_to_download_preview = edge_node['image_versions2']['candidates'][0]['url']
            post.post_preview = f"{account_name}/posts/{edge_node['id']}_preview.jpg"
            if not edge_node["carousel_media"]:
                post.is_carousel = 0
                post_media = PostMedia()
                post_media.post_id = post.post_id
                post_media.post_image = f"{account_name}/posts/{post.date_of_release}_{edge_node['id']}_img.jpg"
                post_media.link_to_download = edge_node['image_versions2']['candidates'][0]['url']
                post_media.media_type = "image"

                posts_list.append(post)
                posts_media_list.append(post_media)
            else:
                post.is_carousel = 1
                for el in edge_node['carousel_media']:
                    el_node = el
                    post_media = PostMedia()
                    post_media.post_id = post.post_id
                    if el_node['video_versions']:
                        post_media.post_image = f"{account_name}/posts/{post.date_of_release}_{el_node['id']}_vid.mp4"
                        post_media.link_to_download = el_node['video_versions'][0]['url']
                        post_media.media_type = "video"
                    else:
                        post_media.post_image = f"{account_name}/posts/{post.date_of_release}_{el_node['id']}_img.jpg"
                        post_media.link_to_download = el_node['image_versions2']['candidates'][0]['url']
                        post_media.media_type = "image"

                    posts_media_list.append(post_media)
                posts_list.append(post)

        if end_cursor == "":
            break

        querystring["end_cursor"] = end_cursor

    # reels
    url = "https://instagram-scraper-2022.p.rapidapi.com/ig/reels_posts_username/"
    querystring = {"user": {account_name}}
    headers = {
        "X-RapidAPI-Key": "1c462312edmsh1ec8f2d3119f648p1beb45jsna5c4bf12a219",
        "X-RapidAPI-Host": "instagram-scraper-2022.p.rapidapi.com"
    }

    for _ in range(iterations):

        n = 0
        while n < 20:
            try:
                response = requests.get(url, headers=headers, params=querystring)
                print('REEELS')
                # print(response.text)
                # time.sleep(1000)
                answer = response.json()
                end_cursor = answer['paging_info']

                if 'max_id' in end_cursor.keys():
                    max_id = answer['paging_info']['max_id']

                else:
                    max_id = "stop"
                break
            except:
                time.sleep(10)
                n += 1

        for item in answer['items']:
            reel = Reel()
            item_media = item['media']
            reel.reel_id = item_media['id']
            cursor.execute(f"SELECT reel_id FROM `reels` WHERE reel_id = '{reel.reel_id}'")
            reel_in_db = cursor.fetchone()
            if reel_in_db:
                continue
            reel.account_id = account_id

            try:
                reel.reel_text = item_media['caption']['text'].replace("'", "").replace('"', "")
            except:
                reel.reel_text = "No caption"
            date_of_release = datetime.fromtimestamp(item_media['taken_at'])
            reel.date_of_release = date_of_release
            reel.reel_video = f"{account_name}/reels/{reel.date_of_release}_{reel.reel_id}_vid.mp4"
            reel.link_to_download_vid = item_media['video_versions'][0]['url']
            reel.reel_preview = f"{account_name}/reels/{reel.reel_id}_preview.jpg"
            try:
                reel.link_to_download_prev = item_media['image_versions2']['candidates'][0]['url']
            except:
                reel.link_to_download_prev = "https://stock.adobe.com/kz/search/images?k=no+image+available&" \
                                             "asset_id=470299797"
            reels_list.append(reel)

        if max_id == "stop" or max_id == "":
            break
        querystring["max_id"] = max_id
    # Сбор рилсов и сторис

    url = "https://instagram-scraper-2022.p.rapidapi.com/ig/user_id/"
    querystring = {"user": f"{account_name}"}
    headers = {
        "X-RapidAPI-Key": "1c462312edmsh1ec8f2d3119f648p1beb45jsna5c4bf12a219",
        "X-RapidAPI-Host": "instagram-scraper-2022.p.rapidapi.com"
    }
    n = 0
    while n < 30:
        try:
            response_id = requests.get(url, headers=headers, params=querystring)
            account_inst_id = response_id.json()['id']
            break
        except:
            n += 1
            time.sleep(10)
    url = "https://instagram-scraper-2022.p.rapidapi.com/ig/stories/"
    querystring = {"id_user": account_inst_id}
    headers = {
        "X-RapidAPI-Key": "1c462312edmsh1ec8f2d3119f648p1beb45jsna5c4bf12a219",
        "X-RapidAPI-Host": "instagram-scraper-2022.p.rapidapi.com"
    }

    stories_download_links = []
    stories_list = []
    n = 0
    while n < 20:
        print("STORIES")
        response = requests.get(url, headers=headers, params=querystring)
        answer = response.json()
        if "reels_media" in answer.keys():
            break
        else:
            n += 1
            time.sleep(10)

    if 'reels_media' in answer.keys() and answer['reels_media']:
        story_items = answer['reels_media'][0]['items']
        for story_item in story_items:
            story = Story()
            story.story_id = story_item['id']
            cursor.execute(f"SELECT story_id FROM `stories` WHERE story_id = '{story.story_id}'")
            story_in_db = cursor.fetchone()
            if story_in_db:
                continue
            date_of_release_story = story_item['taken_at']
            date_of_release_story = datetime.fromtimestamp(date_of_release_story)
            story.date_of_release = date_of_release_story

            if "story_link_stickers" in story_item.keys():
                story.on_story_link = story_item['story_link_stickers'][0]['story_link']['url']
            else:
                story.on_story_link = "No links"

            if 'video_versions' in story_item.keys():
                story.story_image = f"{account_name}/stories/{story.date_of_release}_{story.story_id}_vid.mp4"
                stories_download_links.append([story_item['video_versions'][0]['url'], story.story_image])

                stories_download_links.append([story_item['image_versions2']['candidates'][0]['url'],
                                               f"{account_name}/stories/{story.story_id}_img.jpg"])
                story.media_type = "video"

            else:
                story.story_image = f"{account_name}/stories/{story.date_of_release}_{story.story_id}_img.jpg"
                stories_download_links.append([story_item['image_versions2']['candidates'][0]['url'],
                                               f"{account_name}/stories/{story.story_id}_img.jpg"])
                story.media_type = "img"

            stories_list.append(story)

    url = "https://instagram-scraper-2022.p.rapidapi.com/ig/info_username/"
    querystring = {"user": f"{account_name}"}

    headers = {
        "X-RapidAPI-Key": "1c462312edmsh1ec8f2d3119f648p1beb45jsna5c4bf12a219",
        "X-RapidAPI-Host": "instagram-scraper-2022.p.rapidapi.com"
    }

    n = 0
    while n < 20:
        try:
            response = requests.get(url, headers=headers, params=querystring)
            answer = response.json()
            profile_pic_url = answer['user']['profile_pic_url']
            media_downloading_sync(profile_pic_url, f"{account_name}/profile_pic/{account_name}.jpg")
            break
        except:
            time.sleep(10)
            n += 1

    cursor.execute(f"SELECT account_name FROM `accounts` WHERE account_name = '{account_name}'")
    account_in_db = cursor.fetchone()
    if not account_in_db:
        cursor.execute(f"Insert Into `accounts`(account_id, group_id, account_name, last_update_date) "
                       f"Values('{account_id}', '{group_id}', '{account_name}', '{datetime.now().date()}')")
        db_con.commit()

    for post in posts_list:
        try:
            cursor.execute(f"Insert Into `posts`(post_id, account_id, post_text,"
                           f" post_preview, date_of_release, last_update_date, is_carousel) "
                           f"Values('{post.post_id}', '{account_id}', '{post.post_text}', '{post.post_preview}',"
                           f"'{post.date_of_release}', '{datetime.now().date()}', '{post.is_carousel}')")
        except:
            continue

    for post_media in posts_media_list:
        try:
            cursor.execute(f"INSERT INTO `posts_media`(post_id, post_image, media_type) "
                           f"VALUES('{post_media.post_id}',"
                           f" '{post_media.post_image}',"
                           f" '{post_media.media_type}')")
        except:
            continue

    for cur_reel in reels_list:
        try:
            cursor.execute(f"INSERT INTO `reels`(reel_id, account_id, "
                           f"reel_text, date_of_release, last_update_date, reel_image)"
                           f" VALUES('{cur_reel.reel_id}', '{account_id}', '{cur_reel.reel_text}',"
                           f" '{cur_reel.date_of_release}', '{datetime.now().date()}',"
                           f" '{cur_reel.reel_video}')")
        except:
            continue

    for story_ in stories_list:
        try:
            cursor.execute(f"INSERT INTO `stories`(story_id, account_id, "
                           f"date_of_release, story_image, media_type, on_story_link)"
                           f" VALUES('{story_.story_id}', '{account_id}', '{story_.date_of_release}',"
                           f" '{story_.story_image}', '{story_.media_type}', '{story_.on_story_link}')")
        except:
            continue

    for reel in reels_list:
        post_media_1, post_media_2 = PostMedia(), PostMedia()
        post_media_1.post_image = reel.reel_video
        post_media_1.link_to_download = reel.link_to_download_vid
        post_media_2.post_image = reel.reel_preview
        post_media_2.link_to_download = reel.link_to_download_prev
        posts_media_list.append(post_media_1)
        posts_media_list.append(post_media_2)

    for post_ in posts_list:
        post_media = PostMedia()
        post_media.post_image = post_.post_preview
        post_media.link_to_download = post_.link_to_download_preview
        posts_media_list.append(post_media)

    resp = fgrequests.build([el.link_to_download for el in posts_media_list], proxies=proxies)
    print("Responses are gotten")
    print(f"length is {len(resp)}")
    res_post_media_to_download = {}
    # print(list(resp))
    for idx, post_media in enumerate(posts_media_list):
        if resp[idx]:
            res_post_media_to_download[post_media.post_image] = resp[idx].content
        else:
            undownloaded_files.append([post_media.link_to_download, post_media.post_image])
    # print(undownloaded_files)
    print(f"keys here: " + str(len(res_post_media_to_download.keys())))
    asyncio.run(save_files(res_post_media_to_download))
    print("FINISH!")

    # for post_media in posts_media_list:
    #     media_downloading_sync(post_media.link_to_download, post_media.post_image)

    # for reel in reels_list:
    #     media_downloading_sync(reel.link_to_download_vid, reel.reel_video)
    #     media_downloading_sync(reel.link_to_download_prev, reel.reel_preview)

    for el in stories_download_links:
        media_downloading_sync(el[0], el[1])

    for el in undownloaded_files:
        media_downloading_sync(el[0], el[1])
    print("THE END!")

    print("Загрузка файлов на s3")

    try:
        upload_to_s3_threaded(account_name)
    except:
        pass

    try:
        upload_files_dropbox(account_name)
    except:
        pass

    zip_folder(f"{account_name}/", f"{account_name}.zip")

    s3.upload_file(f"{account_name}.zip", bucket_name, f"{account_name}/{account_name}.zip")

    os.remove(f"{account_name}.zip")

    shutil.rmtree(f"{account_name}/")
    db_con.commit()

    cursor.execute(f"SELECT * FROM `posts` WHERE account_id = '{account_id}'")
    posts_count = len(cursor.fetchall())

    cursor.execute(f"SELECT * FROM `stories` WHERE account_id = '{account_id}'")
    stories_count = len(cursor.fetchall())

    cursor.execute(f"SELECT * FROM `reels` WHERE account_id = '{account_id}'")
    reels_count = len(cursor.fetchall())
    cursor.execute(f"UPDATE `accounts` SET account_image = '{account_name}/profile_pic/{account_name}.jpg', "
                   f"posts_count = '{posts_count}', stories_count = '{stories_count}', reels_count = '{reels_count}' "
                   f"WHERE account_id = '{account_id}'")

    db_con.commit()

    cursor.close()
    db_con.close()

    print(f"PARSING OF {account_name} IS DONE!")


# instagram_accounts_parsing(1, "lulu_kazakhstan", 1)
