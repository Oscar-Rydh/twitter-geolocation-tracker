from database.database import Database
from layers_method.extra_user_data import Extra_User_Data
import layers_method.user_locations as user_locations
import create_bounding_box_matrixes as bbtomatrix
import numpy as np
import layers_method.tweet_lang as lang
import layers_method.user_timezone as timezones

accuracy = 1

def get_users_data():
    db = Database('twitter-geo')
    return db.select_everything_from_users()

#Adds layers on top of another and chooses the middle highest point
def calculate_highest_point(layers):
    global accuracy
    nbr_rows = 360*accuracy
    nbr_cols = 180*accuracy
    result_matrix = np.zeros((nbr_rows, nbr_cols))
    for layer in layers:
        result_matrix = np.add(result_matrix, layer)

    max = np.max(result_matrix)
    indices = np.where(result_matrix == result_matrix.max())

    long_mid = int(len(indices[0])/2)
    lat_mid = int(len(indices[1])/2)
    long = indices[0][long_mid]
    lat = indices[1][lat_mid]

    # Figure out if we picked a incorrect coordinate
    error = False
    if result_matrix[long][lat] != max:
        error = True

    lat -= 90*accuracy
    long -= 180*accuracy
    return [lat, long, max, error]

def add_user_name_location_layer(user_name, all_layers, status_code=False):
    global accuracy
    user_location_value = 5
    user_name_bb = user_locations.get_bbox(user_name)
    if user_name_bb != None:
        layer = bbtomatrix.map_boundingbox_to_matrix(user_name_bb, accuracy, user_location_value)
        status_code = True
        all_layers.append(layer)
    else:
        print("User have no location")

def add_tweet_language_layer(user_lang, all_layers, status_code=False):
    global accuracy
    language_value = 1
    user_lang_bb = lang.get_bboxes(user_lang)
    if user_lang_bb != None:
        for bb in user_lang_bb:
            if len(bb) > 0:
                bb = bb[0]
                bb = [bb[0], bb[1], bb[2], bb[3]]
                layer = bbtomatrix.map_boundingbox_to_matrix(bb, accuracy, language_value/len(user_lang_bb))
                all_layers.append(layer)
                status_code = True
    else:
        print ("Got None for language:", user_lang)

def add_time_zone_layer(user_time_zone, all_layers, statuscode=False):
    global accuracy
    timezone_value = 1
    timezone_bbs = timezones.get_bboxes(user_time_zone)
    if timezone_bbs != None:
        for bb in timezone_bbs:
            layer = bbtomatrix.map_boundingbox_to_matrix(list(bb), accuracy, timezone_value/len(timezone_bbs))
            all_layers.append(layer)
            status_code = True
    else:
        print ("Got None for Timezone:", user_time_zone)


def main():
    db = Database('twitter-geo')
    users = get_users_data()
    nbr_of_coordinates = 100
    found_coordinates = []
    i = 0
    #Create layers for each user and print thier highest point
    for user in users:
        all_layers = []
        user_id = user[0]
        user_name = user[2]
        user_lang = user[8]
        user_time_zone = user[7]

        print ("Running user" , user_name)

        # Adding user specified location layer
        got_user_location = False

        add_user_name_location_layer(user_name, all_layers, got_user_location)

        #not done
        #add_user_language_layer(user_lang, all_layers)

        if user_time_zone != None:
            add_time_zone_layer(user_time_zone, all_layers)
        else:
            print ("Got none for user time zone")


        user_tweets = db.select_every_tweet_of_user(user_id)
        user_tweets = [list(elem) for elem in user_tweets]

        used_langs = []

        if len(user_tweets) > 0:
            for tweet in user_tweets:
                tweet_lang = tweet[14]
                if tweet_lang != None and tweet_lang not in used_langs:
                    used_langs.append(tweet_lang)
                    add_tweet_language_layer(tweet_lang, all_layers)



        #Handle Extra tweets
        extra_tweets = []
        print ('Getting extra data for:', user_name)
        if len(user_tweets) < 3:
            extra_user_data = Extra_User_Data(user_id)
            extra_tweets = extra_user_data.get_all_tweets()
        used_extra_time_zones = []
        used_extra_langs= []
        if len (extra_tweets) > 0:
            for tweet in extra_tweets:
                tweet_lang = extra_user_data.get_language_of_tweet(tweet)
                tweet_time_zone = extra_user_data.get_user_time_zone_of_tweet(tweet)

                if tweet_lang != None and tweet_lang not in used_extra_langs:
                    used_extra_langs.append(tweet_lang)
                    print ("Extra Lang is:", tweet_lang)
                    add_tweet_language_layer(tweet_lang, all_layers)
                if tweet_time_zone != None and tweet_time_zone not in used_extra_time_zones :
                    print ("Extra Time zone is:", tweet_time_zone)
                    used_extra_time_zones.append(tweet_time_zone)
                    add_time_zone_layer(tweet_time_zone, all_layers)

        result = calculate_highest_point(all_layers)
        print ('The user:', user_name, 'is located at: lat=',
        result[0], 'long=', result[1], 'with maxvalue=', result[2])
        #print ('Updating database')
        db.update_predicted_coordinates(result[0], result[1], result[2], user_id, result[3])
main()