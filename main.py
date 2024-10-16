# @Author: Xiangxin Kong
# @Date: 2020.5.30
from downloader import *
import tkinter as tk
from tkinter import *


class mainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Manhuagui Downloader')
        self.geometry('400x160')
        baseY = 30

        # Labels for URL and save path
        tk.Label(self, text='Url:', font=('Arial', 16,)).place(x=10, y=baseY)
        tk.Label(self, text='To:', font=('Arial', 16,)).place(x=10, y=baseY + 40)

        # Input fields
        self.var_address = tk.StringVar()
        self.var_url = tk.StringVar()
        self.var_address.set('manga/')
        self.var_url.set('https://www.manhuagui.com/comic/24973/')
        tk.Entry(self, textvariable=self.var_url, font=('Arial', 14), width=28).place(x=60, y=baseY)
        tk.Entry(self, textvariable=self.var_address, font=('Arial', 14), width=28).place(x=60, y=baseY + 40)

        # Download button
        tk.Button(self, text='Download', font=('Arial', 12), command=self.download).place(x=290, y=baseY + 80)
        self.mainloop()

    def download(self):
        try:
            s = MangaDownloader(self.var_url.get(), self.var_address.get())
        except:
            print("Manga not Found")
            self.var_url.set("")
            return
        downloadPanel(s)


class downloadPanel(Toplevel):
    def __init__(self, s):
        super().__init__()
        self.title('Manhuagui Downloader')
        self.geometry('900x600')

        # Display manga info at the top
        self.place_label(s)

        # Create a frame for scrollable buttons area
        self.scrollable_frame = tk.Frame(self)
        self.scrollable_frame.pack(fill="both", expand=True)

        # Create canvas and scrollbar for chapter buttons
        self.canvas = tk.Canvas(self.scrollable_frame)
        self.scrollbar = tk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        # Create a frame inside the canvas for buttons
        self.button_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.button_frame, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Place buttons in the scrollable frame
        self.place_buttons(s)

        # Download and Select All buttons outside scrollable area
        var = IntVar()

        def checkAll():
            for i in self.buttons:
                if var.get() == 1:
                    i.select()
                elif i.cget("state") == 'normal':
                    i.deselect()

        tk.Checkbutton(self, text='Select All', font=('Arial', 18), variable=var,
                       command=checkAll).pack(side="left", padx=10)
        tk.Button(self, text='Download', font=('Arial', 16),
                  command=lambda: self.downloadChapters(s)).pack(side="left", padx=10)

        # Update the scroll region for the canvas
        self.update_scroll_region()

    def update_scroll_region(self):
        # Update the scroll region to include all chapter buttons
        self.button_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def place_label(self, s):
        # Manga info at the top
        tk.Label(self, text=s.title, font=('Arial', 33,)).pack(pady=10)
        info_frame = tk.Frame(self)
        info_frame.pack(pady=10)
        tk.Label(info_frame, text="作者: " + s.author, font=('Arial', 12)).pack(side="left", padx=10)
        tk.Label(info_frame, text="年代: " + s.year, font=('Arial', 12)).pack(side="left", padx=10)
        tk.Label(info_frame, text="地区: " + s.region, font=('Arial', 12)).pack(side="left", padx=10)
        tk.Label(info_frame, text="类型: " + s.plot, font=('Arial', 12)).pack(side="left", padx=10)

    def place_buttons(self, s):
        self.buttons = []
        for i in range(len(s.chapters)):
            s.chapters[i][2] = IntVar()
            cha = tk.Checkbutton(self.button_frame, text=s.chapters[i][0], font=('Arial', 14), variable=s.chapters[i][2])
            cha.grid(row=i // 6, column=i % 6, padx=5, pady=5)  # Use grid instead of place
            if s.chapters[i][0] in s.existedChapters():
                cha.select()
                cha.config(state='disabled')
            self.buttons.append(cha)

    def downloadChapters(self, s):
        for i in range(len(s.chapters)):
            if self.buttons[i].cget("state") == 'normal' and s.chapters[i][2].get():
                s.downloadChapter(s.chapters[i][1])


if __name__ == '__main__':
    mainWindow()
