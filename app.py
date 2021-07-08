import os
from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS
from sqlalchemy import or_

from models import setup_db, db, Game, Tag, Supplies, Rating
from auth import AuthError, requires_auth


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/games')
    def retrieve_games():
        games = Game.query.order_by(Game.id).all()
        formatted_games = [game.short() for game in games]

        if len(games) == 0:
            abort(404)

        return jsonify({
                       'success': True,
                       'games': formatted_games
                       })

    @app.route('/games-detailed')
    def retrieve_games_detailed():
        games = Game.query.order_by(Game.id).all()
        formatted_games = [game.long() for game in games]

        if len(games) == 0:
            abort(404)

        return jsonify({
                       'success': True,
                       'games': formatted_games
                       })

    @app.route('/games/<int:game_id>')
    def retrieve_game(game_id):
        try:
            game = Game.query.filter(Game.id == game_id).one_or_none()

            if game is None:
                abort(404)
        except():
            abort(422)

        return jsonify({
                       'success': True,
                       'games': game.long()
                       })

    @app.route('/games', methods=['POST'])
    @requires_auth('post:games')
    def create_game(jwt):
        body = request.get_json()

        if body:
            name = body.get('name')
            instructions = body.get('instructions')
            players = body.get('players')
            diy = body.get('diy')
            link = body.get('link')
            supplies = body.get('supplies')
            tag_string_list = body.get('tags')
        else:
            abort(400)

        if not name:
            abort(400)

        if tag_string_list and type(tag_string_list) is not list:
            abort(400)

        if supplies and type(supplies) is not list:
            abort(400)
        elif supplies:
            for supply_item in supplies:
                if type(supply_item) is not dict:
                    abort(400)

        try:
            new_game = Game(name=name,
                            instructions=instructions,
                            players=players, diy=diy,
                            link=link)

            if tag_string_list:
                new_game.add_tags(tag_string_list)

            if supplies:
                new_game.add_supplies(supplies)

            db.session.add(new_game)
            db.session.commit()
            new_game_json = new_game.long()
        except KeyError:
            abort(400)
        except():
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            'success': True,
            'games': new_game_json
        })

    @app.route('/games/<int:game_id>', methods=['PATCH'])
    @requires_auth('patch:games')
    def update_game(jwt, game_id):
        body = request.get_json()

        if body:
            name = body.get('name')
            instructions = body.get('instructions')
            players = body.get('players')
            diy = body.get('diy')
            link = body.get('link')
            supplies = body.get('supplies')
            tag_string_list = body.get('tags')
        else:
            abort(400)

        if tag_string_list and type(tag_string_list) is not list:
            abort(400)

        if supplies and type(supplies) is not list:
            abort(400)
        elif supplies:
            for supply_item in supplies:
                if type(supply_item) is not dict:
                    abort(400)

        try:
            current_game = Game.query.get(game_id)

            if current_game is None:
                abort(404)

            if name:
                current_game.name = name
            if instructions:
                current_game.instructions = instructions
            if players:
                current_game.players = players
            if diy:
                current_game.diy = diy
            if diy:
                current_game.link = link
            if tag_string_list:
                current_game.add_tags(tag_string_list)
            if supplies:
                for supply_item in current_game.supplies:
                    db.session.delete(supply_item)
                current_game.add_supplies(supplies)

            db.session.commit()
            updated_game_json = current_game.long()
        except KeyError:
            abort(400)
        except():
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            'success': True,
            'games': updated_game_json
        })

    @app.route('/games/<int:game_id>', methods=['DELETE'])
    @requires_auth('delete:games')
    def delete_game(jwt, game_id):
        try:
            game = Game.query.filter(Game.id == game_id).one_or_none()

            if game is None:
                abort(404)

            db.session.delete(game)
            db.session.commit()
        except():
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            'success': True,
            'deleted': game_id
            })

    @app.route('/games/<int:game_id>/rating', methods=['POST'])
    @requires_auth('post:rating')
    def create_rating(jwt, game_id):
        body = request.get_json()

        rating = body.get('rating')

        if type(rating) is not int or rating not in range(1, 6):
            abort(400)

        try:
            new_rating = Rating(rating=rating, game_id=game_id)

            db.session.add(new_rating)
            db.session.commit()
            new_rating_json = new_rating.format()
        except KeyError:
            abort(400)
        except():
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            'success': True,
            'tags': new_rating_json
        })

    @app.route('/games/search')
    def games_search():
        body = request.get_json()

        search_term = body.get('search_term')

        if not search_term:
            abort(400)

        tag_results = Tag.query.filter(Tag.tag.ilike('%' + search_term + '%'))

        game_ids_from_tags = []

        for tag in tag_results:
            for game in tag.games:
                if game.id not in game_ids_from_tags:
                    game_ids_from_tags.append(game.id)

        search_results = Game.query.filter(or_(Game.name.ilike('%' + search_term + '%'),
                                               Game.id.in_(game_ids_from_tags)))

        formatted_games = [game.long() for game in search_results]

        return jsonify({
                       'success': True,
                       'games': formatted_games
                       })

    @app.route('/tags')
    @requires_auth('get:tags')
    def retrieve_tags(jwt):
        tags = Tag.query.order_by(Tag.id).all()
        formatted_tags = [tag.format() for tag in tags]

        if len(tags) == 0:
            abort(404)

        return jsonify({
                       'success': True,
                       'tags': formatted_tags
                       })

    @app.route('/tags', methods=['POST'])
    @requires_auth('post:tags')
    def create_tag(jwt):
        body = request.get_json()

        tag = body.get('tag')

        if not tag:
            abort(400)

        tag = tag.lower()

        database_tag = Tag.query.filter(Tag.tag == tag).one_or_none()

        if database_tag:
            abort(409)

        try:
            new_tag = Tag(tag=tag)
            print(new_tag.tag)
            db.session.add(new_tag)
            db.session.commit()
            new_tag_json = new_tag.format()
        except KeyError:
            abort(400)
        except():
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            'success': True,
            'tags': new_tag_json
        })

    @app.route('/tags/<int:tag_id>/games')
    @requires_auth('get:tags')
    def retrieve_games_by_tag(jwt, tag_id):
        tag = Tag.query.filter(Tag.id == tag_id).one_or_none()
        formatted_games = [game.short() for game in tag.games]

        if not tag:
            abort(404)

        return jsonify({
                       'success': True,
                       'tag': tag.format(),
                       'games': formatted_games
                       })

    @app.route('/tags/<int:tag_id>', methods=['DELETE'])
    @requires_auth('delete:tags')
    def delete_tag(jwt, tag_id):
        try:
            tag = Tag.query.filter(Tag.id == tag_id).one_or_none()

            if tag is None:
                abort(404)

            db.session.delete(tag)
            db.session.commit()
        except():
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            'success': True,
            'deleted': tag_id
            })
    
    @app.route('/tags/<int:tag_id>', methods=['PATCH'])
    @requires_auth('patch:tags')
    def update_tag(jwt, tag_id):
        body = request.get_json()

        tag = Tag.query.filter(Tag.id == tag_id).one_or_none()

        new_tag = body.get('tag', None)

        if not tag or not new_tag:
            abort(400)

        try:
            tag.tag = new_tag

            db.session.commit()
        except():
            abort(422)

        return jsonify({
            'success': True,
            'tags': tag.format()
        })

    @app.route('/supplies')
    @requires_auth('get:supplies')
    def retrieve_supplies(jwt):
        supplies = Supplies.query.order_by(Supplies.id).all()
        formatted_supplies = [supply.format() for supply in supplies]

        if len(supplies) == 0:
            abort(404)

        return jsonify({
                       'success': True,
                       'supplies': formatted_supplies
                       })

    @app.route('/supplies/<int:supplies_id>', methods=['DELETE'])
    @requires_auth('delete:supplies')
    def delete_supplies(jwt, supplies_id):
        try:
            supplies = Supplies.query.filter(Supplies.id == supplies_id).one_or_none()

            if supplies is None:
                abort(404)

            db.session.delete(supplies)
            db.session.commit()
        except():
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

        return jsonify({
            'success': True,
            'deleted': supplies_id
            })

    @app.route('/supplies/<int:supplies_id>', methods=['PATCH'])
    @requires_auth('patch:supplies')
    def update_supplies(jwt, supplies_id):
        body = request.get_json()

        name = body.get('name', None)
        quantity = body.get('quantity', None)
        estimated_total_cost = body.get('estimated_total_cost', None)

        supplies = Supplies.query.filter(Supplies.id == supplies_id).one_or_none()

        if not name and not quantity and not estimated_total_cost:
            abort(400)

        try:
            if name:
                supplies.name = name
            if quantity:
                supplies.quantity = quantity
            if estimated_total_cost:
                supplies.estimated_total_cost = estimated_total_cost

            db.session.commit()
        except():
            abort(422)

        return jsonify({
            'success': True,
            'supplies': supplies.format()
        })

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
            }), 400


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
            }), 404

    @app.errorhandler(409)
    def resource_already_exists(error):
        return jsonify({
            "success": False,
            "error": 409,
            "message": "resource already exists"
            }), 409

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422


    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error['description']
            }), error.status_code

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
