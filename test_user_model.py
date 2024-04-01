"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        db.session.rollback()

    def test_user_repr(self):
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.assertEqual(u.__repr__(), '<User #None: testuser, test@test.com>')

    def test_user_following(self):

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuse2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        # u1 is not following u2
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u2.is_followed_by(u1))

        #u1 is following u2
        u2.followers.append(u1)
        db.session.commit()

        #u2 is followed by u1
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.is_following(u2))

    def test_user_signup(self):
        user1 = User.signup(
                username="test1",
                password="HASHED_PASSWORD",
                email="test1@test.com",
                image_url="http://test.url"
            )
        u1 = User.query.filter_by(username="test1").first()
        self.assertEqual(u1.id, user1.id)

    def test_user_authenticate(self):
        is_auth = User.authenticate(username='randomUser', password="randomPassword")
        self.assertFalse(is_auth)
