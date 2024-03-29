""" Fichier de tools Strava """

#!/usr/bin/python3
# -*-coding:Utf-8 -*

import os
from datetime import datetime, timedelta
import requests
import urllib3

from stravalib import Client
from stravalib import model, unithelper as uh
from stravaweblib import WebClient, DataFormat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


__author__ = "Arnaud TORA"
__copyright__ = "Copyright 2020"
__credits__ = "Arnaud TORA"
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Arnaud TORA"
__status__ = "Dev"


AUTH_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"


def get_creds(creds_file):
    """
    Lecture et recuperation des identifiants de connexions
        - ID
        - SecretClient
        - Token
        - Code
        - RefreshCode
        - Email
        - Password

    :param creds_file: Le fichier de credentials
    :type creds_file: str

    :return: Un dictionnaire des credentials
    :rtype: dict
    """
    creds = {}

    with open(creds_file, "r") as fichier:
        contenu = fichier.readlines()
        for ligne in contenu:
            ligne = ligne.replace(" ", "")
            ligne = ligne.replace("\n", "")
            ligne = ligne.replace("\r", "")
            if ligne.startswith("ID"):
                creds["id"] = int(ligne.rsplit(":")[1])
            if ligne.startswith("SecretClient"):
                creds["SecretClient"] = ligne.rsplit(":")[1]
            if ligne.startswith("Token"):
                creds["Token"] = ligne.rsplit(":")[1]
            if ligne.startswith("Code"):
                creds["Code"] = ligne.rsplit(":")[1]
            if ligne.startswith("RefreshCode"):
                creds["RefreshCode"] = ligne.rsplit(":")[1]
            if ligne.startswith("Email"):
                creds["Email"] = ligne.rsplit(":")[1]
            if ligne.startswith("Password"):
                creds["Password"] = ligne.rsplit(":")[1]

    return creds


def refresh_acces_token(creds):
    """
    Refresh des tokens pour communiquer avec Strava 

    :param creds: Le dictionnaire de credentials
    :type creds: dict
    """
    payload = {
        'client_id': creds["id"],
        'client_secret': creds["SecretClient"],
        'refresh_token': creds["RefreshCode"],
        'grant_type': "refresh_token",
        'f': 'json'
    }

    print ("Requesting Token...")
    res = requests.post(AUTH_URL, data=payload, verify=False)
    access_token = res.json()['access_token']
    expiry_ts = res.json()['expires_at']
    creds["AccesToken"] = access_token

    print("Access Token = {}".format(creds["AccesToken"]))
    print("New token will expire at: ",end='\t')
    print(datetime.utcfromtimestamp(expiry_ts).strftime('%Y-%m-%d %H:%M:%S'))


def get_client(creds):
    """
    Mise a jour du client avec le nouveau token

    :param creds: Le dictionnaire de credentials
    :type creds: dict

    :return: La structure client
    :rtype: :class:`stravalib.client`
    """

    client = Client(access_token=creds["AccesToken"])
    return client


def display_athlete(client):
    """
    Affichage des informations de l'Athlete

    :param client: La structure client
    :type client: :class:`stravalib.client`
    """
    athlete = client.get_athlete()
    print ("\n### Display Athlete ###")
    print("Athlete's name is {} {}, based in {}, {}".format(athlete.firstname, athlete.lastname, athlete.city, athlete.country))
    print("Photo URL " + athlete.profile)
    print("all_run_totals : " + str(athlete.stats.all_run_totals.distance))
    print("all_bike_totals : " + str(athlete.stats.all_ride_totals.distance))


def display_activity(activity, client):
    """
        Affichage detaille de l'activite en parametre
            - id
            - name
            - kudos_count

    :param activity: L'activite a afficher
    :type activity: :class:`stravalib.model.Activity`

    :param client: La structure client
    :type client: :class:`stravalib.client`
    """

    data = {}
    data['id'] = activity.id
    data['name'] = activity.name
    data['kudos'] = activity.kudos_count
    data['gear_id'] = activity.gear_id
    # activity['start_date_local'] = activity['start_date_local']
    # activity['type'] = activity['type']
    # activity['distance'] = activity['distance']
    # activity['elapsed_time'] = activity['elapsed_time']
    print ("La derniere activite retrouvee est :")
    print (data)
    print ("Materiel : {}".format(client.get_gear(activity.gear_id)))


def get_last_activity(client):
    """
    Retourne la derniere activite

    :param client: La structure client
    :type client: :class:`stravalib.client`

    :return: La derniere activite
    :rtype: :class:`stravalib.model.Activity`
    """
    print ("\nGet last activity")
    for activity in client.get_activities(limit=1):
        return activity


def display_last_activity(client):
    """
    Affiche la derniere activite, de maniere detaille

    :param client: La structure client
    :type client: :class:`stravalib.client`
    """
    print ("\nDisplay last activity")
    for activity in client.get_activities(limit=1):
        display_activity(activity, client)


def display_n_activity(client, number):
    """
    Affichage simple des N dernieres activitees

    :param client: La structure client
    :type client: :class:`stravalib.client`

    :param n: Le nombre d'activite maximum
    :type n: int
    """

    print ("\nDisplay last {} activity".format(number))
    for activity in client.get_activities(limit=number):
        print("{0.id} - {0.name} - {0.moving_time}".format(activity))

def get_first_n_activity(client, after, before, type_act, number):
    """
    Retourne les N premieres activites

    :param client: La structure client
    :type client: :class:`stravalib.client`

    :param n: Le nombre d'activite maximum
    :type n: int

    :return: La derniere activite
    :rtype: :class:`stravalib.model.Activity`
    """

    list_act=[]
    print ("\nGet first {} activity".format(number))
    for activity in client.get_activities(after = after, before = before, limit=number):
        if type_act=="All":
            list_act.insert(0, activity)
        if(type_act=="Run" and activity.type=="Run"):
            list_act.insert(0, activity)
        if(type_act=="Ride" and activity.type=="Ride"):
            list_act.insert(0, activity)

    return list_act

def create_manual_run(client):
    """
    Creation d'une activite manuelle

    :param client: La structure client
    :type client: :class:`stravalib.client`

    :return: La derniere activite
    :rtype: :class:`stravalib.model.Activity`
    """

    print ("\nCreation d'une activite")
    now = datetime.now().replace(microsecond=0)
    activity = client.create_activity("[fake] Test_API_Strava - Envoi via l'API Python #GEEK",
        description="Debut de l'utilisation de l'API, ça ouvre pleins de possibilite :P",
        activity_type=model.Activity.RUN,
        start_date_local=now,
        elapsed_time=str(timedelta(hours=1, minutes=4, seconds=5).total_seconds()).replace('.0', ''),
        distance=uh.kilometers(15.2))

    print ("Activite cree, voir https://www.strava.com/activities/" + str(activity.id))
    return activity

def get_webclient(creds):
    """
    Log into the website with WebClient

    :param creds: Les donnees de credentials
    :type creds: dict

    :return: La structure WebClient
    :rtype: :class:`WebClient`
    """

    # Log in (requires API token and email/password for the site)
    print("WebClient tentative connect")
    print(creds["AccesToken"])
    webclient = WebClient(access_token=creds["AccesToken"], email=creds["Email"], password=creds["Password"])
    print ("WebClient : ")
    print (webclient)

    return webclient


def get_activity_data(webclient, activity_id, data_type=DataFormat.ORIGINAL):
    """
    Recuperation du fichier de l'activite voulue en utilisant WebClient

    :param webclient: The Webclient class
    :type webclient: :class:`WebClient`

    :param activity: L'activite voulue.
    :type activity: :class:`stravalib.model.Activity`

    :return: Le `filename` du fichier recupere et cree
    :rtype: str
    """
#    activity_id = activity.id

    # Get the filename and data stream for the activity data
    data = webclient.get_activity_data(activity_id, fmt=data_type)

    # Save the activity data to disk using the server-provided filename
    with open(data.filename, 'wb') as f_buffer:
        for chunk in data.content:
            if not chunk:
                break
            f_buffer.write(chunk)

    return data.filename


def upload_existing_activite(client, activity_file, type_ride):
    """
    Upload d'une activite existante a partir d'un fichier exporte de Strava

    :param client: La structure client
    :type client: :class:`stravalib.client`

    :param activity_file: Le nom du fichier a envoyer a Strava
    :type activity_file: str

    :param type_ride: Type d'activite entre {VirtualRide,Ride}
    :type type_ride: str
    """
    print ("\nUpload d'une activite")

    # On prend le nom du fichier comme nom d'activite
    # On recupere aussi son extension (data_type)
    activite_name, data_type = os.path.splitext(activity_file)
    activite_name = activite_name.replace("_", " ")
    data_type = data_type.replace(".", "")

    print ("activite_name : " + activite_name)
    print ("data_type     : " + data_type)


    with open(activity_file, 'rb') as fp_buffer:
        if type_ride == "VirtualRide" :
            uploader = client.upload_activity(fp_buffer, data_type=data_type, name=activite_name, activity_type="VirtualRide")
        else:
            uploader = client.upload_activity(fp_buffer, data_type=data_type, name=activite_name, activity_type="Ride")
        print (uploader.response)

        activity = uploader.wait()
        print ("Activite upload, voir https://www.strava.com/activities/" + str(activity.id))


        if type_ride == "VirtualRide" :
            # Update de l'activite cree avec le bon velo
            # Recuperation de l'ID du velo nomme HomeTrainer ou HT
            bikes = client.get_athlete().bikes
            for bike in bikes:
                if "HT" in bike.name or "Home Trainer" in bike.name:
                    print ("Update de l'activite avec le velo " + bike.name + " " + str(bike.id))
                    client.update_activity(activity.id, gear_id=bike.id)
                    break


def delete_strava_activity(webclient, activity):
    """
    Suppression de l'activite definit par son id

    :param webclient: The Webclient class
    :type webclient: :class:`WebClient`

    :param activity: L'activite voulue.
    :type activity: :class:`stravalib.model.Activity`
    """
    # Delete the activity
    print ("Suppression de l'activite : " + activity.name + " --- " +  str(activity.id))
    webclient.delete_activity(activity.id)
