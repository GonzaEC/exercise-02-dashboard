import os
import requests
from flask import Flask, redirect, render_template_string, request, url_for

API_URL = os.environ.get("API_URL", "http://localhost:8080")

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Node Registry — Nodes</title>
  <style>
    body { font-family: sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 1rem; }
    th, td { border: 1px solid #ccc; padding: 0.5rem 1rem; text-align: left; }
    th { background: #f4f4f4; }
    .health { padding: 0.5rem; border-radius: 4px; margin-bottom: 1rem; }
    .ok { background: #d4edda; color: #155724; }
    .error { background: #f8d7da; color: #721c24; }
    form { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: flex-end; margin-bottom: 1rem; }
    input { padding: 0.4rem; border: 1px solid #ccc; border-radius: 3px; }
    button { padding: 0.4rem 1rem; cursor: pointer; }
    .msg { margin: 0.5rem 0; font-weight: bold; }
  </style>
</head>
<body>
  <h1>Node Registry — Nodes Dashboard</h1>

  <h2>API Health</h2>
  <div class="health {{ 'ok' if health else 'error' }}">
    {% if health %}
      Status: {{ health.status }} | DB: {{ health.db_status }} | Active nodes: {{ health.nodes_count }}
    {% else %}
      Cannot reach API
    {% endif %}
  </div>

  <h2>Registered Nodes</h2>
  {% if nodes %}
  <table>
    <tr><th>Name</th><th>Host</th><th>Port</th><th>Status</th><th>Action</th></tr>
    {% for node in nodes %}
    <tr>
      <td>{{ node.name }}</td>
      <td>{{ node.host }}</td>
      <td>{{ node.port }}</td>
      <td>{{ node.status }}</td>
      <td>
        <form method="post" action="/delete/{{ node.name }}">
          <button type="submit">Delete</button>
        </form>
      </td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <p>No nodes registered yet.</p>
  {% endif %}

  {% if message %}<p class="msg">{{ message }}</p>{% endif %}

  <h2>Register Node</h2>
  <form method="post" action="/register">
    <input name="name" placeholder="Name" required>
    <input name="host" placeholder="Host" required>
    <input name="port" type="number" placeholder="Port" min="1" max="65535" value="8080" required>
    <button type="submit">Register</button>
  </form>
</body>
</html>
"""


def get_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=5)
        return r.json()
    except Exception:
        return None


def get_nodes():
    try:
        r = requests.get(f"{API_URL}/api/nodes", timeout=5)
        return r.json()
    except Exception:
        return []


@app.route("/")
def index():
    message = request.args.get("message")
    return render_template_string(TEMPLATE, health=get_health(), nodes=get_nodes(), message=message)


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    host = request.form.get("host", "").strip()
    port = request.form.get("port", "8080").strip()
    try:
        r = requests.post(
            f"{API_URL}/api/nodes",
            json={"name": name, "host": host, "port": int(port)},
            timeout=5,
        )
        if r.status_code in (200, 201):
            return redirect(url_for("index", message=f"Node '{name}' registered."))
        return redirect(url_for("index", message=f"Error {r.status_code}: {r.text}"))
    except Exception as e:
        return redirect(url_for("index", message=f"Request failed: {e}"))


@app.route("/delete/<name>", methods=["POST"])
def delete(name):
    try:
        r = requests.delete(f"{API_URL}/api/nodes/{name}", timeout=5)
        if r.status_code == 200:
            return redirect(url_for("index", message=f"Node '{name}' deleted."))
        return redirect(url_for("index", message=f"Error {r.status_code}: {r.text}"))
    except Exception as e:
        return redirect(url_for("index", message=f"Request failed: {e}"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501)
