import os
import sqlite3
import bcrypt
from logging_setup import setup_logger

def setup_database(db_path="user.db", logger=None):
    """Set up and connect to the database."""
    if not database_exists(db_path):
        create_database(db_path, logger)
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        logger.error("Error connecting to the database: %s", e)
        raise ValueError(f"Failed to connect to the database: {e}")

def database_exists(db_path):
    """Check if the database file exists."""
    return os.path.exists(db_path)

def create_database(db_path, logger=None):
    """Create the database file."""
    try:
        open(db_path, 'w').close()
        logger.info("Database created successfully.")
    except Exception as e:
        logger.error("Error creating the database: %s", e)
        raise ValueError(f"Failed to create the database: {e}")

logger = setup_logger("AuthTestLogger")

class AuthTest:
    def __init__(self, db_path="user.db"):
        """Initializes the AuthTest instance with the specified database path."""
        self.db_path = db_path
        self.conn = setup_database(self.db_path, logger)
        self._create_users_table()
        self.logger = logger

    def _create_users_table(self):
        """Creates the 'users' table if it does not already exist."""
        try:
            with self.conn:
                self.conn.execute(
                    """
                     CREATE TABLE IF NOT EXISTS users (
                            username TEXT PRIMARY KEY, 
                            password TEXT
                        ) 
                    """
                )
        except sqlite3.Error as e:
            self.logger.error("Error creating 'users' table: %s", e)
            raise ValueError(f"Failed to create 'users' table: {e}")

    def test_login(self, username, password):
        """Tests login functionality by attempting to log in with a given username and password"""
        try:
            with self.conn, self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT password FROM users WHERE username=?", (username,)
                )
                user_data = cursor.fetchone()

                if user_data is not None:
                    user_password = user_data[0]
                    if bcrypt.checkpw(password.encode("utf-8"), user_password):
                        self.logger.info("User logged in successfully: %s", username)
                        return True
                    else:
                        self.logger.warning("Incorrect password for user: %s", username)
                        return False
                else:
                    self.logger.warning("User does not exist: %s", username)
                    return False

        except (sqlite3.Error, TypeError) as e:
            self.logger.error("Error testing login: %s", e)
            raise ValueError(f"An error occurred during login testing: {e}")

class Register:
    def __init__(self, conn, supervisor_approval_required=True):
        self.conn = conn
        self.supervisor_approval_required = supervisor_approval_required
        self.logger = setup_logger(__name__ + ".register")

    def _hash_password(self, password):
        """Generate a hashed password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password

    def add_user(self, username, password):
        """Add a new user to the database with the given username and password."""
        try:
            if self.supervisor_approval_required:
                # Check here if supervisor approval is granted
                approval_granted = self.check_supervisor_approval()
                if not approval_granted:
                    self.logger.warning("Supervisor approval is required.")
                    print("Supervisor approval is required.")
                    return
            with self.conn, self.conn.cursor() as cursor:
                # Check that the username doesn't already exist in the database
                query = "SELECT * FROM users WHERE username=?"
                cursor.execute(query, (username,))
                # If there is no result from the query, then the username isn't taken
                if not cursor.fetchone():
                    # Hash the password before storing it in the database
                    hashed_password = self._hash_password(password)
                    cursor.execute(
                        "INSERT INTO users VALUES (?, ?)",
                        (username, hashed_password),
                    )
                    self.conn.commit()
                    self.logger.info("User added successfully.")
                    print("User added successfully.")
                else:
                    self.logger.warning(
                        "Username '%s' is already in use.", username
                    )
                    print(f"The username '{username}' is already in use.")
        except sqlite3.Error as e:
            self.logger.error("Failed to add user: %s", e)
            print("Failed to add user due to a database error.")

    def check_supervisor_approval(self):
        """Check if supervisor approval is granted."""
        try:
            # Implement the logic for checking supervisor approval here
            # Return True if approval is granted, otherwise return False
            return True  # Example: Approval always granted for now
        except Exception as e:
            self.logger.error("Error checking supervisor approval: %s", e)
            return False

if __name__ == "__main__":
    pass
