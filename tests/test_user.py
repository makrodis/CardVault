import unittest
from app import create_app, db
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password(self):
        u = User()
        u.create_password('heptane')
        self.assertTrue(u.check_password('heptane'))
        self.assertFalse(u.check_password('heptane2'))

    def test_password2(self):
        u = User()
        u.create_password('heptane')
        self.assertNotEqual(u.password, 'heptane')

    def test_username(self):
        u = User()
        u.username = 'heptane'
        self.assertEqual(u.username, 'heptane')

   