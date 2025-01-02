import sys
from myapp import app

if __name__ == "__main__":
    if "--setup" in sys.argv:
        with app.app_context():
            from myapp import db
            db.create_all()
            db.session.commit()
            print("Database tables created")
    else:
        app.run(debug=True)