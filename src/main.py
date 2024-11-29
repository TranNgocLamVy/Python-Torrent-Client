import tkinter as tk
from tkinter import filedialog
from tkinter import *

from torrent_client import TorrentClient

class Application(tk.Frame):
    def __init__(self, tk, title: str = "Simple Torrent-like Application") -> None:
        self.root = tk
        self.root.title(title)
        self.root.geometry("400x400")

        selectFileButton = Button(text="Select a torrent file", width=20, height=2, command=self.download_selected_file)
        selectFileButton.pack(padx=10, pady=10, side=TOP)

    def refresh(self):
        self.root.update()
        self.root.after(1000,self.refresh)


    def download_selected_file(self):
        file = filedialog.askopenfile(parent=self.root,  title='Choose a torrent file (.torrent)', filetypes=[('torrent files', '*.torrent')], mode='rb')
        if file is None:
            print("No file selected")
            return
        torrent_client = TorrentClient(file.name)
        self.refresh()
        torrent_client.download_torrent_file()


def main():
    tk = Tk()
    app = Application(tk)
    tk.mainloop()

if __name__ == "__main__":
    main()