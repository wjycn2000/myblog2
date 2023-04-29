
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap5


bootstrap = Bootstrap5()
db = SQLAlchemy()
moment = Moment()
mail = Mail()
ckeditor = CKEditor()
