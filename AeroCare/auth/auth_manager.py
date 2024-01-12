import sqlite3
import bcrypt
import logging

class AuthTest:
    def __init__(self, db_path="user.db"):
        """Initializes the AuthTest instance with the specified database path."""
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_users_table()
        self.logger = self._setup_logger()

    def _create_users_table(self):
        """Creates the 'users' table if it does not already exist."""
        with self.conn:
            self.conn.execute(
                """
                 CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY, 
                        password TEXT
                    ) 
                """
            )

    def _setup_logger(self):
        logger = logging.getLogger("AuthTestLogger")
        logger.setLevel(logging.DEBUG)

        # Log to console
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger

    def test_login(self, username, password):
        """Tests login functionality by attempting to log in with a given username and password"""
        with self.conn, self.conn.cursor() as cursor:
            try:
                cursor.execute("SELECT password FROM users WHERE username=?", (username,))
                user_data = cursor.fetchone()
                if user_data is None:
                    self.logger.error("User does not exist: %s", username)
                    raise ValueError("User does not exist")
                else:
                    user_password = user_data[0]
                    if bcrypt.checkpw(password.encode("utf-8"), user_password):
                        return True
                    else:
                        self.logger.error("Incorrect password for user: %s", username)
                        raise ValueError("Incorrect Password")
            except (sqlite3.Error, TypeError) as e:
                self.logger.error("Error retrieving user information: %s", e)
                raise ValueError(f"An error occurred: {e}")

if __name__ == "__main__":
    pass
