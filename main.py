import os,re,threading,requests
import browser_cookie3
from tqdm import tqdm
from lxml import etree
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import time
import configparser

latest_cookie_string = ""
config = configparser.ConfigParser()
config.read('config.ini')
EDGE_DRIVER_PATH = config.get('browser', 'edge_driver_path')
# EDGE_DRIVER_PATH="/Users/xuanlinlv/Documents/edgedriver_mac64_m1/msedgedriver"

def extract_cookie_header():
    cj = browser_cookie3.edge(domain_name='meeting.tencent.com')
    needed_keys = {
        "_ga", "_ga_RPMZTEBERQ", "lz_sign", "lz_appid", "lz_uid", "lz_time", "lz_expire"
    }
    cookies = []
    for c in cj:
        if c.name in needed_keys:
            cookies.append(f"{c.name}={c.value}")
    return '; '.join(cookies)

def get_title_and_mp4_url(url):
    opts = Options()
    opts.add_argument("--window-size=1920,1080")
    service = Service(EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=opts)

    try:
        driver.get("https://meeting.tencent.com")
        time.sleep(2)
        cj = browser_cookie3.edge(domain_name='meeting.tencent.com')
        for c in cj:
            try:
                driver.add_cookie({
                    'name': c.name,
                    'value': c.value
                })
            except Exception as e:
                pass

        driver.get(url)
        time.sleep(10)
        selenium_cookies = driver.get_cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in selenium_cookies])
        global latest_cookie_string
        latest_cookie_string = cookie_str

        tree = etree.HTML(driver.page_source)
        xpath = '/html/body/div[6]/div/div/div[1]/div/div[1]/div/div[1]/div/div/span'
        t = tree.xpath(xpath)
        title = t[0].text.strip() if t and hasattr(t[0], 'text') and t[0].text else "tencent_meeting"

        video_url = None
        for v in driver.find_elements(By.TAG_NAME, "video"):
            src = v.get_attribute("src")
            if src and ".mp4?token=" in src:
                video_url = src
                break
        if not video_url:
            raise ValueError("未找到有效的视频 URL（未包含 .mp4?token）")
        return title, video_url

    except Exception as e:
        raise e
    finally:
        driver.quit()

def download_mp4_multithread(url,filename,headers=None,num_threads=8):
    headers = headers or {}
    headers['Range'] = 'bytes=0-1'
    r = requests.get(url, headers=headers, stream=True)
    cr = r.headers.get('Content-Range')
    if cr and 'bytes' in cr:
        try:
            total_size = int(cr.split('/')[-1])
        except Exception as e:
            raise ValueError("[ERROR] 无法解析 Content-Range 提取文件大小")
    else:
        raise ValueError("[ERROR] 无法从响应中获取视频大小（Content-Range 缺失）")
    part_size=total_size//num_threads
    def dl_range(s,e,i):
        h=headers.copy()
        h['Range']=f"bytes={s}-{e}"
        r=requests.get(url,headers=h,stream=True)
        pbar = tqdm(
            total=e - s + 1,
            unit='B',
            unit_scale=True,
            desc=f"Part {i}",
            position=i,
            leave=False
        )
        with open(f"{filename}.part{i}", "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        pbar.close()
    threads=[]
    for i in range(num_threads):
        s = part_size * i
        e = total_size - 1 if i == num_threads - 1 else s + part_size - 1
        t = threading.Thread(target=dl_range, args=(s, e, i))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    with open(filename, "wb") as out:
        for i in range(num_threads):
            pf = f"{filename}.part{i}"
            with open(pf, "rb") as f:
                out.write(f.read())
            os.remove(pf)
    # 校验合并后文件大小
    merged_size = os.path.getsize(filename)
    if merged_size != total_size:
        raise ValueError(f"[ERROR] 合并后的文件大小不一致，期望 {total_size} 字节，实际 {merged_size} 字节")
    else:
        print(f"[INFO] 合并完成：{filename}（{merged_size} 字节）")

if __name__=="__main__":
    meeting_page_url=input("URL: ")
    title,video_url=get_title_and_mp4_url(meeting_page_url)
    safe_title=re.sub(r'[\\/*?:"<>|]',"_",title)+".mp4"
    base, ext = os.path.splitext(safe_title)
    i = 2
    while os.path.exists(safe_title):
        safe_title = f"{base}-{i}{ext}"
        i += 1
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Accept-Encoding": "identity;q=1, *;q=0",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://meeting.tencent.com/",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "video",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "same-site",
        "priority": "i",
        "range": "bytes=0-1"
    }
    headers['Cookie'] = latest_cookie_string
    download_mp4_multithread(video_url, safe_title, headers=headers)