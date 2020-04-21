import json
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from backend.models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)  # CORS by default allows '*' for all origins.

    @app.errorhandler(400)
    def bad_request(*args):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(*args):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(*args):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable_entity(*args):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422

    @app.errorhandler(500)
    def internal_server_error(*args):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        try:
            categories = Category.query.order_by(Category.id).all()
            return jsonify({
                'success': True,
                'categories': {category.id: category.type for category in categories}
            })
        except:
            abort(500)

    @app.route('/questions')
    def get_questions():
        try:
            page = request.args.get('page', 1, type=int)
            questions = Question.query.order_by(Question.id).all()
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            questions_list = [question.format() for question in questions][start:end]
            if not questions_list:
                abort(400)
            categories = {category.id: category.type for category in Category.query.order_by(Category.id).all()}
            return jsonify({
                'success': True,
                'questions': questions_list,
                'total_questions': len(questions),
                'categories': categories,
                'current_category': "Science"
                # Since the front end doesn't tell us what category it's on in this request,
            })  # we default to Science.
        except:
            abort(400)

    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()
        if question:
            question.delete()
            return jsonify({
                'success': True
            })
        else:
            abort(404)

    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            data = json.loads(request.data)
            if 'searchTerm' not in data.keys():
                question = data['question']
                answer = data['answer']
                difficulty = data['difficulty']
                category = data['category']
                if not (question and answer and difficulty and category):
                    abort(400)
                new_question = Question(question, answer, category, difficulty)
                new_question.insert()
                return jsonify({
                    'success': True,
                })
            elif 'searchTerm' in data.keys():
                search_term = data['searchTerm']
                questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
                return jsonify({
                    'success': True,
                    'questions': [question.format() for question in questions]
                })
        except:
            abort(422)

    @app.route('/categories/<category_id>/questions')
    def get_questions_by_category(category_id):
        category = Category.query.filter(Category.id == category_id).one_or_none()
        if not category:
            abort(404)

        questions = Question.query.filter(Question.category == category.id).all()
        return jsonify({
            'success': True,
            'total_questions': len(questions),
            'current_category': category.type,
            'questions': [question.format() for question in questions]
        })

    @app.route('/quizzes', methods=['POST'])
    def create_quiz():
        data = json.loads(request.data)
        previous_questions = data['previous_questions']  # will have ids of questions
        quiz_category_id = data['quiz_category']['id']
        questions = Question.query.filter(Question.category == quiz_category_id).all()
        unseen_questions = [question.format() for question in questions if question.id not in previous_questions]
        print('unseen questions are: ', unseen_questions)
        return jsonify({
            'success': True,
            'question': random.choice(unseen_questions) if unseen_questions else False
        })

    return app
