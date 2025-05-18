from bilibili_api import video, Credential, HEADERS
import httpx
import os
import sys


SESSDATA = "97d36aea%2C1707810441%2C1bf6a%2A81EUVXFJ7IbJwspvF-QD1GXuho8E7JQX1rUE7e2LF-dq2F10LQMeZjBpZyAMlx24QvJsIdqwAACgA"
BILI_JCT = "c06d22b806d1a52524c90ef6d5a3d56e"
BUVID3 = "2D232235-E682-1AF7-B7B3-0DDD672B937506032infoc"


# FFMPEG 路径，查看：http://ffmpeg.org/
FFMPEG_PATH = "ffmpeg"

async def download_url(url: str, out: str, info: str):
    # 下载函数
    async with httpx.AsyncClient(headers=HEADERS) as sess:
        resp = await sess.get(url)
        length = resp.headers.get('content-length')
        with open(out, 'wb') as f:
            process = 0
            for chunk in resp.iter_bytes(1024):
                if not chunk:
                    break

                process += len(chunk)
                if process == length:
                    print(f'下载完成 {info} {process} / {length}')
                f.write(chunk)

async def main(bvid):
    # 实例化 Credential 类
    credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT, buvid3=BUVID3)
    # 实例化 Video 类
    v = video.Video(bvid=bvid, credential=credential)
    # 获取视频下载链接
    download_url_data = await v.get_download_url(0)
    # 解析视频下载信息
    detecter = video.VideoDownloadURLDataDetecter(data=download_url_data)
    streams = detecter.detect_best_streams()
    # 有 MP4 流 / FLV 流两种可能
    if detecter.check_flv_stream() == True:
        # FLV 流下载
        await download_url(streams[0].url, "audiofile/"+bvid+".flv", "FLV 音视频流")
    else:
        # MP4 流下载
        #await download_url(streams[0].url, bvid+".m4s", "视频流")
        await download_url(streams[1].url, "audiofile/"+bvid+".m4s", "音频流")

    #print('已下载为：video.mp4')

if __name__ == '__main__':
    # 主入口
    asyncio.get_event_loop().run_until_complete(main())
