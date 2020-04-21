# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run
```

`FLASK_APP` and `FLASK_ENV` are already set for you in the root level `.flaskenv` file. Flask finds this file and 
exports these environment variables when you run `flask run`. 

## API
### Getting all categories
```
GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
{'1' : "Science",
'2' : "Art",
'3' : "Geography",
'4' : "History",
'5' : "Entertainment",
'6' : "Sports"}
```
### Getting all questions
```
GET '/questions'
- Returns all questions in the database
Returns a JSON response of the following python dictionary:  
{
    'success': True,
    'questions': [list of questions],
    'total_questions': len(questions),
    'categories': categories,
    'current_category': "Science"
}

Each question in the questions list has the following form:
{
    'id': id,
    'question': question,
    'answer': answer,
    'category': category,
    'difficulty': difficulty
}
```

### Deleting a question
```
DELETE '/questions/<question_id>'
- Deletes the question with the given question_id

Returns {'success': True} on success.
```

### Creating a new question
```
POST '/questions'
This method expects a JSON payload with the following fields:
* question
* answer
* category
* difficulty

Returns {'success': True} on success.
```

### Getting questions by category
```
GET '/categories/<category_id>/questions'

- Similar to getting all questions, but only returns questions with the given ID.
Responds:
{
    'success': True,
    'total_questions': len(questions),
    'current_category': category id,
    'questions': [questions list]
}

Each question in the questions list has the following form:
{
    'id': id,
    'question': question,
    'answer': answer,
    'category': category,
    'difficulty': difficulty
}
```

### Creating a quiz
```
POST '/quizzes'

This post request expects a JSON body like the following:
{
    'previous_questions': [a list of previous question id's],
    'quiz_category': {'id': category id for the quiz}
}

On success, this will return
{
    'success': True,
    'question': A random, unseen question in the quiz category provided.
}
```

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```