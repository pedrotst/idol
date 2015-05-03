import tweepy
import urllib
import requests
import os
import json
import io
from PIL import Image, ImageDraw

_consumer_key = 'ITxhHe7UB4Leanb9eLZYqEQ6B'
_consumer_secret = 'SRdPZz1z5vsnh59BRHdsXNdfNTaJCqKY3TJb0VRG6xYV7DUWUQ'
_access_token = '161067536-Xpr059ztjAtSw7GUMeKJAzzg9rJxGBoED6FDxF9H'
_access_token_secret = 'pGfS6i7iUWPSTAkDIlt2iqwRj7itxw58gSmycjHhhEhAq'
_key = '65e8786f-3f22-4edc-a826-8cada32ca0de'


def _authorize():
    auth = tweepy.OAuthHandler(_consumer_key, _consumer_secret)
    auth.set_access_token(_access_token, _access_token_secret)
    return auth

def _ensure_folder(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
def _add_face_num(string, i):
    return string[:-4]+'-face'+str(i)+".jpg"

def _str_add_face(string):
    return string[:-4]+"-faces.jpg"

def draw_faces(img_path):
    img_file = open(img_path, 'rb')

    hp_url = 'https://api.idolondemand.com/1/api/sync/detectfaces/v1'
    auth = _authorize()
    api = tweepy.API(auth)

    data = {'apikey': _key}
    file = {'file': img_file}
    req = requests.post(hp_url, files = file, data = data)
    faces_list = json.loads(req.text).get('face')
    print(req.text)
    if len(faces_list) > 0:
        original_image = Image.open(img_file)
        draw = ImageDraw.Draw(original_image)
        for i, face in enumerate(faces_list):
            width, left, top, height = face['width'] , face['left'], face['top'], face['height']
            cut_left = int(left - (width*0.1))

            cut_right = int(left + (width*1.1))
            cut_bottom = int(top + (height*1.1))
            cut_top = int(top - (height * 0.1))

            croped_example = draw.rectangle([(cut_left, cut_top), (cut_right, cut_bottom)], outline = (255,0,0,255))
        original_image.save(_str_add_face(img_path))


def get_faces(hashtag, image_limit, save_whole_img = False):
    save_folder = '#'+hashtag+'-faces'
    _ensure_folder(save_folder)
    hp_url = 'https://api.idolondemand.com/1/api/sync/detectfaces/v1'
    auth = _authorize()
    api = tweepy.API(auth)
    cursor = tweepy.Cursor(api.search, q=hashtag, count=image_limit, lang='en')
    sponsor_list = []
    for i, tweet in enumerate(cursor.items(limit=image_limit)):
        media = tweet.entities.get("media")
        # print(media)
        if media is not None:
            media_url = media[0]['media_url_https']+":large"
            send_data = {'apikey': _key, 'url': media_url}
            req = requests.post(hp_url, data = send_data)
            face_dict = json.loads(req.text)
            # print(face_dict['face'])
            image_buffer = io.BytesIO(urllib.request.urlopen(media_url).read())
            original_image = Image.open(image_buffer)
            draw = ImageDraw.Draw(original_image)
            original_name = hashtag+'-'+str(i)+'.jpg'
            if save_whole_img:    
                original_image.save(os.path.join(save_folder, original_name))
            for j, face in enumerate(face_dict['face']):
                print(face)
                width, left, top, height = face['width'] , face['left'], face['top'], face['height']

                cut_left = int(left - (width*0.1))

                cut_right = int(left + (width*1.1))
                cut_bottom = int(top + (height*1.1))
                cut_top = int(top - (height * 0.1))
                print(cut_left, cut_top, cut_right, cut_bottom)
                croped_sample = original_image.crop((cut_left, cut_top, cut_right, cut_bottom))
                croped_name = _add_face_num(original_name, j)
                croped_path = os.path.join(save_folder, croped_name)
                croped_sample.save(croped_path)


def hash_sponsors(hashtag, image_limit, image_type = 'complex_3d'):
    save_file = hashtag+"-sponsors"
    _ensure_folder(save_file)

    hp_url = 'https://api.idolondemand.com/1/api/sync/recognizeimages/v1'
    auth = _authorize()
    api = tweepy.API(auth)

    cursor = tweepy.Cursor(api.search, q=hashtag, count=image_limit, lang='en')
    sponsor_list = []
    for i, tweet in enumerate(cursor.items(limit=image_limit)):
        media = tweet.entities.get("media")
        if media is not None:
            media_url = media[0]['media_url_https']+":large"
            data = {'apikey': _key, 'image_type': image_type, 'url': media_url}
            req = requests.post(hp_url, data = data)
            sponsors = json.loads(req.text).get('object')
            print(media_url)
            if len(sponsors) > 0:
                img_buffer = io.BytesIO(urllib.request.urlopen(media_url).read())
                original_image = Image.open(img_buffer)
                draw = ImageDraw.Draw(original_image)
                for spon_num, sponsor in enumerate(sponsors):
                    coords_l = []
                    if sponsor['name'] not in sponsor_list:
                        sponsor_list.append(sponsor['name'])
                    for coords in sponsor['corners']:
                        x, y = coords['x'], coords['y']
                        coords_l.append((x,y))
                    coords_l.append(coords_l[0])
                    print(coords_l)
                    draw.line(coords_l, fill=(255,0,0,255), width = 5)
                original_image.save(os.path.join(save_file, str(i)+".jpg"))

    with open(os.path.join(save_file, 'sponsor_list.txt'), 'w') as sponsor_file:
        for item in sponsor_list:
            sponsor_file.write("{}\n".format(item))

if __name__ == '__main__':
    # hash_sponsors('AH8', 300)
    get_faces('AH8', 100, save_whole_img=True)
    # draw_faces(os.path.join('#AH8-faces', 'AH8-26.jpg'))

    # print("Hi! Welcome to IDOL Twitter, what do you want to do?")
    # print("1- Get the Sponsors of a given hash")
    # print("2- Get the faces of a particular hash")
    # print("3- Draw the face rectangle of a given file")

    # choice = input()
    # if choice == "1":
    #     hashtag = input("Insert the hashtag you want to search for: ")
    #     hash_sponsors(hashtag, 400)
    # elif choice == "2":
    #     hashtag = input("Insert the hashtag you want to search for: ")
    #     get_faces(hashtag, 400)
    # elif choice == "3":
    #     hashtag = input("Insert the hashtag you want to search for: ")