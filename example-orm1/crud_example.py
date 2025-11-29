import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# Load environment variables from the .env file
load_dotenv()

# Get the database URI from the environment variable
DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

# --- From here, the code is very similar to the previous example ---

# Create an engine that connects to the MySQL database
engine = create_engine(DATABASE_URI, echo=True)

# Create a declarative base for the model
Base = declarative_base()

db = SQLAlchemy()

# Define the User table as a Python class
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False)

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    score_total = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_logged_in = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

# Create the user table.
# Be aware that this will automatically create the table in your 'default' database.
# In a real-world scenario, you would typically use database migrations.
Base.metadata.create_all(engine)

# Create a session to manage the database conversation
Session = sessionmaker(bind=engine)

# --- The CRUD functions remain the same ---

def create_user(session, username, email):
    """Adds a new user to the database."""
    new_user = User(username=username, email=email)
    session.add(new_user)
    session.commit()
    print(f"Created user: {new_user}")

def seed_data(session):
    """Adds initial data if the table is empty."""
    if not session.query(User).first():
        print("Seeding initial user data...")
        create_user(session, "john_doe", "john.doe@example.com")
        create_user(session, "jane_smith", "jane.smith@example.com")
        create_user(session, "peter_jones", "peter.jones@example.com")

def get_all_users(session):
    """Fetches and prints all users from the database."""
    users = session.query(User).all()
    print("\n--- All Users ---")
    if not users:
        print("No users found.")
    for user in users:
        print(user)

def get_user_by_username(session, username):
    """Fetches a single user by their username."""
    user = session.query(User).filter_by(username=username).first()
    print(f"\n--- Find User by Username ('{username}') ---")
    if user:
        print(f"Found user: {user}")
    else:
        print(f"User with username '{username}' not found.")
    return user

def update_user_email(session, username, new_email):
    """Updates the email of a specified user."""
    user = session.query(User).filter_by(username=username).first()
    if user:
        user.email = new_email
        session.commit()
        print(f"\nUpdated user '{username}'. New email: {new_email}")
    else:
        print(f"\nUser with username '{username}' not found. No update performed.")

def delete_user(session, username):
    """Deletes a user from the database by their username."""
    user = session.query(User).filter_by(username=username).first()
    if user:
        session.delete(user)
        session.commit()
        print(f"\nDeleted user: {username}")
    else:
        print(f"\nUser with username '{username}' not found. No deletion performed.")

# --- Main execution block ---

if __name__ == '__main__':
    # Create a session to interact with the database
    session = Session()

    try:
        # Step 1: Seed data (will only run if the table is empty)
        seed_data(session)

        # Step 2: Read all users
        get_all_users(session)

        # Step 3: Update a user
        update_user_email(session, "john_doe", "j.doe@newemail.com")

        # Step 4: Read the updated user
        get_user_by_username(session, "john_doe")

        # Step 5: Delete a user
        delete_user(session, "jane_smith")

        # Step 6: Verify deletion
        get_all_users(session)

    except Exception as e:
        session.rollback()  # Roll back the transaction in case of an error
        print(f"An error occurred: {e}")
    finally:
        session.close()  # Close the session
