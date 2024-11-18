import tkinter as tk
from tkinter import filedialog
from tkinter import *

from torrentClient import TorrentClient



def main():
    def download_selected_file():
        file = filedialog.askopenfile(parent=root,  title='Choose a torrent file (.torrent)', filetypes=[('torrent files', '*.torrent')], mode='rb')
        if file is None:
            print("No file selected")
            return
        torrent_client = TorrentClient(file.name)
        torrent_client.download_torrent_file('output.txt')


    root = tk.Tk()

    root.title("Simple Torrent-like Application")
    root.geometry("400x400")

    selectFileButton = Button(text="Select a torrent file", width=20, height=2, command=download_selected_file)
    selectFileButton.pack(padx=10, pady=10, side=TOP)

    root.mainloop()

if __name__ == "__main__":
    main()