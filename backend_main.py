import multiprocessing
import os
import shutil
import time
import zipfile
import aiofiles
import aiohttp
import asyncio

from flask import Flask, render_template, redirect, request, Response, session, send_file, jsonify

import boto3
from botocore.client import Config

from database_manage.db_creation import create_database_local_connection
from main import instagram_accounts_parsing

from db_objects_management.db_account_management import delete_accounts_info, delete_accounts_media
from flask_apscheduler import APScheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = "rtergkcx2312~@!3dsadase315240"


flask_scheduler = APScheduler()


async def download_media(session, url, filename):
    async with session.get(url) as response:
        if response.status == 200:
            async with aiofiles.open(filename, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    await f.write(chunk)
            print(f"{filename} downloaded successfully")
        else:
            print(f"Failed to download {filename}")


async def download_and_zip_media(media_urls, output_zip):
    async with aiohttp.ClientSession(trust_env=True, connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = []
        for i, url in enumerate(media_urls):
            if 'jpg' in url:
                filename = f"media_{i+1}.jpg"
            else:
                filename = f"media_{i + 1}.mp4"
            task = download_media(session, url, filename)
            tasks.append(task)
        await asyncio.gather(*tasks)

    # Создаем zip-архив
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for i, url in enumerate(media_urls):
            if 'jpg' in url:
                filename = f"media_{i+1}.jpg"
            else:
                filename = f"media_{i+1}.mp4"
            zipf.write(filename)
            os.remove(filename)


def daily_instagram_accounts_parsing():
    print("STARTED!!!")
    db_con, cursor = create_database_local_connection()
    cursor.execute("SELECT account_name, group_id FROM `accounts`")
    accounts_info = cursor.fetchall()
    for account in accounts_info:
        parse_process = multiprocessing.Process(target=instagram_accounts_parsing, args=(account[1], account[0], 1,))
        parse_process.start()
        parse_process.join()
        parse_process.close()
        time.sleep(60)
    cursor.close()
    db_con.close()


def instagram_accounts_parsing_list_edition(accounts_list, group_id):
    for account_name in accounts_list:
        instagram_accounts_parsing(group_id, account_name, 9, )
        time.sleep(60)


s3_resource = boto3.resource(
        's3',
        endpoint_url='https://s3.timeweb.com',
        region_name='ru-1',
        aws_access_key_id='R1ZWBQWDJ44WUXQGUF5A',
        aws_secret_access_key='t5nHJ1K1aisTgOuDVLZlgSA5bwUhvip68CCBNx6w',
        config=Config(s3={'addressing_style': 'path'})
    )

s3 = boto3.client(
    's3',
    endpoint_url='https://s3.timeweb.cloud',
    region_name='ru-1',
    aws_access_key_id='R1ZWBQWDJ44WUXQGUF5A',
    aws_secret_access_key='t5nHJ1K1aisTgOuDVLZlgSA5bwUhvip68CCBNx6w',
    config=Config(s3={'addressing_style': 'path'})
)

bucket_name = "49a2f75b-d806e76b-e741-49be-a128-315f48f934c4"
bucket_obj = s3_resource.Bucket(bucket_name)


def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))


def delete_local_file(filename):
    time.sleep(10)
    while True:
        try:
            os.remove(filename)
            break
        except:
            time.sleep(5)


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
@app.route('/1', methods=["GET", "POST"])
@app.route('/index/1', methods=["GET", "POST"])
def default_index():
    db_con, cursor = create_database_local_connection()
    cursor.execute("SELECT * FROM `groups`")
    groups = cursor.fetchall()
    if "Default" not in [i[1] for i in groups]:
        cursor.close()
        db_con.close()
        return redirect("/2")
    groups_count = len(groups)
    if groups_count == 0:
        cursor.execute("INSERT INTO `groups`(group_id, group_name) VALUES(1, 'Default')")
        db_con.commit()
        cursor.close()
        db_con.close()
        return redirect("/1")
    cursor.execute("SELECT * FROM `groups` WHERE group_id = 1")
    current_group = cursor.fetchone()

    cursor.execute("SELECT * FROM `accounts` WHERE group_id = 1")
    accounts = cursor.fetchall()
    accounts = [i for i in accounts if i[-1]]
    accounts_count = len(accounts)
    cursor.close()
    db_con.close()
    return render_template("main.html", groups=groups, current_group=current_group, accounts_count=accounts_count,
                           accounts=accounts)


@app.route('/<int:group_id>', methods=["GET", "POST"])
@app.route('/index/<int:group_id>', methods=["GET", "POST"])
def index(group_id):
    db_con, cursor = create_database_local_connection()
    cursor.execute("SELECT * FROM `groups`")
    groups = cursor.fetchall()
    cursor.execute(f"SELECT * FROM `groups` WHERE group_id = {group_id}")
    current_group = cursor.fetchone()
    cursor.execute(f"SELECT * FROM `accounts` WHERE group_id = {group_id}")
    accounts = cursor.fetchall()
    accounts = [i for i in accounts if i[-1]]
    accounts_count = len(accounts)
    cursor.execute("SELECT story_id FROM `stories` JOIN `accounts` ON `stories`.account_id = `accounts`.account_id")
    stories = cursor.fetchall()
    stories_count = len(set(stories))
    cursor.close()
    db_con.close()
    return render_template("main.html", groups=groups, current_group=current_group, accounts_count=accounts_count,
                           stories_count=stories_count, accounts=accounts)


@app.route('/add_new_group', methods=["POST"])
def add_new_group():
    group_name = request.form['group-name']
    db_con, cursor = create_database_local_connection()
    cursor.execute(f"INSERT INTO `groups`(group_name) VALUES('{group_name}')")
    db_con.commit()
    cursor.execute(f"SELECT group_id FROM `groups` WHERE group_name = '{group_name}'")
    cur_group_id = cursor.fetchone()[0]
    cursor.close()
    db_con.close()
    return redirect(f"/{cur_group_id}")


@app.route('/delete_group/<int:group_id>', methods=["POST"])
def delete_group(group_id):
    db_con, cursor = create_database_local_connection()
    cursor.execute(f"SELECT account_id FROM `accounts` WHERE group_id = '{group_id}'")
    accounts_ids = [i[0] for i in cursor.fetchall()]
    cursor.execute(f"SELECT account_name FROM `accounts` WHERE group_id = '{group_id}'")
    accounts_names_list = [i[0] for i in cursor.fetchall()]
    deleting_process = multiprocessing.Process(target=delete_accounts_media, args=(accounts_names_list,))
    deleting_process.start()
    for acc_id in accounts_ids:
        delete_accounts_info(acc_id)
    cursor.execute(f"DELETE FROM `groups` WHERE group_id = '{group_id}'")
    db_con.commit()
    cursor.close()
    db_con.close()
    return "to be redirected"


@app.route('/add_new_acc', methods=["POST"])
def add_new_acc():
    db_con, cursor = create_database_local_connection()
    group_name = request.form['group']
    cursor.execute(f"SELECT group_id FROM `groups` WHERE group_name = '{group_name}'")
    group_id = cursor.fetchone()[0]
    acc_name = request.form['account-link']
    db_con.close()
    cursor.close()
    parse_process = multiprocessing.Process(target=instagram_accounts_parsing, args=(group_id, acc_name, 5,))
    parse_process.start()
    return redirect(f"/{group_id}")


@app.route('/add_new_several_accounts', methods=["POST"])
def add_new_several_accounts():
    db_con, cursor = create_database_local_connection()
    accounts_list = request.form.getlist("account-link")
    group_name = request.form['group']
    cursor.execute(f"SELECT group_id FROM `groups` WHERE group_name = '{group_name}'")
    group_id = cursor.fetchone()[0]
    parsing_list_process = multiprocessing.Process(target=instagram_accounts_parsing_list_edition,
                                                   args=(accounts_list, group_id,))
    parsing_list_process.start()
    db_con.close()
    cursor.close()
    return redirect(f"/{group_id}")


@app.route('/change_account_group', methods=["POST"])
def change_account_group():
    db_con, cursor = create_database_local_connection()
    group_name = request.form['group-name']
    account_id = request.form['accountIdField']
    cursor.execute(f"SELECT group_id FROM `groups` WHERE group_name = '{group_name}'")
    group_id = cursor.fetchone()[0]
    cursor.execute(f"UPDATE `accounts` SET group_id = '{group_id}' WHERE account_id = '{account_id}'")
    db_con.commit()
    db_con.close()
    cursor.close()
    return redirect(f"/{group_id}")


@app.route('/delete_acc/<string:acc_id>', methods=["POST"])
def delete_acc(acc_id):
    db_con, cursor = create_database_local_connection()
    cursor.execute(f"SELECT account_name FROM `accounts` WHERE account_id = '{acc_id}'")
    account_name = cursor.fetchone()[0]
    delete_accounts_info(acc_id)
    delete_process = multiprocessing.Process(target=delete_accounts_media, args=([account_name],))
    delete_process.start()
    return "to be redirected"


@app.route('/posts/<string:account_name>', methods=["GET", "POST"])
def posts_page(account_name):
    db_con, cursor = create_database_local_connection()

    cursor.execute(f"SELECT `posts`.post_id, `posts`.post_text, `posts`.date_of_release, `posts`.post_preview,"
                   f" `posts`.is_carousel"
                   f" FROM `posts`"
                   f" JOIN `accounts` ON `posts`.account_id = `accounts`.account_id"
                   f" JOIN `posts_media` ON `posts_media`.post_id = `posts`.post_id"
                   f" WHERE `accounts`.account_name = '{account_name}';")

    posts = cursor.fetchall()

    res_posts = []

    for post in posts:
        if post not in res_posts:
            res_posts.append(post)

    posts_count = len(res_posts)
    cursor.close()
    db_con.close()
    return render_template("posts.html", posts=res_posts[::-1], posts_count=posts_count, account_name=account_name)


@app.route('/reels/<string:account_name>', methods=["GET", "POST"])
def reels_page(account_name):
    db_con, cursor = create_database_local_connection()

    cursor.execute(f"SELECT account_id FROM `accounts` WHERE account_name = '{account_name}'")

    acc_id = cursor.fetchone()[0]

    cursor.execute(f"SELECT reel_id, reel_text, date_of_release, reel_image FROM `reels` WHERE account_id = '{acc_id}';")

    reels = cursor.fetchall()
    # reels = [list(i) for i in reels]

    # for idx, reel in enumerate(reels):
    #     reels[idx] = reel + [reel[0].split("_")[0]]

    reels_count = len(reels)
    cursor.close()
    db_con.close()
    return render_template("reels.html", reels=reels[::-1], reels_count=reels_count, account_name=account_name)


@app.route('/stories/<string:account_name>', methods=["GET", "POST"])
def stories_page(account_name):
    db_con, cursor = create_database_local_connection()

    cursor.execute(f"SELECT account_id FROM `accounts` WHERE account_name = '{account_name}'")

    acc_id = cursor.fetchone()[0]

    cursor.execute(f"SELECT story_id, date_of_release, story_image FROM `stories` WHERE account_id = '{acc_id}';")

    stories = cursor.fetchall()
    # stories = [list(i) for i in stories]
    #
    # for idx, story in enumerate(stories):
    #     stories[idx][0] = stories[idx][0][:-6]

    stories_count = len(stories)
    cursor.close()
    db_con.close()
    return render_template("stories.html", stories=stories[::-1], stories_count=stories_count, account_name=account_name)


@app.route('/download_certain_post/<string:post_id>', methods=["POST"])
def download_certain_post(post_id):
    db_con, cursor = create_database_local_connection()

    cursor.execute(f"SELECT post_image FROM `posts_media` WHERE post_id = '{post_id}'")

    post_image_list = [i[0] for i in cursor.fetchall()]
    cursor.execute(f"SELECT `accounts`.account_name FROM `posts` JOIN `accounts` "
                   f"ON `posts`.account_id = `accounts`.account_id WHERE `posts`.post_id = '{post_id}'")

    account_name = cursor.fetchone()[0]

    os.makedirs(f"{post_id}/", exist_ok=True)

    for post_image in post_image_list:
        s3.download_file(bucket_name, f"{post_image}", f"{post_id}/{post_image.split('/')[-1]}")

    zip_folder(f"{post_id}/", f"{post_id}.zip")
    shutil.rmtree(f"{post_id}/")

    cursor.close()
    db_con.close()
    return post_id


@app.route('/download_selected_posts/', methods=["POST"])
def download_selected_posts():
    selected_checkboxes = request.form.getlist('checkbox')
    account_name = request.form.get('checkboxes-hidden-acc-name')
    db_con, cursor = create_database_local_connection()
    media_to_download_list = []
    for el in selected_checkboxes:
        cursor.execute(f"SELECT post_image FROM `posts_media` WHERE post_id = '{el}'")
        cur_media = cursor.fetchall()
        if cur_media:
            for i in cur_media:
                media_to_download_list.append("https://s3.timeweb.cloud/"
                                              "49a2f75b-d806e76b-e741-49be-a128-315f48f934c4/" + i[0])

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(download_and_zip_media(media_to_download_list, f"{account_name}_selected_posts.zip"))
    loop.close()
    cursor.close()
    db_con.close()
    delete_process = multiprocessing.Process(target=delete_local_file, args=(f"{account_name}_selected_posts.zip",))
    delete_process.start()
    return send_file(f"{account_name}_selected_posts.zip")


@app.route('/download_selected_reels/', methods=["POST"])
def download_selected_reels():
    selected_checkboxes = request.form.getlist('checkbox')
    account_name = request.form.get('checkboxes-hidden-acc-name')
    db_con, cursor = create_database_local_connection()
    media_to_download_list = []
    for el in selected_checkboxes:
        cursor.execute(f"SELECT reel_image FROM `reels` WHERE reel_id = '{el}'")
        cur_media = cursor.fetchall()
        if cur_media:
            for i in cur_media:
                media_to_download_list.append("https://s3.timeweb.cloud/"
                                              "49a2f75b-d806e76b-e741-49be-a128-315f48f934c4/" + i[0])
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(download_and_zip_media(media_to_download_list, f"{account_name}_selected_reels.zip"))
    loop.close()
    cursor.close()
    db_con.close()
    delete_process = multiprocessing.Process(target=delete_local_file, args=(f"{account_name}_selected_reels.zip",))
    delete_process.start()
    return send_file(f"{account_name}_selected_reels.zip")


@app.route('/download_selected_stories/', methods=["POST"])
def download_selected_stories():
    selected_checkboxes = request.form.getlist('checkbox')
    account_name = request.form.get('checkboxes-hidden-acc-name')
    db_con, cursor = create_database_local_connection()
    media_to_download_list = []
    for el in selected_checkboxes:
        cursor.execute(f"SELECT story_image FROM `stories` WHERE story_id = '{el}'")
        cur_media = cursor.fetchall()
        if cur_media:
            for i in cur_media:
                media_to_download_list.append("https://s3.timeweb.cloud/"
                                              "49a2f75b-d806e76b-e741-49be-a128-315f48f934c4/" + i[0])
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(download_and_zip_media(media_to_download_list, f"{account_name}_selected_stories.zip"))
    loop.close()
    cursor.close()
    db_con.close()
    delete_process = multiprocessing.Process(target=delete_local_file, args=(f"{account_name}_selected_stories.zip",))
    delete_process.start()
    return send_file(f"{account_name}_selected_stories.zip")


@app.route('/send_local_zip/<string:post_id>', methods=["GET", "POST"])
def send_local_zip(post_id):
    delete_process = multiprocessing.Process(target=delete_local_file, args=(f"{post_id}.zip",))
    delete_process.start()
    return send_file(f"{post_id}.zip")


def main():
    flask_scheduler.add_job(id='Update Inst Accs Task', func=daily_instagram_accounts_parsing,
                            trigger='cron', hour=0, minute=0, second=0)
    flask_scheduler.start()
    app.run(host="0.0.0.0", debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
