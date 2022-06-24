import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]
        return current_questions

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

    @app.route("/categories",methods=["GET"])
    def get_categories():
        categories = Category.query.all()
        categories_list = [category.type for category in categories]
        if len(categories_list) == 0:
            abort(404)
        return jsonify({
                "success": True,
                "categories": categories_list
            })

    @app.route("/questions" , methods=["GET"])
    def get_questions():
        qns = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()
        questions = paginate_questions(request,qns)
        if len(questions) == 0:
            abort(404)
        return jsonify({
                "success": True,
                "questions": questions,
                "total_questions": len(Question.query.all()),
                "categories":  [category.format() for category in categories],
                "currentCategory": any(category.format() for category in categories)
            })

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            return jsonify(
               {
                "success": True,
                "deleted": question_id,
            })

    @app.route("/postquestions", methods=["POST"])
    def post_question():
        body = request.get_json()
        new_question = body.get("question",None)
        new_answer = body.get("answer",None)
        new_difficulty = body.get("difficulty",None)
        new_category = body.get("category",None)
        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()
            qns = Question.query.order_by(Question.id).all()
            categories = Category.query.order_by(Category.id).all()
            questions = paginate_questions(request,qns)
            return jsonify({
                'success': True,
                'created': True,
                'questions': questions,
                'total_questions': len(Question.query.all()),
                "categories":  [category.format() for category in categories],
                "currentCategory": any(category.format() for category in categories)
                })
        except:
            abort(422)

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        body = request.get_json()
        search_term = body.get("searchTerm")
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

    @app.route("/categories/<string:category_id>/questions")
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

    @app.route("/quizzes", methods=["POST"])
    def get_question():
        body = request.get_json()
        previous_questions = body.get("previous_questions")
        quiz_category = body.get("quiz_category")
        if quiz_category['type'] == 'click':
            questions = Question.query.order_by('id').all()
            category = Category.query.filter_by(id = '1').first()
        else:
            questions = Question.query.filter(Question.category == quiz_category['type']).all()
            category = Category.query.filter_by(id = quiz_category['type']).first()
        if questions == []:
            abort(404)
        try:
            filter_questions = []
            if len(previous_questions) == 0:
                filter_questions = questions
            for p in previous_questions:
                filter_questions = filter(lambda a: a.id != p, questions)
                questions = list(filter_questions)
            selection = [question.format() for question in questions]
            if len(selection) != 0: 
                random_selection = random.randrange(len(selection))
                selection = selection[random_selection]
            else:
                selection = []
            return jsonify({
                "success": True,
                "question": selection,
                "currentCategory": category.type
            })

        except:
            abort(422)

    @app.errorhandler(404)
    def fourOwfour(error):
        return (
            jsonify({"success": False, 
                    "error": 404, 
                    "message": "Requested resource not found"}), 404,)

    @app.errorhandler(422)
    def process_failed(error):
        return (
            jsonify({
                "success": False, 
                "error": 422, 
                "message": "Processing failed"}),422,)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400, 
            "message": "Bad request error"}), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False, 
            "error": 405, 
            "message": "Method not allowed"}),405
        
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False, 
            "error": 500, 
            "message": "Internal server error"}),500

        
    return app