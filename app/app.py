import os
from flask import Flask, render_template, request, redirect, url_for
from .models import db, Task


def create_app() -> Flask:
    app = Flask(__name__)

    # Configuração do banco de dados (RDS) via variáveis de ambiente
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")

    if not all([db_user, db_password, db_host, db_name]):
        raise RuntimeError(
            "Variáveis de ambiente do banco não configuradas: DB_USER/DB_PASSWORD/DB_HOST/DB_NAME"
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def index():
        tasks = Task.query.order_by(Task.created_at.desc()).all()
        return render_template("index.html", tasks=tasks)

    @app.post("/add")
    def add_task():
        title = request.form.get("title", "").strip()
        if title:
            t = Task(title=title)
            db.session.add(t)
            db.session.commit()
        return redirect(url_for("index"))

    @app.post("/toggle/<int:task_id>")
    def toggle_task(task_id: int):
        t = Task.query.get_or_404(task_id)
        t.done = not t.done
        db.session.commit()
        return redirect(url_for("index"))

    @app.post("/delete/<int:task_id>")
    def delete_task(task_id: int):
        t = Task.query.get_or_404(task_id)
        db.session.delete(t)
        db.session.commit()
        return redirect(url_for("index"))

    return app


# Instância para uso pelo gunicorn (wsgi:app)
app = create_app()
