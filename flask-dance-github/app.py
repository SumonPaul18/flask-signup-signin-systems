from flask import Flask, redirect, url_for
from flask_dance.contrib.github import make_github_blueprint, github
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
app.secret_key = "supersekrit"
blueprint = make_github_blueprint(
    client_id="Ov23lipmSx3DA6yvlFMl",
    client_secret="9ea8c766080cede3abff86e1fcfbfad8256914ee",
)
app.register_blueprint(blueprint, url_prefix="/login")

@app.route("/")
def index():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    assert resp.ok
    return "You are @{login} on GitHub".format(login=resp.json()["login"])

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000 )
