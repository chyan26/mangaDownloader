# @Author: Xiangxin Kong
# @Date: 2020.5.30
import shutil
import requests
import re
import os
import time
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
from decoder import get
from header import header
import threading

class MangaDownloader:
    def __init__(self, address, path):
        self.path = path + "/"
        self.baseURL = "https://www.manhuagui.com"
        url = "https://www.manhuagui.com/comic/" + re.match(r'^.*comic/([0-9]+)/?', address).group(1)
        self.getAbstraction(url)


    def getAbstraction(self, url):
        req = requests.get(url).content
        bf = BeautifulSoup(req, 'html.parser')

        self.title = bf.h1.text
        self.author = bf.find("strong", text="漫画作者：").parent.a.text
        self.plot = bf.find("strong", text="漫画剧情：").parent.a.text
        self.year = bf.find("strong", text="出品年代：").parent.a.text
        self.region = bf.find("strong", text="漫画地区：").parent.a.text
        self.chapters = list(
            map(lambda x: [x.get('title'), x.get('href'), None], bf.find_all('a',{'class':'status0'})))
        self.chapters.reverse()
        self.length = len(self.chapters)

    def existedChapters(self):
        """return a list of Chapters<String> that already existed"""
        localChapters = []
        for chapter in self.chapters:
            if os.path.isdir(self.path + self.title + "/" + chapter[0]):
                localChapters.append(chapter[0])
        return localChapters

    @staticmethod
    def createDirectory(path):
        """create a new file at path"""
        print("create")
        Path(path).mkdir(parents=True, exist_ok=True)

    def isMangaExist(self):
        """return true if the manga already existed"""
        return os.path.isdir(self.path + self.title + "/")
    
    def natural_sort_key(self,s):
        """
        Sorts in a human-friendly way by breaking the filename into numeric and non-numeric parts.
        """
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    def downloadChapter(self, url):
        abstraction = get(self.baseURL + "/" + url)  # Assuming JSON response
        mangaName = abstraction['bname']
        chapterName = abstraction['cname']
        length = abstraction['len']
        e = abstraction['sl']['e']
        m = abstraction['sl']['m']
        path = abstraction['path']

        localPath = self.path + "/" + mangaName + "/" + chapterName + "/"
        self.createDirectory(localPath)
        print(f'Downloading {mangaName} {chapterName}, Total pages: {length}')

        # List to store the paths of all downloaded images
        image_files = []

        # A function to download a single page (to be run in threads)
        def download_page(filename):
            pgUrl = 'https://i.hamreus.com' + path + filename
            print("Downloading image:", os.path.basename(pgUrl))

            # Replace '.webp' with '.jpg' in the filename
            if os.path.basename(pgUrl).endswith(".webp"):
                new_filename = os.path.basename(pgUrl)[:-5]  # Remove '.webp'
            else:
                new_filename = os.path.basename(pgUrl)

            self.downloadPg(pgUrl, e, m, localPath)
            image_files.append(localPath + new_filename)

        # List to hold threads
        threads = []

        # Start a new thread for each file download
        for filename in abstraction['files']:
            t = threading.Thread(target=download_page, args=(filename,))
            threads.append(t)
            t.start()
            time.sleep(0.2)  # Optional: Small delay to avoid overloading

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Sort the image files by their numeric part in the filename
        # Sort files using natural sort
        image_files.sort(key=self.natural_sort_key)
        #image_files.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
        
        
        # After all downloads are complete, generate the PDF
        self.generatePDF(image_files, mangaName, chapterName, localPath)

        # After generating the PDF, delete the directory containing the image files
        if os.path.exists(localPath):
            print(f"Deleting directory: {localPath}")
            shutil.rmtree(localPath)  # This deletes the entire directory and its contents
            print(f"Directory {localPath} deleted successfully")

        return True
    
    def generatePDF(self, image_files, mangaName, chapterName, localPath):
        if len(image_files) == 0:
            print(f"No images found for {chapterName}. Skipping PDF generation.")
            return
        
        # Load images and create PDF
        pdf_file = os.path.join(self.path, mangaName, f"{chapterName}.pdf")
        
        # Open the first image and convert it to RGB
        first_image = Image.open(image_files[0]).convert('RGB')
        
        # Load the remaining images
        image_list = [Image.open(img).convert('RGB') for img in image_files[1:]]

        # Save all images into a PDF
        first_image.save(pdf_file, save_all=True, append_images=image_list)
        print(f"PDF generated for {chapterName}: {pdf_file}")

    def downloadPg(self, url, e, m, localPath):
        # repeat 10 times
        for i in range(10):
            try:
                res = requests.get(url, params={'e': e, 'm': m}, headers=header, timeout=10)
                res.raise_for_status()
            except:
                print('页面 %s 下载失败 重试中...' % url)
                print('等待2秒...')
                # wait for 2s
                time.sleep(2)
                continue
            filename = (localPath + os.path.basename(url))[:-5]
            file = open(filename, 'wb')
            file.write(res.content)
            file.close()
            # transfer to jpg
            Image.open(filename).save(filename, 'jpeg')
            return
        print('超过重复次数 跳过此章')

