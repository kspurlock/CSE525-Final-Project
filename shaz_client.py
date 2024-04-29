from tkinter import *
import tkinter as tk
import asyncio
from PIL import ImageTk, Image
from tkinter import Tk, Button
import io
import os
from typing import Iterable
from audio_recorder import record_audio

def call_server():
    asyncio.run(connect())
    
root = Tk()
root.title("ShazamPi")
root.minsize(800, 400)
root.resizable(0,0)
left_frame = Frame(root, width=400, heigh=400)
left_frame.grid(row=0, column=0)
right_frame = Frame(root, width=400, heigh=400)
right_frame.grid(row=0, column=1)

canvas = Canvas(left_frame, width=400, height=400, bg='white')
canvas.pack()
#canv.grid(row=2, column=3)

song_text_var = StringVar()
artist_text_var = StringVar()
album_text_var = StringVar()
release_text_var = StringVar()


song_label = Label(right_frame, textvariable=song_text_var, font="Helvetica 18")
song_label.place(relx=.5, rely=.3, anchor=CENTER)

artist_label = Label(right_frame, textvariable=artist_text_var, text="Artist", font="Helvetica 12")
artist_label.place(relx=.5, rely=.4, anchor=CENTER)

album_label = Label(right_frame, textvariable=album_text_var, font="Helvetica 12")
album_label.place(relx=.5, rely=.5, anchor=CENTER)

release_label = Label(right_frame, textvariable=release_text_var, font="Helvetica 12")
release_label.place(relx=.5, rely=.6, anchor=CENTER)

button = Button(right_frame, text="SHAZAM", font="Helvetica 12 bold", command=call_server)
button.place(relx=0.5, rely=0.8, anchor=CENTER)

right_sub_frame = Frame(right_frame, width=100, height=100)
right_sub_frame.place(relx=0.5, rely=0.7, anchor=CENTER)


slider = Scale(right_sub_frame, from_=1, to=20, orient=HORIZONTAL)
slider.grid(row=0, column=1)

slider_label = Label(right_sub_frame, text="Recording Time:", font="Helvetica 12")
slider_label.grid(row=0, column=0)


displayed_image = ImageTk.PhotoImage(Image.open("resource/start.png")) 
error_image = Image.open("resource/error.png")
image_container = canvas.create_image(0, 0, anchor=NW, image=displayed_image)

def parse_response(response_bytes):
    # Metadata length header is the first 2 bytes
    metadata_size = int.from_bytes(response_bytes[:2], byteorder="big")
    meta_bytes = response_bytes[2:metadata_size+2].decode()
    metadata_list = meta_bytes.split("\n")
    image_bytes = response_bytes[metadata_size+2:]
    
    return image_bytes, metadata_list

def update_labels(metadata_list: Iterable[str]):
    song_text_var.set(metadata_list[0])
    artist_text_var.set(metadata_list[1])
    album_text_var.set(metadata_list[2])
    release_text_var.set(metadata_list[3])
   
def update_canvas(new_image):
    displayed_image = ImageTk.PhotoImage(new_image)
    canvas.itemconfig(image_container, image=displayed_image)
    canvas.imgref = displayed_image
    
async def connect():
    reader, writer = await asyncio.open_connection(
        '192.168.1.10', 8000)
    
    record_path = record_audio(record_seconds=slider.get())
    
    with open(record_path, "rb") as audio_file:
        message = audio_file.read() 
        
    writer.write(message)
    await writer.drain()
    writer.write_eof()
    
    os.remove(record_path)

    response_bytes = await reader.read(-1)
    reader.feed_eof()
    
    metadata_size = int.from_bytes(response_bytes[:2], byteorder="big")
    print(f"Client received {metadata_size} bytes")
    
    if metadata_size > 0:
        image_bytes, metadata_list = parse_response(response_bytes)
        update_labels(metadata_list)
        
        new_image = Image.open(io.BytesIO(image_bytes)) 
        update_canvas(new_image)
        
    else:
        update_canvas(error_image)
        
   
    writer.close()
    await writer.wait_closed()

root.mainloop()
