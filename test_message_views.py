"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


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


class MessageViewTestCase(TestCase):
    """Test views for messages."""

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

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_view_message(self):
        """Can view a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            message = Message(text="Hello", user_id=self.testuser.id)
            db.session.add(message)
            db.session.commit()
            # Now, that session setting is saved, so we can have
            # the rest of ours test
            message = Message.query.one()
            resp = c.get(f"/messages/{message.id}")
            self.assertEqual(resp.status_code, 200)

            self.assertIn(b"Hello", resp.data)

    def test_delete_message(self):
        """Can delete a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            message = Message(text="Hello", user_id=self.testuser.id)
            db.session.add(message)
            db.session.commit()
            # Now, that session setting is saved, so we can have
            # the rest of ours test
            self.assertEqual(len(self.testuser.messages), 1)
            message = Message.query.one()
            resp = c.post(f"/messages/{message.id}/delete")
            self.assertEqual(resp.status_code, 302)

            self.assertEqual(len(self.testuser.messages), 0)

    def test_like_message(self):
        """Can like a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            u = User(
                username="testuser2",
                email="test2@test.com",
                password="testuser2",
            )
            db.session.add(u)
            db.session.commit()
            message = Message(text="Hello", user_id=u.id)
            db.session.add(message)
            db.session.commit()
            # Now, that session setting is saved, so we can have
            # the rest of ours test
            self.assertEqual(len(self.testuser.likes), 0)

            #add like
            resp = c.post(f"/users/add_like/{message.id}")
            self.assertEqual(resp.status_code, 302)

            self.assertEqual(len(self.testuser.likes), 1)

            # remove like
            resp = c.post(f"/users/add_like/{message.id}")
            self.assertEqual(resp.status_code, 302)

            self.assertEqual(len(self.testuser.likes), 0)
