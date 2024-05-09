import mysql.connector


def create_database_local_connection():

    database_connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        passwd="lapa21",
        database="instagram",
    )

    cursor = database_connection.cursor()
    return database_connection, cursor


def create_group_table():
    db_con, cursor = create_database_local_connection()
    cursor.execute("CREATE TABLE `groups` ("
                   "group_id INT PRIMARY KEY AUTO_INCREMENT,"
                   "group_name VARCHAR(255));")
    db_con.commit()
    cursor.close()
    db_con.close()


def create_accounts_table():
    db_con, cursor = create_database_local_connection()
    cursor.execute("CREATE TABLE `accounts` ("
                   "account_id VARCHAR(512) PRIMARY KEY,"
                   "group_id INT,"
                   "account_name VARCHAR(255),"
                   "last_update_date DATE,"
                   "account_image VARCHAR(512),"
                   "posts_count INT,"
                   "stories_count INT,"
                   "reels_count INT,"
                   "FOREIGN KEY (group_id) REFERENCES `groups`(group_id)"
                   ");")
    db_con.commit()
    cursor.close()
    db_con.close()


def create_posts_table():
    db_con, cursor = create_database_local_connection()
    cursor.execute("CREATE TABLE `posts` ("
                   "post_id VARCHAR(128) PRIMARY KEY,"
                   "account_id VARCHAR(512),"
                   "post_text TEXT,"
                   "post_preview VARCHAR(512),"
                   "date_of_release DATE,"
                   "last_update_date DATE,"
                   "is_carousel INT,"
                   "FOREIGN KEY (account_id) REFERENCES `accounts`(account_id)"
                   ");")
    db_con.commit()
    cursor.close()
    db_con.close()


def create_posts_media_table():
    db_con, cursor = create_database_local_connection()
    cursor.execute("CREATE TABLE `posts_media` ("
                   "id INT PRIMARY KEY AUTO_INCREMENT,"
                   "post_id VARCHAR(128),"
                   "post_image VARCHAR(512),"
                   "media_type VARCHAR(128),"
                   "FOREIGN KEY (post_id) REFERENCES `posts`(post_id)"
                   ");")
    db_con.commit()
    cursor.close()
    db_con.close()


def create_reels_table():
    db_con, cursor = create_database_local_connection()
    cursor.execute("CREATE TABLE `reels` ("
                   "id INT PRIMARY KEY AUTO_INCREMENT,"
                   "reel_id VARCHAR(128) UNIQUE,"
                   "account_id VARCHAR(512),"
                   "reel_text TEXT,"
                   "date_of_release DATE,"
                   "last_update_date DATE,"
                   "reel_image VARCHAR(512),"
                   "FOREIGN KEY (account_id) REFERENCES `accounts`(account_id)"
                   ");")
    db_con.commit()
    cursor.close()
    db_con.close()


def create_stories_table():
    db_con, cursor = create_database_local_connection()
    cursor.execute("CREATE TABLE `stories` ("
                   "id INT PRIMARY KEY AUTO_INCREMENT,"
                   "story_id VARCHAR(128),"
                   "account_id VARCHAR(512),"
                   "date_of_release DATE,"
                   "story_image VARCHAR(512),"
                   "media_type VARCHAR(128),"
                   "on_story_link VARCHAR(512),"
                   "FOREIGN KEY (account_id) REFERENCES `accounts`(account_id)"
                   ");")
    db_con.commit()
    cursor.close()
    db_con.close()


# create_group_table()
# create_accounts_table()
# create_posts_table()
# create_posts_media_table()
# create_reels_table()
# create_stories_table()

