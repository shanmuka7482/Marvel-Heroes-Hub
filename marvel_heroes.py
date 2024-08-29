import tkinter as tk
from tkinter import ttk,messagebox
from PIL import ImageTk, Image
import os
from dotenv import load_dotenv
import requests
import json
import ssl
from urllib3 import poolmanager
from io import BytesIO
import pyglet 
import sys

# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

width_app = 500 # Width 
height_app = 600 # Height

# Custom Colors
bg_color = "#1c2c39" 
text_color = "#fb8e75"
light_color = "#f4f4f4"
dark_text = "#284057"

# Load Custom Fonts
pyglet.font.add_file(resource_path("fonts\\Bangers-Regular.ttf"))
pyglet.font.add_file(resource_path("fonts\\Roboto-Light.ttf"))


class TLSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_version=ssl.PROTOCOL_TLS,
                ssl_context=ctx)

# Clear Widgets from a frame
def clear_widgets(frame):
    for widget in frame.winfo_children():
        widget.destroy()

# get names,id
def fetch_names():
    load_dotenv()
    data=[]
    ts=1
    PublicKey=os.getenv('PublicKey')
    Hash=os.getenv('Hash')
    api=f"https://gateway.marvel.com:443/v1/public/characters?limit=10&ts={ts}&apikey={PublicKey}&hash={Hash}"
    try:
        session = requests.session()
        session.mount('https://', TLSAdapter())
        res = session.get(api)
        # names
        for i in res.json()["data"]["results"]:
            name=i["name"]
            id=i["id"]
            data.append([name,id])

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return data

# get image location,description
def fetch_description(id):
    load_dotenv()
    images=[]
    ts=1
    PublicKey=os.getenv('PublicKey')
    Hash=os.getenv('Hash')
    api=f"https://gateway.marvel.com:443/v1/public/characters/{id}?limit=10&ts={ts}&apikey={PublicKey}&hash={Hash}"
    try:
        session = requests.session()
        session.mount('https://', TLSAdapter())
        res = session.get(api)
        # images
        for i in res.json()["data"]["results"]:
            image = i["thumbnail"]["path"]+"/portrait_incredible."+i["thumbnail"]["extension"]
            description = i["description"]
            name=i["name"]
            images.append([image,description,name])

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return images

def display_selection():
    selection = combo.get()
    index = combo.current()
    returns = messagebox.showinfo(
        message=f"The selected values is {selection}"
        )
    if returns == "ok":
        loadframe3(index)

def loadframe1():
    clear_widgets(frame2)
    frame1.tkraise()
    frame1.pack_propagate(False)

    # frame1 widgets
    # Logo
    global logo_Image
    img = Image.open(resource_path("assets\\logo-2.png"))
    img = img.resize((180,110))
    logo_Image = ImageTk.PhotoImage(img)
    logo_Widget = tk.Label(frame1, image = logo_Image, bg = bg_color, pady = 10)
    logo_Widget.pack(pady=30)

    # Label
    tk.Label(frame1, text="Ready for Marvel Universe ?", bg = bg_color, fg = text_color, font = ("Bangers", 24)).pack(pady=40)

    # Button Widget
    tk.Button(frame1, 
            text = "Lets Go!!!", 
            bg = "#fb8e75", 
            font = ("Roboto", 15), 
            fg = "#ffffff", 
            cursor = "hand2", 
            activebackground = "#e07a65",
            activeforeground= "#ffffff", 
            command = loadframe2,
            highlightthickness = 0,
            bd = 0
            ).pack()

def loadframe2():
    clear_widgets(frame1)
    clear_widgets(frame3)
    frame2.tkraise()
    frame2.pack_propagate(False)

    # frame2 widgets
    # Logo
    global logo_Image
    img = Image.open(resource_path("assets\\logo-2.png"))
    img = img.resize((180,110))
    logo_Image = ImageTk.PhotoImage(img)
    logo_Widget = tk.Label(frame2, image = logo_Image, bg = bg_color)
    logo_Widget.grid(row=0, column=0, columnspan=2, pady=30)

    # Label
    tk.Label(frame2, text="Marvel Characters", bg = bg_color, fg = text_color, font = ("Bangers", 20)).grid(row=1, column=0, columnspan=2, pady=20)

    # converting 2d into 1d
    names = [item[0] for item in data] 

    # Drop-down 
    global combo
    combo = ttk.Combobox(frame2,state="readonly",
                         values=names)
    combo.grid(row=2, column=0, columnspan=2, pady=10)

    # button
    tk.Button(frame2, 
        text = "Search", 
        bg = "#fb8e75", 
        font = ("Roboto", 15), 
        fg = "#ffffff", 
        cursor = "hand2", 
        activebackground = "#e07a65",
        activeforeground= "#ffffff", 
        command = display_selection,
        highlightthickness = 0,
        bd = 0
            ).grid(row=3, column=0, pady=20)
    
    # Back Button
    tk.Button(frame2, 
            text = "Back", 
            bg = "#fb8e75", 
            font = ("Roboto", 15), 
            fg = "#ffffff", 
            cursor = "hand2", 
            activebackground = "#e07a65",
            activeforeground= "#ffffff", 
            command = loadframe1,
            highlightthickness = 0,
            bd = 0
            ).grid(row=3, column=1, pady=20)

def loadframe3(index):
    clear_widgets(frame2)
    frame3.tkraise()
    frame3.pack_propagate(False)

    id = data[index][1]
    images=fetch_description(id)
    print(images)
    image_url = images[0][0]
    description = images[0][1]
    name = images[0][2]

    # Null Description
    if(description == ""):
        description = "No Description"

    # frame3 widgets
    # Image

    # Fetch and display image
    try:
        response = requests.get(image_url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = img.resize((200, 300))  # Resize as needed
        img = ImageTk.PhotoImage(img)
        
        # Display the image
        tk.Label(frame3, image=img, bg=bg_color).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Keep a reference to the image
        global img_ref
        img_ref = img

    except Exception as e:
        print(f"An error occurred while fetching or displaying the image: {e}")

    # Label
    tk.Label(frame3, text=name, bg = bg_color, fg = text_color, font = ("Bangers", 24)).grid(row=1, column=0, columnspan=2, pady=20)

    # Description
    tk.Label(frame3, text=description, bg = light_color, fg = dark_text, font = ("Roboto", 14), wraplength=width_app-40).grid(row=2, column=0, columnspan=2, pady=20,padx=10)

    # Back Button
    tk.Button(frame3, 
            text = "Back", 
            bg = "#fb8e75", 
            font = ("Roboto", 15), 
            fg = "#ffffff", 
            cursor = "hand2", 
            activebackground = "#e07a65",
            activeforeground= "#ffffff", 
            command = loadframe2,
            highlightthickness = 0,
            bd = 0
            ).grid(row=3, column=0, pady=10, sticky="s", columnspan=2)    


# initialize app
root = tk.Tk()
root.title("Marvel Heroes Hub")

root.eval("tk::PlaceWindow . center")

# screen_width = root.winfo_screenwidth()  # Width of the screen
# screen_height = root.winfo_screenheight() # Height of the screen
 
# # Calculate Starting X and Y coordinates for Window
# x = (screen_width/2) - (width_app/2)
# y = (screen_height/2) - (height_app/2)

# root.geometry('%dx%d+%d+%d' % (width_app, height_app, x, y))

# create Frame widget
frame1 = tk.Frame(root, width=width_app, height=height_app, bg=bg_color)
frame2 = tk.Frame(root, width=width_app, height=height_app, bg=bg_color)
frame3 = tk.Frame(root, bg=bg_color)

frame1.grid(row = 0, column = 0, sticky="nesw")
frame2.grid(row = 0, column = 0, sticky="n")
frame3.grid(row = 0, column = 0, sticky="n")

data=fetch_names()

loadframe1()


# run app
root.mainloop()