from fp import app
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from configs import db_config


#CONNECT to DB
engine = create_engine(db_config.DB_URI)
Base = declarative_base()
Base.metadata.reflect(engine)
db_session = scoped_session(sessionmaker(bind=engine))
@app.teardown_appcontext
def shutdown_session(exception=None):
        db_session.remove()

