import base64
import tempfile
import json
from subprocess import check_output
from flask import (
    Flask,
    Response,
    request,
)
from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)
app = Flask(__name__)


def extract_ids_and_result(result):
    """Extract ids and result from a result"""
    path1, path2, res = result.split(";")
    id1 = path1.split("/")[-1].split(".")[0]
    id2 = path2.split("/")[-1].split(".")[0]
    return id1, id2, int(res.replace("%", ""))


def extract_result(output_sherlock):
    results = []
    for res in output_sherlock.split("\n")[:-1]:
        id1, id2, res = extract_ids_and_result(res)
        results.append({"id1": id1, "id2": id2, "similarity": res})

    return results


@app.route("/", methods=["POST"])
def main():
    try:
        extension = request.json.get("extension")
        submissions = request.json.get("submissions", [])

        with tempfile.TemporaryDirectory() as submissions_folder:
            for submission in submissions:
                path: str = f"{submissions_folder}/{submission['id']}.{extension}"

                with open(path, "wb") as file:
                    file.write(base64.b64decode(submission["code"]))

            command = ["./sherlock", "-z", "1", "-e", extension, submissions_folder]
            response_sherlock = check_output(command).decode("utf-8")
            response = extract_result(response_sherlock)

        return Response(
            json.dumps({"results": response}),
            status=200,
            mimetype="application/json",
        )
    except Exception as err:
        app.logger.error("Failed to run plagiarism: %s", err)

    return Response(
        status=500,
        mimetype="application/json",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
