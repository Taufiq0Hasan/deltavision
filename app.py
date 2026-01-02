from flask import Flask, render_template, request
from ultralytics import YOLO
from collections import defaultdict
import os

app = Flask(__name__)

model = YOLO("best.pt")

UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    result_image = None
    stats = {}

    if request.method == "POST":
        file = request.files["image"]
        upload_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(upload_path)

        results = model(upload_path)

        result_path = os.path.join(RESULT_FOLDER, file.filename)
        results[0].save(filename=result_path)
        result_image = result_path

        # Extract detection stats
        class_names = model.names
        detections = results[0].boxes
        raw_stats = defaultdict(list)

        for box in detections:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            raw_stats[class_names[cls]].append(conf)

        # Average confidence per class
        stats = {k: round(sum(v)/len(v)*100, 2) for k, v in raw_stats.items()}

    return render_template("index.html", result_image=result_image, stats=stats)

if __name__ == "__main__":
    app.run(debug=True)
