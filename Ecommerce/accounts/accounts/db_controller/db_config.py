import os.path
import os





# Make sure this is the correct absolute path to your 'accountsvol' directory
DATAVOL = r'C:\Users\soni004\Desktop\Thesis\Ecommerce\accounts\accounts'
SQLALCHEMY_DATABASE_URI_SHORT = os.path.join(DATAVOL, 'accounts.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQLALCHEMY_DATABASE_URI_SHORT



# Path to the SQLAlchemy-migrate file
SQLALCHEMY_MIGRATE_REPO = os.path.join(DATAVOL, 'db_repository')
# To turn off the Flask-SQLAlchemy event system and disable the
# annoying warning (likely to be fixed in Flask-SQLAlchemy v3).
SQLALCHEMY_TRACK_MODIFICATIONS = False