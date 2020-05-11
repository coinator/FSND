import json
import random

from flask import abort, Flask, jsonify, request
from flask_cors import CORS

from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [q.format() for q in selection]
    return questions[start:end]


def format_categories(categories):
    formatted_categories = [c.format() for c in categories]
    formatted_categories = {c["id"]: c["type"] for c in formatted_categories}
    return formatted_categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PATCH,POST,DELETE,OPTIONS"
        )
        return response

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": ""}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "Not found"}), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return (
            jsonify(
                {"success": False, "error": 422, "message": "Unprocessable entity"}
            ),
            422,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "Internal Server Error"}
            ),
            500,
        )

    @app.route("/categories")
    def get_categories():
        try:
            categories = Category.query.all()
            formatted_categories = format_categories(categories)
            if len(categories) == 0:
                abort(404)

            return jsonify({"success": True, "categories": formatted_categories})
        except:
            abort(400)

    @app.route("/categories/<category_id>/questions")
    def get_category_questions(category_id):
        category = Category.query.get(category_id)

        if not category:
            abort(404)

        current_category = category.format()

        categories = Category.query.all()
        formatted_categories = format_categories(categories)

        questions = Question.query.filter_by(category=category_id).all()
        formatted_questions = paginate_questions(request, questions)

        if len(questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": formatted_questions,
                "totalQuestions": len(questions),
                "categories": formatted_categories,
                "currentCategory": current_category,
            }
        )

    @app.route("/questions")
    def get_question():
        questions = Question.query.all()

        # catches no questions in db
        if len(questions) == 0:
            abort(404)

        formatted_questions = paginate_questions(request, questions)

        # catches invalid pages
        if len(formatted_questions) == 0:
            abort(404)

        categories = Category.query.all()
        current_category = Category.query.get(1).format()
        formatted_categories = format_categories(categories)
        return jsonify(
            {
                "success": True,
                "questions": formatted_questions,
                "totalQuestions": len(questions),
                "categories": formatted_categories,
                "currentCategory": current_category,
            }
        )

    @app.route("/questions", methods=["POST"])
    def post_question():
        data = json.loads(request.data)
        if "searchTerm" in data:
            search_term = data["searchTerm"]
            try:
                questions = Question.query.filter(
                    Question.question.ilike(f"%{search_term}%")
                ).all()

                questions = [q.format() for q in questions]
                return jsonify({"success": True, "questions": questions})
            except:
                abort(400)
        else:
            if any(value is None for value in data.values()):
                abort(422)
            try:
                new_question = Question(**data)
                new_question.insert()
            except TypeError:
                abort(422)
            return jsonify({"success": True})

    @app.route("/questions/<id>", methods=["DELETE"])
    def delete_question(id):
        question = Question.query.get(id)

        if question is None:
            abort(404)

        question.delete()

        return jsonify({"success": True})

    @app.route("/quizzes", methods=["POST"])
    def create_quiz():
        data = json.loads(request.data)
        previous_questions = data["previous_questions"]
        category_id = data["quiz_category"]["id"]
        if category_id == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(Question.category == category_id).all()
        questions = [
            question.format()
            for question in questions
            if question.id not in previous_questions
        ]
        return jsonify(
            {
                "success": True,
                "question": random.choice(questions) if questions else False,
            }
        )

    return app
