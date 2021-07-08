from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    ForeignKey,
    create_engine)
from flask_sqlalchemy import SQLAlchemy
import os

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    '''
    setup_db(app)
        binds a flask application and a SQLAlchemy service
    '''
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


tag_game_xref = db.Table('tag_game_xref',
                         Column('tag_id',
                                Integer,
                                ForeignKey('tags.id'),
                                primary_key=True),
                         Column('game_id',
                                Integer,
                                ForeignKey('games.id'),
                                primary_key=True)
                         )


class Tag(db.Model):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    tag = Column(String, nullable=False, unique=True)
    games = db.relationship('Game',
                            secondary=tag_game_xref,
                            backref='tags', lazy="joined")

    def __init__(self, tag):
        self.tag = tag

    def format(self):
        return {
            'id': self.id,
            'tag': self.tag,
            }


class Supplies(db.Model):
    __tablename__ = 'supplies'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer)
    estimated_total_cost = Column(String)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)

    def __init__(self, name, quantity, estimated_total_cost):
        self.name = name
        self.quantity = quantity
        self.estimated_total_cost = estimated_total_cost

    def __key(self):
        '''Along with __hash__, allows you to do an intersection of two sets
        of supplies. This is based on the idea that two supply items are equal
        if they have the same string for name, quantity, estimated_total_cost'''
        return (self.name, self.quantity, self.estimated_total_cost)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if (self.name == other.name and
           self.quantity == other.quantity and
           self.estimated_total_cost == other.estimated_total_cost):

            return True
        else:
            return False

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'estimated_total_cost': self.estimated_total_cost,
            'game_id': self.game_id
            }


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True)
    rating = Column(Integer, nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)

    def __init__(self, rating, game_id):
        self.rating = rating
        self.game_id = game_id

    def format(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'game_id': self.game_id
            }


class Game(db.Model):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    instructions = Column(String)
    players = Column(Integer)
    diy = Column(Boolean)
    link = Column(String)
    supplies = db.relationship('Supplies',
                               cascade="all,delete",
                               backref='game',
                               lazy="joined")

    def __init__(self, name, instructions='', players='1',
                 diy=False, link=''):
        self.name = name
        self.instructions = instructions
        self.players = players
        self.diy = diy
        self.link = link

    def add_supplies(self, supplies_json):
        new_supplies = []

        for supply_item in supplies_json:
            supplies_object = Supplies(name=supply_item['name'],
                                       quantity=supply_item['quantity'],
                                       estimated_total_cost=supply_item['estimated_total_cost'])

            new_supplies.append(supplies_object)

        '''
        supplies_to_create = list(set(new_supplies).difference(set(original_supplies)))
        supplies_to_delete = list(set(original_supplies).difference(set(new_supplies)))
        already_exists = list(set(original_supplies).intersection(set(new_supplies)))

        print(supplies_to_create)
        print(already_exists)

        supplies_to_create.append(already_exists)


        if return_supplies_tbd_deleted:
            return supplies_to_delete
        else:
        '''

        self.supplies = new_supplies

        return

    def get_supplies(self):
        supplies = self.supplies
        supplies = [s.format() for s in supplies]

        return supplies

    def add_tags(self, tag_string_list):
        tag_string_list = [tag.lower().strip() for tag in tag_string_list]
        tag_object_list = []
 
        for tag in tag_string_list:
            database_tag = Tag.query.filter(Tag.tag == tag).one_or_none()

            if database_tag is None:
                new_tag = Tag(tag=tag)
                tag_object_list.append(new_tag)
            else:
                tag_object_list.append(database_tag)

        self.tags = tag_object_list

        return

    def get_avg_rating(self):
        ratings = Rating.query.filter(Rating.game_id == self.id) \
                           .order_by(Rating.id).all()
        ratings = [r.rating for r in ratings]

        if len(ratings) != 0:
            avg_rating = round(sum(ratings) / len(ratings), 2)
        else:
            avg_rating = ''

        return avg_rating

    def short(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def long(self):

        tags_string = [tag.tag for tag in self.tags]
        supplies_string = [supply_item.format() for supply_item
                           in self.supplies]

        return {
            'id': self.id,
            'name': self.name,
            'instructions': self.instructions,
            'players': self.players,
            'diy': self.diy,
            'tags': tags_string,
            'supplies': supplies_string,
            'rating': self.get_avg_rating()
        }
