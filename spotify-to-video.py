from tkinter import *
from tkinter import filedialog
from tkinter.scrolledtext import *

import requests
import base64
from googleapiclient.discovery import build
import pytube
from textblob import TextBlob
from moviepy.editor import VideoFileClip, concatenate_videoclips

import random
import webbrowser

import os
folder = ""
global screen1


def del1():
    errorscreen.destroy()


def del2():
    errorscreen2.destroy()


def del3():
    errorscreen3.destroy()


def del4():
    errorscreen4.destroy()


def del5():
    errorscreen5.destroy()


def del6():
    errorscreen6.destroy()


def del7():
    completed.destroy()
    console1.destroy()


def choosefolder():
    global folder
    folder1 = frame.filename = filedialog.askdirectory(initialdir="/", title="Select a folder")
    Label(frame, text=folder1).grid(row=12, column=0, columnspan=2)
    folder = str(folder1)
    return folder


def callback(url):
    webbrowser.open_new(url)


def Print(text):
    str(text)
    TextBox.insert(END, f"{text}\n")
    TextBox.yview(END)
    TextBox.pack()
    console1.update()
    print(text)


def shuffle():
    if videoMerge.get():
        checkButton3.grid(row=10, pady=(0, 20), column=0, sticky='w', padx=22)
        checkButton2.grid(row=9, pady=(0, 0), column=0, sticky='w', padx=22)
    else:
        checkButton3.grid_forget()
        checkButton2.grid(row=9, pady=(0, 20), column=0, sticky='w', padx=22)


def Info():
    infoScreen = Toplevel(master)
    infoScreen.title("INFO")
    infoScreen.geometry("400x300")
    f = Frame(infoScreen)
    f.grid(row=0, column=0)
    Label(f, text="This app based on your spotify playlist songs\nsearches the youtube for\nthe best sutable video"
                  " resoult with or without lyrics(max 360p).").grid(row=1, column=0)
    Label(f, text="To get client id and client secret go to webside").grid(row=2, column=0)
    spot_link = Label(f, text="https://developer.spotify.com/dashboard", fg="blue", cursor="hand2")
    spot_link.grid(row=3, column=0)
    spot_link.bind("<Button-1>", lambda e: callback("https://developer.spotify.com/dashboard"))
    Label(f, text="\nthere you login to your spotify account and create an app\n"
                  "After creating an app you will see your client id and client secret").grid(row=4, column=0)
    Label(f, text="To get YT API Key simply follow this tutorial:\n").grid(row=5, column=0)
    api_k = Label(f, text="https://www.youtube.com/watch?v=VqML5F8hcRQ", fg="blue", cursor="hand2")
    api_k.grid(row=6, column=0)
    api_k.bind("<Button-1>", lambda e: callback("https://www.youtube.com/watch?v=VqML5F8hcRQ"))
    Label(f, text="I think thats all if you have any problems text me at:\nsylwester.jarosz@spoko.pl").grid(row=7)
    f.pack()


def checkandgo():
    global clientID
    global clientSecret
    global playlistLink
    global apiKey
    global screen1
    global frame
    clientID = clientIDb.get()
    clientSecret = clientSecretb.get()
    playlistLink = playlistLinkb.get()
    apiKey = apiKeyb.get()
    if clientID == "" or clientSecret == "" or playlistLink == "" or apiKey == "":
        global errorscreen
        errorscreen = Toplevel(master, bg="black")
        errorscreen.geometry("200x50")
        errorscreen.title("Error")
        Label(errorscreen, text="You have to fill out all boxes", bg="black",fg="red").pack()
        Button(errorscreen,text="OK",command=del1).pack()
    elif len(clientID) != 32:
        global errorscreen2
        errorscreen2 = Toplevel(master, bg="black")
        errorscreen2.geometry("200x70")
        errorscreen2.title("Error")
        Label(errorscreen2, text="Length of the clientID is incorrect", bg="black",fg="red").pack()
        Label(errorscreen2, text="Correct length is 32", bg="black", fg="red").pack()
        Button(errorscreen2, text="OK", command=del2).pack()
    elif len(clientSecret) != 32:
        global errorscreen3
        errorscreen3 = Toplevel(master, bg="black")
        errorscreen3.geometry("200x70")
        errorscreen3.title("Error")
        Label(errorscreen3, text="Length of the clientSecret is incorrect", bg="black",fg="red").pack()
        Label(errorscreen3, text="Correct length is 32", bg="black", fg="red").pack()
        Button(errorscreen3, text="OK", command=del3).pack()
    elif len(playlistLink) != 82:
        global errorscreen4
        errorscreen4 = Toplevel(master, bg="black")
        errorscreen4.geometry("200x70")
        errorscreen4.title("Error")
        Label(errorscreen4, text="Length of the playlistLink is incorrect", bg="black",fg="red").pack()
        Label(errorscreen4, text="Correct length is 82", bg="black", fg="red").pack()
        Button(errorscreen4, text="OK", command=del4).pack()
    elif len(apiKey) != 39:
        global errorscreen5
        errorscreen5 = Toplevel(master, bg="black")
        errorscreen5.geometry("200x70")
        errorscreen5.title("Error")
        Label(errorscreen5, text="Length of the apiKey is incorrect", bg="black", fg="red").pack()
        Label(errorscreen5, text="Correct length is 39", bg="black", fg="red").pack()
        Button(errorscreen5, text="OK", command=del5).pack()
    elif len(folder) < 1:
        global errorscreen6
        errorscreen6 = Toplevel(master, bg="black")
        errorscreen6.geometry("200x70")
        errorscreen6.title("Error")
        Label(errorscreen6, text="Choose the folder", bg="black", fg="red").pack()
        Label(errorscreen6, text="Please :)", bg="black", fg="red").pack()
        Button(errorscreen6, text="OK", command=del6).pack()
    else:
        global console1
        console1 = Toplevel(master, bg="#313335")
        # console1.geometry("100x500")
        # console1.title("Logs")
        # Label(console1, text="Console", bg="black", fg="red").pack()
        # wrapper1 = LabelFrame(console1)
        # wrapper1.pack(fill="both", expand="yes")
        global TextBox
        console1.wm_title("Console")
        console1.resizable(True, False)
        wrapper1 = LabelFrame(console1, bg='#2B2B2B')
        Label(console1, text="Console", bg='#2B2B2B', fg="white").pack()
        mycanvas = Canvas(wrapper1)
        mycanvas.pack(side=LEFT, expand="yes", fill="both")
        myframe = Frame(mycanvas)
        mycanvas.create_window((0, 0), window=myframe, anchor="nw")
        wrapper1.pack(fill="both", expand="yes", padx=10, pady=10)
        TextBox = ScrolledText(mycanvas, height='10', width='10000', bg='#2B2B2B', fg="#FFFFFF")
        console1.geometry("500x200")
        console1.update()
        go()


def go():
    try:
        Print("Hi")
        Print("Let's start")
        authUrl = "https://accounts.spotify.com/api/token"
        authHeader = {}
        authData = {}

        # clientID = "8b37f8bc8f3147cba5ed5a40619bc637"
        # clientSecret = "6875e6c11bb94512abe75c470a2ba26e"

        def getAccessToken(clientID, clientSecret):
            message = f"{clientID}:{clientSecret}"
            message_bytes = message.encode('ascii')
            base64_bytes = base64.b64encode(message_bytes)
            base64_message = base64_bytes.decode('ascii')

            authHeader['Authorization'] = "Basic " + base64_message
            authData['grant_type'] = "client_credentials"

            ress = requests.post(authUrl, headers=authHeader, data=authData)
            responseObject = ress.json()
            # Print(json.dumps(responseObject, indent=2))

            accessToken = responseObject['access_token']
            return accessToken

        def getplaylisttracks(token, playlistID):
            playlistEndPoint = f"https://api.spotify.com/v1/playlists/{playlistID}"
            getHeader = {
                "Authorization": "Bearer " + token
            }
            res = requests.get(playlistEndPoint, headers=getHeader)
            playlisObject = res.json()

            return playlisObject

        token = getAccessToken(clientID, clientSecret)

        # playlistLink = "https://open.spotify.com/playlist/0zTN7OktVtQS5sVvVIMrFz?si=J8A2kNxPQfy_kMhPmrCnAw"
        playlistID = playlistLink[34:]
        tracklist = getplaylisttracks(token, playlistID)

        # Print(json.dumps(tracklist, indent=2))

        allTracks = 0
        for t in tracklist['tracks']['items']:
            songName = t['track']['name']
            allTracks += 1
            # Print(songName + " lyrics")
        # Print(tracklist['tracks']['items'][1]['track']['name'])
        Print(f"found {allTracks} tracks")

        folderName = str(tracklist['name'])
        folderNameNoSpaces = ""
        for i in folderName:
            if i == " ":
                folderNameNoSpaces += "_"
            else:
                folderNameNoSpaces += i

        ytService = build('youtube', 'v3', developerKey=apiKey)
        # IMPORTANT LOOOOOOOOOOOP
        path = rf"{folder}\{folderNameNoSpaces}"
        os.mkdir(path)
        fileList = []

        for sname in range(0, allTracks):
            title = f"{tracklist['tracks']['items'][sname]['track']['name']}"
            song_lang = ""  # song language

            if TextBlob(title).detect_language() == "pl":
                if radio_lyrics.get():
                    song_lang = " tekst"
                else:
                    song_lang = ""
            else:
                if radio_lyrics.get():
                    song_lang = " lyrics"
                else:
                    song_lang = ""
            request = ytService.search().list(
                part='snippet',
                # channelId='UCvR2R7j218tzejtTsb_X6Rw',
                maxResults=1,
                order='searchSortUnspecified',
                q=f"{tracklist['tracks']['items'][sname]['track']['name']} {tracklist['tracks']['items'][sname]['track']['artists'][0]['name']}{song_lang}"

            )
            Print(f"Executing song nr {sname + 1} title: {tracklist['tracks']['items'][sname]['track']['name']} {song_lang}")
            response = request.execute()



            videoId = response['items'][0]['id']['videoId']
            ytUrl = rf"https://www.youtube.com/watch?v={videoId}"
            Print(f"Yt link: {ytUrl}")
            videoTitle = str(response['items'][0]['snippet']['title'])
            print(videoTitle)
            youtube = pytube.YouTube(ytUrl)
            streams = youtube.streams.filter(progressive=True).order_by('resolution')
            Print(f"Download file {sname + 1} Starting")

            fileName = f"{tracklist['tracks']['items'][sname]['track']['name']} {tracklist['tracks']['items'][sname]['track']['artists'][0]['name']}"
            fileNameSimple = ""
            for c in fileName:
                if c.isalnum():
                    fileNameSimple += c

            for s in reversed(streams):

                # print(s)
                res = int(s.resolution[:-1])
                # print(res)
                if res > 360:
                    continue
                else:

                    s.download(path, filename=fileNameSimple)
                    Print(f"Download file {sname + 1} completed")
                    break
            if videoMerge.get():
                fileList.append(VideoFileClip(rf'{path}/{fileNameSimple}.mp4'))
        if videoMerge.get():
            Print("Merging videos Started")
            if videoShuffle.get():
                random.shuffle(fileList)
            f = concatenate_videoclips(fileList)
            f.write_videofile(rf'{path}/merged_{folderNameNoSpaces}.mp4')
            Print("Merging videos Completed")
        global completed
        completed = Toplevel(master)
        completed.geometry("200x70")
        completed.title("Completed")
        Label(completed, text="Downloading Completed", fg="#5FBF3D").pack()
        Label(completed, text="Thanks for using my program :)", fg="#5FBF3D").pack()
        Button(completed, text="OK", command=del7).pack()
    except:
        Print(f"Unexpected error: {sys.exc_info()[0]}")
        Print("Error may occure  in few ways:\n1)When you ran out of youtube api Quotes"
              "\nYoutube API allows less than 100 song per day\n(Counter resets dayliy on hour 0:00 PT time)\n"
              "I suggest waiting to this point or making new API key\n\n"
              "2)Spotify API may sometimes have some server errors\n"
              "I suggest waiting few minutes and it should work perfectly\n"
              "3)Check if all your informations are put correctly\n"
              "like spotify client or secret and others\n\n"
              "4)Check your internet connection\n\n"
              "IF YOU NEED MY HELP WRITE TO ME AT:\nsylwester.jarosz@spoko.pl")
        raise


master = Tk()
master.title("Spotify to video with lyrics")
master.geometry("400x450")
frame = Frame(master)

Button(frame, text='Info', command=Info)\
    .grid(row=0, column=0, sticky="NW")
#
Label(frame, text='Spotify to lyric video', font=('Arial Bold', 16))\
    .grid(row=0, column=0, columnspan=2, pady=(0, 20))
#
Label(frame, text='SPOTIFY API', font=('Arial Bold', 12))\
    .grid(row=1, column=0, columnspan=2)
#
Label(frame, text='client ID').grid(row=2, column=0, columnspan=2)
clientIDb = StringVar()
Entry(frame, textvariable=clientIDb, width="35").grid(row=3, column=0, columnspan=2)
#
Label(frame, text='client Secret').grid(row=4, column=0, columnspan=2)
clientSecretb = StringVar()
Entry(frame, textvariable=clientSecretb, width="35").grid(row=5, column=0, columnspan=2)
#
Label(frame, text='Playlist Link').grid(row=6, column=0, columnspan=2)
playlistLinkb = StringVar()
Entry(frame, textvariable=playlistLinkb, width="35").grid(row=7, column=0, columnspan=2)
#
radio_lyrics = BooleanVar()
radio_lyrics.set(False)
Checkbutton(frame, text="Video with lyrics", variable=radio_lyrics, offvalue=False, onvalue=True)\
    .grid(row=8, column=0, sticky='w', padx=22)
#
videoMerge = BooleanVar()
videoMerge.set(False)
checkButton2 = Checkbutton(frame, text="Merge to one video", variable=videoMerge, offvalue=False, onvalue=True,
                           command=shuffle)
checkButton2.grid(row=9, pady=(0, 20), column=0, sticky='w', padx=22)
#
videoShuffle = BooleanVar()
videoShuffle.set(False)
checkButton3 = Checkbutton(frame, text="Shuffle songs", variable=videoShuffle, offvalue=False, onvalue=True)
#
Label(frame, text='YOUTUBE API', font=('Arial Bold', 12))\
    .grid(row=11, column=0, columnspan=2)
#
Label(frame, text='YT API Key').grid(row=12, column=0, columnspan=2)
apiKeyb = StringVar()
Entry(frame, textvariable=apiKeyb, width="35").grid(row=13, column=0, columnspan=2)
#
Button(frame, text='Choose folder for videos', command=choosefolder).grid(row=14, column=0, columnspan=2)
#
Button(frame, text="START IT", command=checkandgo, width="37").grid(row=15, column=0, columnspan=2)

frame.pack()
master.mainloop()
