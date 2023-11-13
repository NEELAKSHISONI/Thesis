import os
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define your Firebird database URI
db_url = 'firebird+fdb://localhost/C:/Temp/TEST.GDB'

# Create a SQLAlchemy engine
engine = create_engine(db_url)

# Define the data model using SQLAlchemy's declarative_base
Base = declarative_base()

class YourTable(Base):
    __tablename__ = 'your_table'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    # Add more columns as needed

# Create tables in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Perform database operations using the session
# Example: Insert a new row
new_row = YourTable(name='Example')
session.add(new_row)
session.commit()

# Query the database
results = session.query(YourTable).all()
for result in results:
    print(result.id, result.name)

# Close the session
session.close()
