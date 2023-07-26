import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import collections

collections.Iterable = collections.abc.Iterable
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
    app = Flask(__name__, instance_relative_config=True)
    app.app_context().push()
    setup_db(app)

    # Set up CORS
    CORS(app)

    # Set Access-Control-Allow headers after each request
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response

    # Endpoint to get all available categories
    @app.route("/categories", methods=["GET"])
    def get_categories():
        try:
            categories = Category.query.order_by(Category.type).all()
            if not categories:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "categories": {cat.id: cat.type for cat in categories},
                }
            )

        except Exception as e:
            print(e)
            abort(404)

    # Create an endpoint to handle GET requests for questions, including pagination (every 10 questions).This endpoint should return a list of questions, number of total questions, current category, categories.
    @app.route("/questions", methods=["GET"])
    def get_questions():
        try:
            # get all questions
            selection = Question.query.order_by(Question.id).all()
            # get the total num of questions
            totalQuestions = len(selection)
            # get current questions in a page (10q)
            currentQuestions = paginate_questions(request, selection)

            # if the page number is not found
            if len(currentQuestions) == 0:
                abort(404)

            # get all categories
            categories = Category.query.all()
            categoriesDict = {}
            for category in categories:
                categoriesDict[category.id] = category.type

            return jsonify(
                {
                    "success": True,
                    "questions": currentQuestions,
                    "total_questions": totalQuestions,
                    "categories": categoriesDict,
                }
            )
        except Exception as e:
            print(e)
            abort(400)

    # Endpoint to delete a question by ID
    @app.route("/questions/<int:id>", methods=["DELETE"])
    def delete_question(id):
        try:
            question = Question.query.filter(Question.id == id).one_or_none()
            if not question:
                abort(404)

            question.delete()
            return jsonify({"success": True, "deleted": id})

        except Exception as e:
            print(e)
            abort(404)

    # Endpoint to add a new question
    @app.route("/add_questions", methods=["POST"])
    def add_question():
        try:
            data = request.get_json()
            new_question = data.get("question")
            new_answer = data.get("answer")
            new_difficulty = data.get("difficulty")
            new_category = data.get("category")

            if not all([new_question, new_answer, new_difficulty, new_category]):
                abort(422)

            question = Question(
                question=new_question,
                answer=new_answer,
                difficulty=new_difficulty,
                category=new_category,
            )
            question.insert()

            return jsonify({"success": True, "created": question.id})

        except Exception as e:
            print(e)
            abort(422)

    # Endpoint to search questions based on a search term
    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        body = request.get_json()
        search_term = body.get("searchTerm", None)

        if search_term:
            search_results = Question.query.filter(
                Question.question.ilike(f"%{search_term}%")
            ).all()

            return jsonify(
                {
                    "success": True,
                    "questions": [question.format() for question in search_results],
                    "total_questions": len(search_results),
                    "current_category": None,
                }
            )
        abort(404)

    # GET questions search from backend
    # @app.route("/questions/search")
    # # http://127.0.0.1:5000/questions/search?search=What

    # def search_questions():
    #     search_term = request.args.get("search")
    #     selection = Question.query.filter(
    #         Question.question.ilike(f"%{search_term}%")
    #     ).all()
    #     search_questions = paginate_questions(request, selection)

    #     if search_term == None:
    #         abort(404)

    #     return jsonify(
    #         {
    #             "success": True,
    #             "questions": list(search_questions),
    #             "total_questions": len(selection),
    #         }
    #     )

    # Endpoint to get questions by category
    # GET questions based on category.
    @app.route("/categories/<int:id>/questions")
    def questions_in_category(id):
        # retrive the category by given id
        category = Category.query.filter_by(id=id).one_or_none()
        if category:
            # retrive all questions in a category
            questionsInCat = Question.query.filter_by(category=str(id)).all()
            currentQuestions = paginate_questions(request, questionsInCat)

            return jsonify(
                {
                    "success": True,
                    "questions": currentQuestions,
                    "total_questions": len(questionsInCat),
                    "current_category": category.type,
                }
            )
        # if category not founs
        else:
            abort(404)

    # Endpoint to play the quiz
    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        try:
            body = request.get_json()

            if not ("quiz_category" in body and "previous_questions" in body):
                abort(422)

            category = body.get("quiz_category")
            previous_questions = body.get("previous_questions")

            if category["type"] == "click":
                available_questions = Question.query.filter(
                    Question.id.notin_((previous_questions))
                ).all()
            else:
                available_questions = (
                    Question.query.filter_by(category=category["id"])
                    .filter(Question.id.notin_((previous_questions)))
                    .all()
                )

            new_question = (
                available_questions[
                    random.randrange(0, len(available_questions))
                ].format()
                if len(available_questions) > 0
                else None
            )

            return jsonify({"success": True, "question": new_question})
        except:
            abort(400)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {"success": False, "error": 422, "message": "Unprocessable entity"}
            ),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "Bad request"}), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "Internal server error"}
            ),
            500,
        )

    return app
