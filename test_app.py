import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Game, Tag, Supplies

#eg_token = <Registered user token here>

#admin_token = <Admin user token here>

reg_header = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + reg_token}

admin_header = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + admin_token}


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.environ['TEST_DATABASE_URL']
        setup_db(self.app, self.database_path)

        self.new_reg_game = {
            "diy": True,
            "instructions": "Drink your beer then flip the cup over.",
            "name": "Flip Cup",
            "players": 20,
            "supplies": [
                {
                    "estimated_total_cost": "$1-$5",
                    "name": "Solo cups",
                    "quantity": 20
                }
            ],
            "tags": [
                "drinking",
                "solo cup"
            ]
        }

        self.new_admin_game = {
            "diy": True,
            "instructions": "Drink your beer then flip the cup over.",
            "name": "Slap Cup",
            "players": 20,
            "supplies": [
                {
                    "estimated_total_cost": "$1-$5",
                    "name": "Solo cups",
                    "quantity": 20
                },
                {
                    "estimated_total_cost": "$1-$5",
                    "name": "Ping pong balls",
                    "quantity": 5
                }
            ],
            "tags": [
                "drinking",
                "solo cup"
            ]
        }



        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_games(self):
        res = self.client().get('/games')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['games'])

    def test_get_single_game(self):
        res = self.client().get('/games/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['games'])

    def test_404_non_existant_game(self):
        res = self.client().get('/game/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_games_detailed(self):
        res = self.client().get('/games-detailed')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['games'])

    def test_search_games(self):
        res = self.client().get('/games/search', json={"search_term": "toss"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['games']))

    def test_search_games_no_results(self):
        res = self.client().get('/games/search', json={"search_term": "jghfuyfgityu67"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['games']), 0)

    def test_create_new_game_no_auth(self):
        res = self.client().post('/games', json=self.new_reg_game)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'No authorization information.')

    def test_create_new_game_reg_auth(self):
        res = self.client().post('/games', json=self.new_reg_game, headers=reg_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['games'])

    def test_create_new_game_admin_auth(self):
        res = self.client().post('/games', json=self.new_admin_game, headers=admin_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['games'])

    def test_edit_game_no_auth(self):
        res = self.client().patch('/games/1', json={"link": "https://www.amazon.com/dp/B007B8ED3Y"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'No authorization information.')

    def test_edit_game_reg_auth(self):
        res = self.client().patch('/games/1', json={"link": "https://www.amazon.com/dp/B007B8ED3Y"}, headers=reg_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['games'])

    def test_edit_game_admin_auth(self):
        res = self.client().patch('/games/5', json={"players": 6}, headers=admin_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['games'])

    def test_delete_game_no_auth(self):
        res = self.client().delete('/games/4')
        data = json.loads(res.data)

        game = Game.query.filter(Game.id == 4).one_or_none()

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'No authorization information.')
        self.assertTrue(game)

    def test_delete_game_not_auth_reg(self):
        res = self.client().delete('/games/4', headers=reg_header)
        data = json.loads(res.data)

        game = Game.query.filter(Game.id == 4).one_or_none()

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found.')
        self.assertTrue(game)

    def test_delete_game_admin_reg(self):
        res = self.client().delete('/games/6', headers=admin_header)
        data = json.loads(res.data)

        game = Game.query.filter(Game.id == 6).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 6)
        self.assertEqual(game, None)

    def test_post_rating_no_auth(self):
        res = self.client().post('/games/1/rating', json={"rating": 5})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'No authorization information.')

    def test_post_rating_reg_auth(self):
        res = self.client().post('/games/1/rating', json={"rating": 5}, headers=reg_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['rating'])

    def test_post_rating_admin_auth(self):
        res = self.client().post('/games/1/rating', json={"rating": 5}, headers=admin_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['rating'])

    def test_get_tags_no_auth(self):
        res = self.client().get('/tags')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'No authorization information.')

    def test_get_tags_reg_auth(self):
        res = self.client().get('/tags', headers=reg_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['tags'])

    def test_get_tags_admin_auth(self):
        res = self.client().get('/tags', headers=admin_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['tags'])

    def test_get_games_from_tag_no_auth(self):
        res = self.client().get('/tags/1/games')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'No authorization information.')

    def test_get_games_from_tag_reg_auth(self):
        res = self.client().get('/tags/1/games', headers=reg_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['games'])

    def test_get_games_from_tag_admin_auth(self):
        res = self.client().get('/tags/1/games', headers=admin_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['games'])

    def test_create_new_tag_no_auth(self):
        res = self.client().post('/tags', json={"tag": "bounce"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'No authorization information.')

    def test_create_new_tag_reg_auth(self):
        res = self.client().post('/tags', json={"tag": "bounce"}, headers=reg_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found.')

    def test_create_new_tag_admin_auth(self):
        res = self.client().post('/tags', json={"tag": "hello"}, headers=admin_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['tags'])

    def test_edit_tag_no_auth(self):
        res = self.client().patch('/tags/1', json={"tag": "bounce"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'No authorization information.')

    def test_edit_tag_reg_auth(self):
        res = self.client().patch('/tags/1', json={"tag": "bounce"}, headers=reg_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found.')

    def test_edit_tag_admin_auth(self):
        res = self.client().patch('/tags/11', json={"tag": "bean bags"}, headers=admin_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['tags'])

    def test_delete_tag_no_auth(self):
        res = self.client().delete('/tags/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'No authorization information.')

    def test_delete_tag_reg_auth(self):
        res = self.client().delete('/tags/1', headers=reg_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found.')

    def test_delete_tag_admin_reg(self):
        res = self.client().delete('/tags/6', headers=admin_header)
        data = json.loads(res.data)

        tag = Tag.query.filter(Tag.id == 6).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 6)
        self.assertEqual(tag, None)

    def test_get_supplies_no_auth(self):
        res = self.client().get('/supplies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'No authorization information.')

    def test_get_supplies_reg_auth(self):
        res = self.client().get('/supplies', headers=reg_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['supplies'])

    def test_get_supplies_admin_auth(self):
        res = self.client().get('/supplies', headers=admin_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['supplies'])

    def test_edit_supplies_no_auth(self):
        res = self.client().patch('/supplies/4', json={"name": "ski poles"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'No authorization information.')

    def test_edit_supplies_reg_auth(self):
        res = self.client().patch('/supplies/4', json={"name": "ski poles"}, headers=reg_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found.')

    def test_edit_supplies_admin_auth(self):
        res = self.client().patch('/supplies/4', json={"name": "ski poles"}, headers=admin_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['supplies'])

    def test_delete_supplies_no_auth(self):
        res = self.client().delete('/supplies/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'No authorization information.')

    def test_delete_supplies_reg_auth(self):
        res = self.client().delete('/supplies/1', headers=reg_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found.')

    def test_delete_supplies_admin_reg(self):
        res = self.client().delete('/supplies/8', headers=admin_header)
        data = json.loads(res.data)

        supplies = Supplies.query.filter(Supplies.id == 8).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 8)
        self.assertEqual(supplies, None)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
