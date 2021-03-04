from flask import Flask, render_template, request, send_file
import youtube_dl
import os
from datetime import datetime


app = Flask(__name__)

def delete_old_files(path_target, days_elapsed):
    """path_target:삭제할 파일이 있는 디렉토리, days_elapsed:경과일수"""
    for f in os.listdir(path_target): # 디렉토리를 조회한다
        f = os.path.join(path_target, f)
        if os.path.isfile(f): # 파일이면
            timestamp_now = datetime.now().timestamp() # 타임스탬프(단위:초)
            # st_mtime(마지막으로 수정된 시간)기준 X일 경과 여부
            is_old = os.stat(f).st_mtime < timestamp_now - (days_elapsed * 24 * 60 * 60)
            if is_old: # X일 경과했다면
                try:
                    os.remove(f) # 파일을 지운다
                    print(f, 'is deleted') # 삭제완료 로깅
                except OSError: # Device or resource busy (다른 프로세스가 사용 중)등의 이유
                    print(f, 'can not delete') # 삭제불가 로깅


def videodown(video_url):
    output_dir = "video"
    download_path = os.path.join(output_dir, "%(title)s.%(ext)s")

    # youtube_dl options
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]",  # 가장 좋은 화질로 선택(화질을 선택하여 다운로드 가능)
        "outtmpl": download_path,  # 다운로드 경로 설정
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            print([video_url])
    except Exception as e:
        print("Error", e)


@app.route("/")
def home():
    delete_old_files(path_target='video/', days_elapsed=2)
    return render_template("index.html")


@app.route("/download", methods=["GET", "POST"])
def post():
    if not request.form["urlinput"]:
        return render_template("404.html")
    if request.method == "POST":
        url = request.form["urlinput"]
        url = str(url)
        if "www.youtube.com/watch?" in url:
            videodown(url)
        elif "youtu.be/" in url:
            videodown(url)
        else:
            return

    folder_path = "video/"

    # each_file_path_and_gen_time: 각 file의 경로와, 생성 시간을 저장함
    each_file_path_and_gen_time = []
    for each_file_name in os.listdir(folder_path):
        # getctime: 입력받은 경로에 대한 생성 시간을 리턴
        each_file_path = folder_path + each_file_name
        each_file_gen_time = os.path.getctime(each_file_path)
        each_file_path_and_gen_time.append((each_file_path, each_file_gen_time))

    # 가장 생성시각이 큰(가장 최근인) 파일을 리턴
    most_recent_file = max(each_file_path_and_gen_time, key=lambda x: x[1])[0]

    return send_file(
        most_recent_file,
        mimetype="video/mp4",
        attachment_filename=most_recent_file.replace("video/", ""),  # 다운받아지는 파일 이름.
        as_attachment=True,
    )

    # return render_template(
    #     "index.html", url=most_recent_file.replace("video/", "").replace(".mp4", "")
    # )


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html")


if __name__ == "__main__":
    if os.path.isdir("video") == False:
        os.mkdir("video")
    app.run(host='0.0.0.0', threaded=True)
