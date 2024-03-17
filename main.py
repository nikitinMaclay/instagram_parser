import collections
import json
import os
import random
import shutil
import time
import zipfile
from datetime import datetime

import boto3
import requests
from botocore.config import Config
from instaloader import Instaloader
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

import bs4

from parsing.instagram_classes import Post, PostMedia, Reel
from database_manage.db_creation import create_database_local_connection

accounts_for_parsing = {"saberalius": "avQOxD!maOIbICES",
                        "alsodi_mohammed": "Q1OewaSmWCjvuq6K",
                        "silvanaecezar": "3vPPN%uzX9roYQNK",
                        "edsonnhantumbo": "HegVnKf@3RoZFpto",
                        "syed_asad_ali_": "RfV@oBslRCHd$mvR",
                        "medissamadnane": "dkpAFZ%Sv!ClRw1p",
                        "ekwanpethek": "JfZo$YgSsjsW@ukx",
                        "pehashan": "mahWmh$Y8OvHJ8V@"}

s3 = boto3.client(
    's3',
    endpoint_url='https://s3.timeweb.cloud',
    region_name='ru-1',
    aws_access_key_id='R1ZWBQWDJ44WUXQGUF5A',
    aws_secret_access_key='t5nHJ1K1aisTgOuDVLZlgSA5bwUhvip68CCBNx6w',
    config=Config(s3={'addressing_style': 'path'})
)

bucket_name = "49a2f75b-d806e76b-e741-49be-a128-315f48f934c4"


def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))


def media_downloading(link, local_path):
    response = requests.get(link)

    if response.status_code == 200:
        with open(f"{local_path}", "wb") as file:
            file.write(response.content)
        print("Файл успешно скачан")
    else:
        print("Ошибка при скачивании файла:", response.status_code)


def instagram_accounts_parsing(account_name, group_id, posts_scroll_count, reel_scroll_count):
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
    db_con, cursor = create_database_local_connection()
    cursor.execute(f"SELECT account_name FROM `accounts` WHERE account_name = '{account_name}'")
    account_in_db = cursor.fetchone()
    if not account_in_db:
        cursor.execute(f"Insert Into `accounts`(group_id, account_name, last_update_date) "
                       f"Values('{group_id}', '{account_name}', '{datetime.now().date()}')")
        db_con.commit()

    cursor.fetchone()

    cursor.execute(f"SELECT account_id FROM `accounts` WHERE account_name = '{account_name}'")
    account_id = cursor.fetchone()[0]

    options = Options()
    # options.add_argument("--headless")
    # profile_directory = r'%AppData%\Mozilla\Firefox\Profiles\7dqce575.inst'
    # profile = webdriver.FirefoxProfile(os.path.expandvars(profile_directory))
    # options.profile = profile

    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    driver.implicitly_wait(5)

    driver.get(f"https://www.instagram.com/")
    print("Opening the driver...")
    time.sleep(5)

    username_input = driver.find_element(by=By.NAME, value="username")
    password_input = driver.find_element(by=By.NAME, value="password")
    username = random.choice(list(accounts_for_parsing.keys()))
    password = accounts_for_parsing[username]
    # username = "ekwanpethek"
    # password = accounts_for_parsing[username]

    print("start login...")
    username_input.send_keys(username)
    password_input.send_keys(password)
    print(f"{username} - acc for parsing")
    time.sleep(1)

    login_btn = driver.find_element(by=By.XPATH,
                                    value="/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[3]/button")
    time.sleep(1)
    login_btn.click()
    time.sleep(15)

    try:
        driver.find_element(by=By.XPATH,
                            value="/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[3]/button")
        time.sleep(15)
    except:
        pass

    print("login successfully!")

    driver.get(f"https://www.instagram.com/{account_name}")
    time.sleep(5)

    # initial_height = driver.execute_script("return document.body.scrollHeight")

    soups = []

    # сбор постов (скроллинг)
    n = 0
    print("Start posts scrolling")
    while n < posts_scroll_count:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        html = driver.page_source
        soups.append(bs4.BeautifulSoup(html, "lxml"))

        # current_height = driver.execute_script("return document.body.scrollHeight")
        n += 1
    print("Posts scrolling is done!")

    print("Start reels scrolling")

    driver.get(f"https://www.instagram.com/{account_name}/reels/")
    time.sleep(5)
    n = 0
    while n < reel_scroll_count:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        html = driver.page_source
        soups.append(bs4.BeautifulSoup(html, "lxml"))

        # current_height = driver.execute_script("return document.body.scrollHeight")
        n += 1

    print("Reels scrolling is done!")
    # сбор ссылок на посты
    post_urls = []
    for soup in soups:
        elements = soup.find_all("a",
                                 class_="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd")
        post_urls.extend([element["href"] for element in elements if element["href"].startswith(("/p", "/reel"))
                          and not element["href"].endswith(("p/", "reels/"))])
    # _ac_u
    res_post_urls = []

    for url in post_urls:
        if url not in res_post_urls and url != "":
            res_post_urls.append(url)

    query_parameters = "__a=1&__d=dis"
    json_list = []
    print("Start posts and reels data collecting...")
    print(f"Need to scrape {len(res_post_urls)} pages")
    for idx, url in enumerate(res_post_urls):
        if idx > 0 and idx % 10 == 0:
            print(f"     Parsing account has been changed")
            driver.quit()

            driver = webdriver.Firefox(options=options)
            driver.implicitly_wait(5)

            driver.get(f"https://www.instagram.com/")
            time.sleep(5)

            username_input = driver.find_element(by=By.NAME, value="username")
            password_input = driver.find_element(by=By.NAME, value="password")

            username = random.choice(list(accounts_for_parsing.keys()))
            password = accounts_for_parsing[username]
            print(f"New - {username}")
            username_input.send_keys(username)
            password_input.send_keys(password)

            time.sleep(1)
            login_btn = driver.find_element(by=By.XPATH,
                                            value="/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[3]/button")
            time.sleep(1)
            login_btn.click()
            time.sleep(10)

        try:

            current_url = driver.current_url
            modified_url = "https://www.instagram.com/" + url + "?" + query_parameters

            driver.get(modified_url)

            # k = 0
            # while k < 6:
            #     try:
            #         raw_data_btn = driver.find_element(By.ID, value="rawdata-tab")
            #         raw_data_btn.click()
            #         break
            #     except:
            #         time.sleep(2)
            #         k += 1
            raw_data_btn = driver.find_element(By.ID, value="rawdata-tab")
            raw_data_btn.click()
            time.sleep(2)

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//pre")))
            pre_tag = driver.find_element(By.XPATH, "//pre")

            json_script = pre_tag.text
            json_parsed = json.loads(json_script)
            json_list.append(json_parsed)

        except Exception as e:
            print(e)
    time.sleep(2)
    driver.quit()

    print("Posts and reels data collecting is done!")

    account_image = None

    print("Start downloading media...")
    for json_data in json_list:

        item_list = json_data.get("items", [])

        for item in item_list:

            post_id = item.get("id")

            cursor.execute(f"SELECT post_id FROM `posts` WHERE post_id = '{post_id}'")
            post_id_in_db = cursor.fetchall()

            cursor.execute(f"SELECT reel_id FROM `reels` WHERE reel_id = '{post_id}'")
            reel_id_in_db = cursor.fetchall()

            if reel_id_in_db or post_id_in_db:
                continue

            account_image = item.get("user", {}).get("hd_profile_pic_url_info", {}).get("url")
            post_preview_download_link = item.get("image_versions2", {}).get("candidates", [{}])[0].get("url")
            media_downloading(post_preview_download_link, f"{account_name}/posts/{post_id}_preview.jpg")
            s3.upload_file(f"{account_name}/posts/{post_id}_preview.jpg",
                           bucket_name,
                           f"{account_name}/posts/{post_id}_preview.jpg")

            date_taken = item.get("taken_at")
            date_of_release = datetime.fromtimestamp(date_taken)

            post_text = item.get("caption", {}).get("text", "No caption")

            post_text = post_text.replace("'", "").replace('"', "")

            carousel_media = item.get("carousel_media", [])
            if carousel_media:
                cur_post = Post()
                cur_post.post_preview = f"{account_name}/posts/{post_id}_preview.jpg"
                cur_post.post_id = post_id
                cur_post.post_text = post_text
                cur_post.date_of_release = date_of_release

                cur_post_media_list = []

                for media in carousel_media:
                    cur_post_media = PostMedia()
                    cur_post_media.post_id = post_id

                    image_url = media.get("image_versions2", {}).get("candidates", [{}])[0].get("url")
                    media_id = str(media.get("pk"))
                    if image_url:
                        cur_post_media.media_type = "image"
                        cur_post_media.link_to_download = image_url
                        cur_post_media.post_image = f"{account_name}/posts/{media_id + '_img'}.jpg"
                        print("carousel image added")
                        cur_post_media_list.append(cur_post_media)

                    video_versions = media.get("video_versions", [])
                    if video_versions:
                        cur_post_media = PostMedia()
                        cur_post_media.post_id = post_id
                        video_url = video_versions[0].get("url")
                        if video_url:
                            cur_post_media.media_type = "video"
                            cur_post_media.link_to_download = video_url
                            cur_post_media.post_image = f"{account_name}/posts/{media_id + '_vid'}.mp4"
                            print("carousel video added")
                        cur_post_media_list.append(cur_post_media)

                cursor.execute(
                    f"INSERT INTO `posts`(post_id, account_id, post_text, "
                    f"post_preview, date_of_release, last_update_date) "
                    f"VALUES('{cur_post.post_id}', '{account_id}', '{cur_post.post_text}', '{cur_post.post_preview}',"
                    f" '{cur_post.date_of_release}', '{datetime.now().date()}')")

                for post_media in cur_post_media_list:
                    media_downloading(post_media.link_to_download, post_media.post_image)
                    cursor.execute(f"INSERT INTO `posts_media`(post_id, post_image, media_type) "
                                   f"VALUES('{post_media.post_id}',"
                                   f" '{post_media.post_image}',"
                                   f" '{post_media.media_type}')")

                    s3.upload_file(post_media.post_image, bucket_name, post_media.post_image)
                # db_con.commit()
            else:
                video_versions = item.get("video_versions", [])
                media_id = str(item.get("pk"))
                if video_versions:
                    cur_reel = Reel()
                    cur_reel.reel_id = post_id
                    cur_reel.reel_text = post_text
                    cur_reel.date_of_release = date_of_release
                    video_url = video_versions[0].get("url")
                    if video_url:
                        cur_reel.link_to_download_vid = video_url
                        cur_reel.reel_video = f"{account_name}/reels/{media_id + '_vid'}.mp4"
                        print("single video added")

                    image_url = item.get("image_versions2", {}).get("candidates", [{}])[0].get("url")
                    if image_url:
                        cur_reel.link_to_download_prev = image_url
                        cur_reel.reel_preview = f"{account_name}/reels/{media_id + '_preview'}.jpg"

                    media_downloading(cur_reel.link_to_download_vid, cur_reel.reel_video)
                    media_downloading(cur_reel.link_to_download_prev, cur_reel.reel_preview)

                    cursor.execute(f"INSERT INTO `reels`(reel_id, account_id, "
                                   f"reel_text, date_of_release, last_update_date, reel_image)"
                                   f" VALUES('{cur_reel.reel_id}', '{account_id}', '{cur_reel.reel_text}',"
                                   f" '{cur_reel.date_of_release}', '{datetime.now().date()}',"
                                   f" '{cur_reel.reel_video}')")

                    s3.upload_file(cur_reel.reel_video, bucket_name, cur_reel.reel_video)
                    s3.upload_file(cur_reel.reel_preview, bucket_name, cur_reel.reel_preview)

                    # db_con.commit()
                else:
                    cur_post = Post()
                    cur_post.post_id = post_id
                    cur_post.post_text = post_text
                    cur_post.post_preview = f"{account_name}/posts/{post_id}_preview.jpg"
                    cur_post.date_of_release = date_of_release

                    cur_post_media = PostMedia()
                    cur_post_media.post_id = post_id

                    media_id = str(item.get("pk"))

                    image_url = item.get("image_versions2", {}).get("candidates", [{}])[0].get("url")
                    if image_url:
                        cur_post_media.media_type = "image"
                        cur_post_media.link_to_download = image_url
                        cur_post_media.post_image = f"{account_name}/posts/{media_id + '_img'}.jpg"

                        cursor.execute(
                            f"INSERT INTO `posts`(post_id, account_id, post_text,"
                            f" post_preview, date_of_release, last_update_date) "
                            f"VALUES('{cur_post.post_id}', '{account_id}', '{cur_post.post_text}',"
                            f" '{cur_post.post_preview}',"
                            f" '{cur_post.date_of_release}', '{datetime.now().date()}')")

                        cursor.execute(f"INSERT INTO `posts_media`(post_id, post_image, media_type) "
                                       f"VALUES('{cur_post_media.post_id}',"
                                       f" '{cur_post_media.post_image}',"
                                       f" '{cur_post_media.media_type}')")

                        # db_con.commit()

                    media_downloading(cur_post_media.link_to_download, cur_post_media.post_image)

                    s3.upload_file(cur_post_media.post_image, bucket_name, cur_post_media.post_image)

    db_con.commit()
    if account_image:
        media_downloading(account_image, f"{account_name}/profile_pic/{account_name}_avatar.jpg")
        s3.upload_file(f"{account_name}/profile_pic/{account_name}_avatar.jpg", bucket_name,
                       f"{account_name}/profile_pic/{account_name}_avatar.jpg")
    print("Posts and Reels media is downloaded!")
    print("Start stories parsing...")

    g = 0
    while g < 6:
        try:
            loader = Instaloader(save_metadata=False,
                                 user_agent="Mozilla/5.0 (Windows NT 10.0; WOW64) "
                                            "AppleWebKit/537.36 (KHTML, like Gecko)"
                                            " Chrome/85.0.4183.102 YaBrowser/20.9.3.136 Yowser/2.5 Safari/537.36",
                                 post_metadata_txt_pattern=None)

            username_ = random.choice(list(accounts_for_parsing.keys()))
            password_ = accounts_for_parsing[username]
            loader.login(username_, password_)
            loader.dirname_pattern = f"{account_name}/stories"
            loader.download_profile(f"{account_name}", download_stories_only=True, profile_pic=False)
        except:
            g += 1
            try:
                loader.close()
            except:
                continue

    for path in [i for i in os.listdir(f"{account_name}/stories") if (i.endswith(".jpg") or i.endswith(".mp4"))]:
        no_resolution_path = path.split(".")[0]
        story_id = f"{no_resolution_path}_story"

        cursor.execute(f"SELECT story_id FROM `stories` WHERE story_id = '{story_id}'")
        story_id_in_db = cursor.fetchall()
        if story_id_in_db:
            continue

        story_date = no_resolution_path.split("_")[0]
        story_date = datetime.strptime(story_date, '%Y-%m-%d')
        if os.path.exists(f"{account_name}/stories/{no_resolution_path}.mp4"):
            cursor.execute(f"INSERT INTO `stories`(story_id, account_id, date_of_release, story_image)"
                           f" VALUES('{story_id}', '{account_id}', '{story_date}',"
                           f" '{account_name}/stories/{no_resolution_path}.mp4')")
            # db_con.commit()

            s3.upload_file(f"{account_name}/stories/{no_resolution_path}.mp4", bucket_name,
                           f"{account_name}/stories/{no_resolution_path}.mp4")

            s3.upload_file(f"{account_name}/stories/{no_resolution_path}.jpg", bucket_name,
                           f"{account_name}/stories/{no_resolution_path}_preview.jpg")

        else:
            cursor.execute(f"INSERT INTO `stories`(story_id, account_id, date_of_release, story_image)"
                           f" VALUES('{story_id}', '{account_id}', '{story_date}',"
                           f" '{account_name}/stories/{no_resolution_path}.jpg')")
            # db_con.commit()

            s3.upload_file(f"{account_name}/stories/{no_resolution_path}.jpg", bucket_name,
                           f"{account_name}/stories/{no_resolution_path}.jpg")
    db_con.commit()
    print("Stories parsing and stories media is done!")
    cursor.execute(f"SELECT id FROM `stories` WHERE account_id = '{account_id}'")
    stories_count = len(cursor.fetchall())
    cursor.execute(f"SELECT post_id FROM `posts` WHERE account_id = '{account_id}'")
    posts_count = len(cursor.fetchall())

    cursor.execute(f"SELECT reel_id FROM `reels` WHERE account_id = '{account_id}'")
    reels_count = len(cursor.fetchall())

    cursor.execute(f"UPDATE `accounts` set account_image = '{account_name}/profile_pic/{account_name}_avatar.jpg',"
                   f" posts_count = '{posts_count}',"
                   f" reels_count = '{reels_count}',"
                   f" stories_count = '{stories_count}' WHERE account_id = {account_id}")

    db_con.commit()
    cursor.close()
    db_con.close()
    print("Deleting local folder...")
    zip_folder(f"{account_name}/", f"{account_name}.zip")
    s3.upload_file(f"{account_name}.zip", bucket_name, f"{account_name}/{account_name}.zip")
    shutil.rmtree(f"{account_name}/")
    os.remove(f"{account_name}.zip")
    print("Deleting local folder is done!")
    print("Parsing is done!")


# instagram_accounts_parsing("adidas", "1", 1)
# instagram_accounts_parsing("nike", 1, 1, 1)
