from flask import Flask, request, jsonify
import logging
import time
import json
from pathlib import Path
from datetime import datetime
import collections

logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)
RECORDS_OUTPUT = Path('./records')


def format_delta(delta: float):
    delta = int(delta)
    hours, remainder = divmod(delta, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class Recording:
    def __init__(self):
        self.current_rec_file = Path()
        self.metadata = collections.defaultdict(dict)
        self.current_question = 0
        self.timestamp = time.time()

    def end_recorindg(self):
        self.current_question = 0
        self.metadata = collections.defaultdict(dict)
        self.timestamp = 0


rec = Recording()
app = Flask(__name__)


@app.route('/recording', methods=['POST', 'DELETE'])
def recording():
    if request.method == 'POST':
        rec.current_rec_file = Path(RECORDS_OUTPUT,
                                    f"{request.json['name']}_{datetime.now().strftime('%d-%m_%H-%M')}")  # noqa
        rec.current_rec_file.mkdir()
        # START RECORDING HERE
        rec.timestamp = time.time()
        logger.info("Recording started")
        return jsonify({'status': 'ok'}), 200
    if request.method == 'DELETE':
        # TODO Logic for stop recording
        with open(rec.current_rec_file / 'metadata.json', 'w') as f:
            json.dump(rec.metadata, f)
        # END RECORDING HERE
        rec.end_recorindg()
        logger.info("Recording stopped")
        return jsonify({'status': 'ok'}), 204


@app.route('/recording/question', methods=['POST'])
def question():
    t = format_delta(time.time() - rec.timestamp)
    if request.json['action'] == 'start':
        rec.current_question += 1
        rec.metadata[rec.current_question]['start'] = t
    elif request.json['action'] == 'end':
        rec.metadata[rec.current_question]['end'] = t
    else:
        return jsonify({'status': 'error'}), 400
    return jsonify({'time_delta': t}), 201


if __name__ == '__main__':
    if not RECORDS_OUTPUT.exists():
        RECORDS_OUTPUT.mkdir()
    app.run()
