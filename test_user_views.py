"""User views tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_list_users(self):
        """Can list users?"""

        resp = self.client.get("/users")
        self.assertEqual(resp.status_code, 200)

        self.assertIn(b"testuser", resp.data)

    def test_users_show(self):
        """Can view user profile?"""

        resp = self.client.get(f"/users/{self.testuser.id}")
        self.assertEqual(resp.status_code, 200)

        self.assertIn(b"testuser", resp.data)

    def test_users_following(self):
        """Can view user following?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = self.client.get(f"/users/{self.testuser.id}/following")
            self.assertEqual(resp.status_code, 200)

            self.assertIn(b"testuser", resp.data)

            u1 = User(username="testuser2",
                    email="test2@test.com",
                    password="testuser2",
                    )

            db.session.add(u1)
            self.testuser.following.append(u1)
            db.session.commit()

            resp = self.client.get(f"/users/{self.testuser.id}/following")
            self.assertEqual(resp.status_code, 200)

            self.assertIn(b"testuser2", resp.data)

    def test_users_followers(self):
        """Can view user followers?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = self.client.get(f"/users/{self.testuser.id}/followers")
            self.assertEqual(resp.status_code, 200)

            self.assertIn(b"testuser", resp.data)

            u1 = User(username="testuser2",
                    email="test2@test.com",
                    password="testuser2",
                    )

            db.session.add(u1)
            self.testuser.followers.append(u1)
            db.session.commit()

            resp = self.client.get(f"/users/{self.testuser.id}/followers")
            self.assertEqual(resp.status_code, 200)

            self.assertIn(b"testuser2", resp.data)
