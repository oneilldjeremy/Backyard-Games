Backyard Games
--------------

Welcome to Backyard Games!

Backyard Games is a backend API that allows users to browse, discover, and create games that can preferably be played in your backyard. Information about the games include the name, number of players, instructions, a link if the game can be purchased online, as well as whether the game can be played with common supplies, and what those supplies are. Games can also be discovered by searching for the name of specific tags that can be applied to the games. A rating can also be applied to the games to allow users to see the average rating the game has received.

The motivation for this project is to create a clear and concise web location for ideas on games to play. I have not found a single location online with a large catalog of games. It will allow for a frontend to be developed in the future to possibly host a website. 

This project is currently hosted via Heroku at the domain: https://backyardgames.herokuapp.com/. You can interact directly with the website by importing the Postman collection. For certain methods, authorization must be provided. Further instruction is available below.

You may also run this project on your machine locally. To run tests, you must have the API available on your local machine. 

### Installing Dependencies for the Backend

1. **PostgeSQL** PostgreSQL is a free database server that must be installed on your local machine. Download here: (https://www.postgresql.org/download/)

2. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


3. **Virtual Enviornment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


4. **PIP Dependencies** - Once you have your virtual environment setup and running, you must install dependencies by navigating to the root project folder and running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.


5. **Key Dependencies**
 - [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

 - [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

### Database Setup
With Postgres running, you can fill a new database with information by running:
```bash
createdb backyardgames
psql trivia < trivia.psql
```

### Environment Setup
The application also depends on setting certain variables in your environment. On a Linux computer, you can simple run setup.sh to set these values:
```bash
./setup.sh
```

### Running the server

From within the root directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

### Interacting with the API

Once Flask is up and running, you may interact with the application API. The recommended method is importing the Postman collection, but you may also use any HTTP request application.

Download Postman at (https://www.postman.com/downloads/)

Once installed, click Collections on the left tab and click Import. Import the file backyard-games-api.postman_collection.json.

Click the top-level collection backyard-games-api. Click Variables on the ribbon.

The variable 'host' is currently set to http://127.0.0.1:5000/. This will allow you to make requests to your local machine when the Flask application is running.

You may also interact with the live database by inputting https://backyardgames.herokuapp.com/ as the 'host' value.

### Obtaining credentials

Many of the methods listed below require a token by loggin in as a user with the correct role. The current roles available are:

Public (no account necessary)
Registered User
Admin

In order to obtain a token, open a Private Session on your internet browser and access https://backyardgames.herokuapp.com/.

This will forward you to the Auth0 login screen.

For a registered user, enter the following credentials:

Username: registered@backyardgames.com
Password: registered1!#

For an administrator user, enter the following credentials:

Username: admin@backyardgames.com
Password: admin1!#

The webiste will then forward you to the logged-in page. You can get the token from the URL in the browser after the hash mark as the 'access_token' parameter value. Copy and paste the entire text up to '&expires_in=7200&token_type=Bearer'

### Using the token

There are three folders available in the Postman collection for each role. Public does not require a token. To test as a Registered User, click the Registered User folder and make sure your on the Authorization tab. Confirm that the Type is set to Bearer Token. Then enter the Registered User token.

To test as an Admin user, follow the same steps on the Admin folder.

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 401: No or invalid authorization header
- 403: Unauthorized
- 404: Resource Not Found
- 409: Resource already exists
- 422: Unrocessable 

Endpoints
GET '/games'
POST '/games'
PATCH '/games/${id}'
DELETE '/games/${id}'
GET '/games-detailed'
GET '/games/${id}'
GET '/games/search'


GET '/games'
- Permissions: all
- Fetches a list of game names and ids. Each game is formatted as it's own dictionary.
- Request Arguments: None
- Returns: An object with a single key, games, that contains a list of game objects, and a success value:
{
    "games": [
        {
            "id": 1,
            "name": "Corn Hole"
        },
        {
            "id": 2,
            "name": "Polish Horseshoes"
        }
        ...
    ]
    'success': true
}


POST '/games'
- Permissions: Registered User, Admin
- Sends a post request in order to create a new game
- Body must include a name, but all other information is optional. If included, the following variable variables must have the associated data types:

"name": String (required),
"instructions": String,
"diy": Boolean,
"players": Integer,
"tags": List of strings,
"supplies": List of dictionaries:
    "name": String (required),
    "quantity": Integer,
    "estimated_total_cost",: String

- Request Body: 
{
    "diy": false,
    "instructions": "Throw the disc toward the can and jam it in",
    "name": "Kan Jam",
    "players": 4,
    "link": "https://www.amazon.com/dp/B001RJ4Q2G",
    "tags": ["action", "frisbee", "drinking", "tossing"]
    "supplies": [
            {
                "estimated_total_cost": "$0-$100",
                "name": "ski poles",
                "quantity": 2
            }
        ]

}
- Returns: An object with a success value and formatted information about the game
{
    'success': true,
    'games': <See games-detailed for format>
}


PATCH '/games/${id}'
- Permissions: Registered User, Admin
- Sends a patch request in order to update
- Body should only include the values to be updated. If you would like to make the value blank, include the value as a blank string (""):

- Request Body: 
{
    "link": "https://www.amazon.com/dp/B001RJ4Q2G",
}
- Returns: An object with a success value and formatted information about the game
{
    'success': true,
    'games': <See games-detailed for format>
}


DELETE '/games/${id}'
- Permissions: Admin
- Sends a delete request in order to delete a game
- No body required
- Request Arguments: id - integer
- Returns: An object with a success value and the deleted question id
{
    'success': true,
    'deleted': 3
}


GET '/games-detailed'
- Permissions: all
- Fetches a list of detailed, formatted game information. Each game is formatted as it's own dictionary.
- Request Arguments: None
- Returns: An object with a single key, games, that contains a list of game objects, and a success value:
{
    "diy": true,
    "id": 2,
    "instructions": "Stick ski poles upside down into the ground. Put bottles on top. Throw frisbee at bottles.",
    "link": null,
    "name": "Polish Horseshoes",
    "players": 4,
    "rating": 4.73,
    "supplies": [
        {
            "estimated_total_cost": "$0-$100",
            "game_id": 2,
            "id": 4,
            "name": "ski poles",
            "quantity": 2
        }
    ],
    "tags": [
        "frisbee",
        "tossing"
    ]
}


GET '/games/${id}'
- Permissions: all
- Fetches a list of detailed information about a single game.
- Request Arguments: None
- Returns: An object with a single key, games, that contains formatted information about the game, and a success value:
{
    'success': true,
    'games': <See games-detailed for format>
}



GET '/games/search'
- Permissions: all
- Fetches a list of detailed information about games matching the provided search term.
- Request Arguments: None
- Body should include the search term.

- Request body:
{
    "search_term": "toss"
}
- Returns: An object with a single key, games, that contains a list of game objects that matched the search term, and a success value:
{
    'success': true,
    'games': <See games-detailed for format>
}


POST '/games/${id}/rating'
- Permissions: Registered, Admin
- Gives a rating (1-5, integers only) to a game.
- Request Arguments: None
- Body should include rating.

- Request body:
{
    "rating": 4
}
- Returns: An object with a single key, ratings, that contains information about the rating, and a success value:
{
    "success": true,
    "tags": {
        "game_id": 6,
        "id": 66,
        "rating": 4
    }
}


GET '/tags'
- Permissions: Registered, Admin
- Fetches a list of tags and ids. Each game is formatted as its own dictionary.
- Request Arguments: None
- Returns: An object with a single key, tags, that contains a list of tag objects, and a success value:
{
    "tags": [
        {
            "id": 1,
            "tag": "tossing"
        }
    ]
    ...
    'success': true
}


POST '/tags'
- Permissions:  Admin
- Sends a post request in order to create a new tag
- Body must include a tag

- Request Body: 
{
    "tag": "fun"
}
- Returns: An object with a success value and formatted information about the tag
{
    'success': true,
    "tags": {
        "id": 13,
        "tag": "fun"
    }
}


PATCH '/tags/${id}'
- Permissions: Admin
- Sends a patch request in order to update a tag
- Body should only include the tag.

- Request Body: 
{
    "tag": "lots of fun",
}
- Returns: An object with a success value and formatted information about the game
{
    'success': true,
    "tags": {
        "id": 13,
        "tag": "lots of fun"
    }
}


DELETE '/tags/${id}'
- Permissions: Admin
- Sends a delete request in order to delete a tag
- No body required
- Request Arguments: tag - integer
- Returns: An object with a success value and the deleted question id
{
    'success': true,
    'deleted': 3
}


GET '/tags/${id}/games'
- Permissions: Registered, Admin
- Fetches a list of games associated with the tag. Each game is formatted as its own dictionary.
- Request Arguments: tag - integer
- Returns: An object with a key, games, that contains a list of short game objects, a key for the tag, and a success value:
{
    "games": [
        {
            "id": 2,
            "name": "Polish Horseshoes"
        }
        ...
    ],
    "success": true,
    "tag": {
        "id": 1,
        "tag": "tossing"
    }
}

GET '/supplies'
- Permissions: Registered, Admin
- Fetches a list of supplies. Each supply item is formatted as its own dictionary.
- Request Arguments: None
- Returns: An object with a single key, supplies, that contains a list of supplies objects, and a success value:
{
    "success": true,
    "supplies": [
        {
            "estimated_total_cost": "$0-$100",
            "game_id": 2,
            "id": 4,
            "name": "Ski poles",
            "quantity": 2
        }...
    ]
}


PATCH '/supplies/${id}'
- Permissions: Admin
- Sends a patch request in order to update a supply item
- Body should only include the values to be updated. If you would like to make the value blank, include the value as a blank string (""):

- Request Body: 
{
    "name": "ski poles"
}
- Returns: An object with a success value and formatted information about the supply item
{
    "success": true,
    "supplies": {
        "estimated_total_cost": "$0-$100",
        "game_id": 2,
        "id": 4,
        "name": "ski poles",
        "quantity": 2
    }
}


DELETE '/supplies/${id}'
- Permissions: Admin
- Sends a delete request in order to delete a supply item
- No body required
- Request Arguments: tag - integer
- Returns: An object with a success value and the deleted question id
{
    'success': true,
    'deleted': 3
}

## Testing
To run the tests, run
```
dropdb backyardgames_test
createdb backyardgames_test
psql backyardgames_test < backyardgames.psql

Collect the tokens for a Registered User and an Admin as instructed above.
Open test_app.py and enter the tokens on the two commented lines for the variables reg_token and admin_token

python test_app.py
```
