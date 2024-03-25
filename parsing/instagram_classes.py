class Post:
    def __init__(self):
        self.post_id = ""
        self.account_id = ""
        self.post_text = ""
        self.date_of_release = ""
        self.post_preview = ""
        self.link_to_download_preview = ""
        self.is_carousel = ""


class Reel:
    def __init__(self):
        self.reel_id = ""
        self.account_id = ""
        self.reel_text = ""
        self.date_of_release = ""
        self.reel_video = ""
        self.link_to_download_vid = ""
        self.link_to_download_prev = ""
        self.reel_preview = ""


class PostMedia:
    def __init__(self):
        self.post_id = ""
        self.post_image = ""
        self.media_type = ""
        self.link_to_download = ""


class Story:
    def __init__(self):
        self.story_id = ""
        self.account_id = ""
        self.date_of_release = ""
        self.story_image = ""
        self.media_type = ""


