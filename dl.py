from urllib import request,parse
from datetime import datetime
import json,re
import sys
import time

n_ofSongs = 99999

def sync_db():
    payload = {'skey':'','no_pagination':'1','num_per_page':n_ofSongs}
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    payload = parse.urlencode(payload).encode('utf-8')
    print("最新データベースDLリクエスト送信")
    rq = request.Request("http://uriminzokkiri.com/index.php?ptype=cmusic&mtype=writeList",headers=headers, data=payload)
    res = request.urlopen(rq).read()
    db_json = res.decode('utf-8')
    
    db = json.loads(db_json)
    
    db = {
        "counts_music":db["counts_music"],
        "sync_time":datetime.now().strftime('%Y/%m/%d/ %H:%M:%S'),
        "data": db["lists"]
    }


    #print(db)

    with open('db.json','w') as f_ptr:
        json.dump(db,f_ptr)
    print("データベースダウンロードOK、合計: ",len(db["data"]))

def sync_songs():
    f = open("db.json")
    db = json.load(f)

    print(db["data"])
    print("DBロード、同期しようとしています...")


    f = open("progress.txt", "r")
    startIdx = int(f.read())
    print("前回の同期から復元し、ID:{}から開始します :p".format(startIdx))
    
    for id in (startIdx,len(db["data"])):
        print(id)
        nk_pop = db["data"][id]
        filename = "{}_{}.mp3".format(nk_pop["no"],cleanhtml(nk_pop["title"]))
        # requst to download music from id
        print("ダウンロードリクエスト: 進捗: {} {}/{} {}%".format(filename,id+1,len(db["data"]),(id / len(db["data"] * 100))))
        request.urlretrieve("http://uriminzokkiri.com/index.php?ptype=cmusic&mtype=download&no={}".format(nk_pop["no"]),filename,reporthook)
        print("ダウンロード完了: {}".format(filename))
        writeProgressFile(id+1)

def writeProgressFile(p):
    f = open("progress.txt", "w")
    f.write(str(p))
    f.close()

def reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        if readsofar >= totalsize: # near the end
            sys.stderr.write("\n")
    else: # total size is unknown
        sys.stderr.write("read %d\n" % (readsofar,))

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext
sync_songs()
#sync_db()


