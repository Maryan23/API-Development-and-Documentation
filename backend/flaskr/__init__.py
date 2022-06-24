from crypt import methods
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        categories_list = [category.type for category in categories]
        if len(categories_list) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': categories_list
        })
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions', methods=['GET'])
    def get_questions():
        categories = Category.query.all()
        categories_list = [category.type for category in categories]
        page = request.args.get('page', 1, type=int)
        questions = Question.query.order_by(Question.id).paginate(page, QUESTIONS_PER_PAGE, False)
        questions_list = [question.format() for question in questions.items]
        if len(questions_list) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': questions_list,
            'total_questions': questions.total,
            'current_category': None,
            'categories': categories_list,
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)
        question.delete()
        return jsonify({
            'success': True,
            'deleted': question_id
        })

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/question', methods=['POST'])
    def create_question():
        body = request.get_json()
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')
        if new_question is None or new_answer is None or new_category is None or new_difficulty is None:
            abort(400)
        question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
        question.insert()
        return jsonify({
            'success': True,
            'created': question.id
        })
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm')
        if search_term is None:
            abort(400)
        questions = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
        questions_list = [question.format() for question in questions]
        if len(questions_list) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': questions_list,
            'total_questions': len(questions_list),
            'current_category': None
        })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        questions = Question.query.filter(Question.category == category_id).all()
        questions_list = [question.format() for question in questions]
        if len(questions_list) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': questions_list,
            'total_questions': len(questions_list),
            'current_category': category_id
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        category = body.get('quiz_category')
        if category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(Question.category == category['id']).all()
        quiz_questions = []
        for question in questions:
            if question.id not in previous_questions:
                quiz_questions.append(question)
        if len(quiz_questions) == 0:
            abort(404)
        random_question = random.choice(quiz_questions)
        return jsonify({
            'success': True,
            'question': random_question.format()
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not found'
        }), 404
    

    return app

