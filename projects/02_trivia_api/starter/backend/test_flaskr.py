import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from backend.flaskr import create_app
from backend.models import setup_db, Question


# NOTE: You must manually set up the database trivia_test and fill it with the
# data from trivia.psql in order for tests to work.
# To do this, just do what you did in the README for the trivia db, but for trivia_test
# i.e. `psql trivia_test < trivia.psql`


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""

    def test_get_categories(self):
        result = self.client().get('/categories')
        result_dict = json.loads(result.data)
        self.assertEqual(result_dict, {
            'categories': {'1': 'Science', '2': 'Art', '3': 'Geography', '4': 'History', '5': 'Entertainment',
                           '6': 'Sports'}, 'success': True})

    def test_get_categories_bad_method(self):
        result = self.client().post('/categories')
        response = json.loads(result.data)
        self.assertEqual(response, {'error': 405, 'message': 'Method not allowed', 'success': False})

    def test_get_questions_good_request_first_page(self):
        result = self.client().get('/questions')
        response = json.loads(result.data)
        self.assertEqual(len(response['questions']), 10)
        self.assertEqual(response['total_questions'], 19)

    def test_get_questions_good_request_second_page(self):
        result = self.client().get('/questions?page=2')
        response = json.loads(result.data)
        self.assertEqual(len(response['questions']), 9)

    def test_get_questions_bad_page(self):
        result = self.client().get('/questions?page=10000')
        response = json.loads(result.data)
        self.assertEqual(response, {'error': 400, 'message': 'Bad request', 'success': False})

    def test_delete_question(self):
        """Delete a question from the database via API, then create an identical question directly with DB."""
        result = self.client().get('/questions')
        response = json.loads(result.data)
        total_questions_initial = response['total_questions']

        question_vals = Question.query.first().format()
        question_id = question_vals['id']
        question_text = question_vals['question']
        answer = question_vals['answer']
        category = question_vals['category']
        difficulty = question_vals['difficulty']
        result = self.client().delete(f'/questions/{question_id}')
        response = json.loads(result.data)
        self.assertEqual(response, {'success': True})
        result = self.client().get('/questions')
        response = json.loads(result.data)
        total_questions_after = response['total_questions']
        self.assertEqual(total_questions_after, total_questions_initial - 1)

        # Now add the same question back, but with a different id
        new_question = Question(question_text, answer, category, difficulty)
        new_question.insert()

    def test_delete_question_bad_id_returns_404(self):
        result = self.client().delete(f'/questions/1000001')
        response = json.loads(result.data)
        self.assertEqual(response, {'error': 404, 'message': 'Not found', 'success': False})

    def test_create_question_successfully_creates_question(self):
        question_text = "This is a dumb fake question"
        question_answer = "This is a dumb fake answer"
        question_category = "1"
        question_difficulty = 1
        data = {
            'question': question_text,
            'answer': question_answer,
            'difficulty': question_difficulty,
            'category': question_category
        }
        result = self.client().post('/questions', json=data)
        response = json.loads(result.data)
        self.assertEqual(response, {'success': True})

        # delete the question we just created to keep database the same
        question_to_delete = Question.query.filter(Question.question == question_text).one_or_none()
        question_to_delete.delete()

    def test_create_question_throws_error_if_fields_missing(self):
        question_text = "This is a dumb fake question"
        question_answer = "This is a dumb fake answer"
        question_category = "1"
        data = {
            'question': question_text,
            'answer': question_answer,
            'category': question_category
        }
        result = self.client().post('/questions', json=data)
        response = json.loads(result.data)
        self.assertEqual(response, {
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        })

    def test_search_for_questions_returns_correct_answers(self):
        data = {
            'searchTerm': 'title'
        }
        result = self.client().post('/questions', json=data)
        response = json.loads(result.data)
        self.assertEqual(response, {
            'questions': [{'answer': 'Maya Angelou', 'category': 4, 'difficulty': 2, 'id': 24,
                           'question': "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"},
                          {'answer': 'Edward Scissorhands', 'category': 5, 'difficulty': 3,
                           'id': 27,
                           'question': 'What was the title of the 1990 fantasy directed by Tim Burton about a '
                                       'young man with multi-bladed appendages?'}],
            'success': True})

    def test_get_questions_by_category_returns_proper_questions(self):
        result = self.client().get('/categories/1/questions')
        response = json.loads(result.data)
        self.assertEqual(response['current_category'], 'Science')
        self.assertEqual(len(response['questions']), 3)

    def test_get_questions_by_category_returns_error_for_bad_category(self):
        result = self.client().get('/categories/100000/questions')
        response = json.loads(result.data)
        self.assertEqual(response, {'error': 404, 'message': 'Not found', 'success': False})

    def test_create_quiz(self):
        data = {
            'previous_questions': [1],
            'quiz_category': {'id': 1}
        }
        result = self.client().post('/quizzes', json=data)
        response = json.loads(result.data)
        self.assertEqual(1, response['question']['category'])
        self.assertTrue(response['question']['id'] not in data['previous_questions'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
