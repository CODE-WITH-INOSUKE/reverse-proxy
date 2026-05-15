from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Your target server
TARGET = "http://us-2.galactichosting.net:10185"

# Headers that should not be forwarded
EXCLUDED_HEADERS = {
    "content-encoding",
    "content-length",
    "transfer-encoding",
    "connection",
}


@app.route("/", defaults={"path": ""}, methods=[
    "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"
])
@app.route("/<path:path>", methods=[
    "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"
])
def proxy(path):
    try:
        # Build target URL
        url = f"{TARGET}/{path}"

        # Forward request
        resp = requests.request(
            method=request.method,
            url=url,
            headers={
                key: value
                for key, value in request.headers
                if key.lower() != "host"
            },
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            stream=True,
            params=request.args,
        )

        # Filter response headers
        headers = [
            (name, value)
            for name, value in resp.raw.headers.items()
            if name.lower() not in EXCLUDED_HEADERS
        ]

        return Response(
            resp.content,
            resp.status_code,
            headers,
        )

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
