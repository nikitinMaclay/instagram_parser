from itertools import chain

import boto3
from botocore.config import Config

from database_manage.db_creation import create_database_local_connection


s3 = boto3.client(
    's3',
    endpoint_url='https://s3.timeweb.cloud',
    region_name='ru-1',
    aws_access_key_id='R1ZWBQWDJ44WUXQGUF5A',
    aws_secret_access_key='t5nHJ1K1aisTgOuDVLZlgSA5bwUhvip68CCBNx6w',
    config=Config(s3={'addressing_style': 'path'})
)

bucket_name = "49a2f75b-d806e76b-e741-49be-a128-315f48f934c4"


def delete_accounts_info(acc_id):
    db_con, cursor = create_database_local_connection()

    cursor.execute(f"SELECT post_id FROM `posts` WHERE account_id = '{acc_id}'")
    posts_ids = [i[0] for i in cursor.fetchall()]

    cursor.execute(f"SELECT reel_id FROM `reels` WHERE account_id = '{acc_id}'")
    reels_ids = [i[0] for i in cursor.fetchall()]

    cursor.execute(f"SELECT id FROM `stories` WHERE account_id = '{acc_id}'")
    stories_ids = [i[0] for i in cursor.fetchall()]

    posts_medias = []

    for el in posts_ids:
        cursor.execute(f"SELECT id FROM `posts_media` WHERE post_id = '{el}'")
        posts_medias_id = [i[0] for i in cursor.fetchall()]
        posts_medias.append(posts_medias_id)

    posts_medias = list(chain.from_iterable(posts_medias))

    for post_media_id in posts_medias:
        cursor.execute(f"DELETE FROM `posts_media` WHERE id = '{post_media_id}'")
        db_con.commit()

    for reel_id in reels_ids:
        cursor.execute(f"DELETE FROM `reels` WHERE reel_id = '{reel_id}'")
        db_con.commit()

    for post_id in posts_ids:
        cursor.execute(f"DELETE FROM `posts` WHERE post_id = '{post_id}'")
        db_con.commit()

    for story_id in stories_ids:
        cursor.execute(f"DELETE FROM `stories` WHERE id = '{story_id}'")
        db_con.commit()

    cursor.execute(f"DELETE FROM `accounts` WHERE account_id = '{acc_id}'")
    db_con.commit()

    cursor.close()
    db_con.close()


def delete_accounts_media(accounts_ids):
    for acc_id in accounts_ids:
        print(acc_id)
        db_con, cursor = create_database_local_connection()
        cursor.execute(f"SELECT account_name FROM `accounts` WHERE account_id = '{acc_id}'")
        acc_name = cursor.fetchone()[0]
        cursor.close()
        db_con.close()
        objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=f"{acc_name}/")

        if 'Contents' in objects:
            for obj in objects['Contents']:
                s3.delete_object(Bucket=bucket_name, Key=obj['Key'])

        delete_accounts_info(acc_id)


# delete_accounts_media([68])