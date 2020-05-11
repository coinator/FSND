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

### VIM TESTS

## Endpoints
```
GET '/categories'
GET '/categories/category_id/questions'
GET '/questions'
POST '/questions'
DELETE '/questions/question_id'
POST '/quizzes'
```

### GET categories
```
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

### GET questions by category
```
GET '/categories/<category_id>/questions'
- Returns questions with category equal to category_id, paginated in pages of 10
- Args: page (default: 1)

Responds:
{
    'success': True,
    'totalQuestions': question_count,
    'currentCategory': category_id,
    'questions': {questions}
}

- Questions have the following form:

{
    'id': id,
    'question': question,
    'answer': answer,
    'category': category,
    'difficulty': difficulty
}
```

### GET questions
```
GET '/questions'
- Returns all the questions paginated, in pages of 10
- Args: page (default: 1)
{
    'success': True,
    'questions': {questions},
    'totalQuestions': question_count,
    'categories': {categories},
    'currentCategory': "Science"
}

- Questions have the following form:
{
    'id': id,
    'question': question,
    'answer': answer,
    'category': category,
    'difficulty': difficulty
}
```

### POST question
```
POST '/questions'
- Creates a question in DB
- Args: JSON payload with the following compulsory args.
* question
* answer
* category
* difficulty

Returns {'success': True} on success.
```

### DELETE question
```
DELETE '/questions/<question_id>'
- Deletes the question with the given question_id

Returns {'success': True} on success.
```

### POST quiz
```
POST '/quizzes'
- Creates a quiz, given previous questions, so that they won't be displayed again.
- Args: JSON paylod with the following compulsory args.
{
    'previous_questions': {previous_question_ids}
    'quiz_category': {'id': category id for the quiz}
}

- A category id of 0, will create a quiz with questions from all available categories

On success, it returns
{
    'success': True,
    'question': A random question in the quiz category provided.
}
```
