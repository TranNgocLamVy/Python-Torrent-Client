import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
import uuid

from threading import Thread

from torrent_client import TorrentClient

class Application(object):
    def __init__(self, tk, title: str = "Simple Torrent-like Application") -> None:
        self.root = tk
        self.root.title(title)
        self.root.geometry("1000x600")

        self.torrent_list = []

        self.init_gui()

    def init_gui(self):
        self.body = ttk.Frame(self.root)

        seperator = ttk.Separator(self.root, orient="horizontal")

        self.footer = ttk.Frame(self.root, bootstyle="default")

        selectFileButton = ttk.Button(self.footer, text="Select a torrent file", bootstyle=PRIMARY, command=self.selected_file)
        
        self.body.pack(fill="both", expand=True, padx=10, pady=10)
        self.footer.pack(fill="x", side="bottom", anchor="n", padx=4, pady=4)
        seperator.pack(fill="x", side="bottom", anchor="n", padx=4, pady=4)
        selectFileButton.pack(padx=10, pady=10, side=LEFT)


    def run(self):
        self.root.mainloop()

    def refresh(self):
        self.root.update()
        self.root.after(1000,self.refresh)

    def selected_file(self):
        file = filedialog.askopenfile(parent=self.root,  title='Choose a torrent file (.torrent)', filetypes=[('torrent files', '*.torrent')], mode='rb')
        if file is None:
            print("No file selected")
            return

        self.refresh()
        thread = Thread(target=self.add_torrent, args=(file.name,), daemon=True)
        thread.start()
        

    def add_torrent(self, file_name):
        torrent_client = TorrentClient(self.body, file_name, str(uuid.uuid4()))
        self.torrent_list.append(torrent_client)


def main():
    tk = ttk.Window(themename="superhero")
    app = Application(tk)
    app.run()

if __name__ == "__main__":
    main()