import os

from sqlalchemy import desc
from flask import Blueprint, render_template, request, jsonify, send_from_directory

from .translations import translate_with_azure
from .models import RoundModel
from .database import db

main = Blueprint("main", __name__, template_folder="templates")


def init_app(app):
    app.register_blueprint(main)


@main.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(main.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


# TODO: Cache-Control headers
@main.route("/")
def homepage():
    return render_template("index.html")


@main.route("/rounds/<round_id>")
def round(round_id):
    return render_template("index.html", id=round_id)


@main.route("/recent")
def recent():
    return render_template("recent.html")


@main.route("/popular")
def popular():
    return render_template("popular.html")


@main.route("/yours")
def yours():
    return render_template("yours.html")


@main.route("/api/rounds/<round_id>/reactions", methods=["POST"])
def round_reaction(round_id):
    round = RoundModel.query.get_or_404(round_id)
    reaction_type = request.json["type"]
    if reaction_type == "funny":
        round.funny_count += 1
    elif reaction_type == "deeep":
        round.deeep_count += 1
    elif reaction_type == "flags":
        round.flags_count += 1
    else:
        return jsonify({"status": "error", "message": "Reaction type unknown"})
    db.session.add(round)
    db.session.commit()
    return jsonify({"status": "success", "round": round.to_dict()})


@main.route("/api/rounds/<round_id>", methods=["GET"])
def api_round(round_id):
    round = RoundModel.query.get_or_404(round_id)
    return jsonify({"status": "success", "round": round.to_dict()})


@main.route("/api/rounds", methods=["GET", "POST"])
def api_rounds():
    if request.method == "POST":
        round = RoundModel()
        round.translations = request.json["translations"]
        round.message = request.json["message"]
        round.language = request.json["language"]
        round.endmessage = request.json["endmessage"]
        round.usergen = request.json["usergen"]
        db.session.add(round)
        db.session.commit()
        return jsonify({"status": "success", "round": round.to_dict()})

    elif request.method == "GET":
        order = request.args.get("order")
        num = int(request.args.get("num"))
        flag_threshold = 2
        if order == "popular":
            rounds = (
                RoundModel.query.filter(RoundModel.usergen == True)  # noqa
                .filter(RoundModel.flags_count < flag_threshold)
                .order_by(desc(RoundModel.deeep_count + RoundModel.funny_count))
                .limit(num)
            )
        else:
            rounds = (
                RoundModel.query.filter(RoundModel.usergen == True)  # noqa
                .filter(RoundModel.flags_count < flag_threshold)
                .order_by(RoundModel.date.desc())
                .limit(num)
            )
        return jsonify({"status": "success", "rounds": [r.to_dict() for r in list(rounds)]})


@main.route("/api/translate", methods=["POST"])
def api_translate():
    text = request.json["text"]
    from_lang = request.json["from"]
    to_lang = request.json["to"]
    translation, error, source = translate_with_azure(text, from_lang, to_lang)
    if error:
        return jsonify({"status": "error", "message": error})
    return jsonify({"status": "success", "text": translation, "source": source})
