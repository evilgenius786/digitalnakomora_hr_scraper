import csv
import json
import os
import threading
import time
import traceback

import requests
from openpyxl import Workbook

# from fake_useragent import UserAgent

# ua = UserAgent()
# print(ua.chrome)
headers = ["idPosrednika", "maticniBroj", "oib", "naziv", "adresaSjedista", "zupanijaSjedista", "adresaPoslovanja",
           "zupanijaPoslovanja", "vrstaPosSubjekta", "registarskiBroj", "datumUpisa", "brojRjesenja", "datumRjesenja",
           "telefon", "mail", "osiguravateljskoDrustvo", "potpisnikKodeksaEtike", "agenti", "privitci", "fax", "web"]
test = False
url = "https://digitalnakomora.hr/posredovanje-ws/api/posrednici"
out = 'out-digitalnakomora.csv'
outxl = 'out-digitalnakomora.xlsx'
error = 'error-digitalnakomora.txt'
s = "scraped-digitalnakomora.txt"
encoding = 'cp1250'
lock = threading.Lock()
threadcount = 10
semaphore = threading.Semaphore(threadcount)


def scrape(i):
    with semaphore:
        print("Working on", i)
        res = ""
        try:
            if test:
                with open('details.json') as dfile:
                    res = json.load(dfile)
            else:
                print(f"{url}/{i}")
                res = requests.get(f"{url}/{i}").text
            detail = json.loads(res)
            detail = detail['data']['posrednik'][0]
            print(json.dumps(detail, indent=4))
            append(detail, i)
        except:
            print("Error", i, res)
            traceback.print_exc()
            with open(error, 'a') as efile:
                efile.write(f"{i}\n")


def append(js, i):
    with lock:
        with open(out, 'a', encoding=encoding, newline='') as outfile:
            csv.DictWriter(outfile, fieldnames=headers).writerow(js)
        with open(s, 'a') as sfile:
            sfile.write(f"{i}\n")


def main():
    logo()
    if not os.path.isfile(out):
        with open(out, 'w', encoding=encoding, newline='') as outfile:
            csv.DictWriter(outfile, fieldnames=headers).writeheader()
    if os.path.isfile(error):
        print("Working on", error)
        threads = []
        with open(error) as efile:
            for line in efile:
                t = threading.Thread(target=scrape, args=(line.strip(),))
                t.start()
                threads.append(t)
                time.sleep(1)
        for thread in threads:
            thread.join()
        print("Done with error file")
    if not os.path.isfile(s):
        with open(s, 'w') as sfile:
            sfile.write("")
    with open(s) as sfile:
        scraped = sfile.read().splitlines()
    print('Loading data...')
    if test:
        with open('posts.json', encoding='utf8') as tfile:
            posts = json.load(tfile)
    else:
        posts = json.loads(requests.get(url).text)
    print("Already scraped data", scraped)
    threads = []
    for post in posts['data']['posrednici']:
        i = post['id']
        if i not in scraped:
            t = threading.Thread(target=scrape, args=(i,))
            t.start()
            threads.append(t)
        # else:
        #     print("Already scraped", i)
        if test:
            break
    for thread in threads:
        thread.join()
    print("Done with scraping.")
    cvrt()
    print("Done with conversion.")
    print("All done!")


def cvrt():
    wb = Workbook()
    ws = wb.active
    with open(out, 'r', encoding=encoding) as f:
        for row in csv.reader(f):
            ws.append(row)
    wb.save(outxl)


def logo():
    os.system('color 0a')
    print(f"""
    ________  .__       .__  __         .__                   ____  __.                                  
    \______ \ |__| ____ |__|/  |______  |  |   ____ _____    |    |/ _|____   _____   ________________   
     |    |  \|  |/ ___\|  \   __\__  \ |  |  /    \\\\__  \   |      < /  _ \ /     \ /  _ \_  __ \__  \  
     |    `   \  / /_/  >  ||  |  / __ \|  |_|   |  \/ __ \_ |    |  (  <_> )  Y Y  (  <_> )  | \// __ \_
    /_______  /__\___  /|__||__| (____  /____/___|  (____  / |____|__ \____/|__|_|  /\____/|__|  (____  /
            \/  /_____/               \/          \/     \/          \/           \/                  \/ 
==============================================================================================================
                        digitalnakomora.hr scraper by: https://github.com/evilgenius786
==============================================================================================================
[+] Multithreaded (Thread count: {threadcount})
[+] Without browser
[+] Super fast
[+] Resumable
[+] Check duplicate
________________________________________________
""")


if __name__ == '__main__':
    main()
    # print(requests.get(f"{url}/{10050}").text)
