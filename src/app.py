import logging

from flask import (Flask,
                   render_template,
                   Response,
                   request)

import os


# 10Mb buffer
BUFF_SIZE=10*(1 << int(os.environ.get("BUFFER_SIZE_MULTIPLIER", 10)))
VIDEO_PATH=os.environ.get("VIDEO_PATH", os.getcwd())
TITLE=os.environ.get("VIDEO_TITLE", os.getcwd())


app = Flask(__name__)

logger = app.logger


def get_path_dict(root, group=None):
  """get a path directory setup for a root path
  """
  logger.info("enumerating: '%s'", root)

  # FIXME: get subdirs?
  # FIXME: filter by file type
  data = {
    "title": TITLE,
    "group": group,
    "files": [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))],
    "paths": {p: [f for f in os.listdir(os.path.join(root, p))]
              for p in os.listdir(root) if os.path.isdir(os.path.join(root, p))}
  }

  logger.info("found %i files", len(data["files"]))
  logger.info("found %i paths", len(data["paths"]))

  return data


@app.route("/")
def index():
  """list video files in the dir
  """
  data = get_path_dict(VIDEO_PATH)

  return render_template("index.html", data=data)


@app.route("/group/<path:group>")
def get_group(group):
  """explore the path at this dir
  """
  data = get_path_dict(os.path.join(VIDEO_PATH, group), group=group)

  return render_template("index.html", data=data)


def get_data(file_path, data_start, data_length=BUFF_SIZE):
  """get some data from disk
  """
  # read some info about the file
  file_length = os.stat(os.path.join(VIDEO_PATH, file_path)).st_size
  file_start = 0

  data_start = min(data_start, file_start+file_length)
  data_length = min(data_length, (file_start+file_length)-data_start)

  with open(os.path.join(VIDEO_PATH, file_path), "rb") as f:
    f.seek(data_start)
    data = f.read(data_length)

  return data, data_start, data_length, file_length


@app.route("/video/<path:filename>")
def get_file(filename):
  """stream the file
  """
  import re

  range_start = 0
  range_length = BUFF_SIZE

  logger.info("accessing '%s'", filename)

  if request.headers.has_key("Range"):
    range_header = request.headers.get("Range", None)

    match = re.search(r'(\d+)-(\d*)', request.headers["Range"])
    groups = match.groups()

    if groups[0]:
      range_start = int(groups[0])
    if groups[1]:
      range_length = int(groups[1])

  data, start, length, file_size = get_data(os.path.join(VIDEO_PATH, filename), range_start, range_length)

  # FIXME: adjust the mimetype for the filetype
  resp = Response(data,
                  206,
                  mimetype="video/mp4",
                  content_type="video/mp4",
                  direct_passthrough=True)

  resp.headers.add("Content-Range",
                   "bytes %i-%i/%i" % (start, start+length-1, file_size))
  resp.headers.add("Accept-Ranges", "bytes")

  return resp


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  app.run()
