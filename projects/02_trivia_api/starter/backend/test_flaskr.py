import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

import logging


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = f"postgres:///{self.database_name}"
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get("/categories")
        res.dict = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.dict,
            {
                "categories": {
                    "1": "Science",
                    "2": "Art",
                    "3": "Geography",
                    "4": "History",
                    "5": "Entertainment",
                    "6": "Sports",
                },
                "success": True,
            },
        )

    def test_get_questions_first_page(self):
        res = self.client().get("/questions")
        response = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response["questions"]), 10)
        self.assertEqual(response["totalQuestions"], 19)

    def test_get_questions_last_page(self):
        res = self.client().get("/questions?page=2")
        response = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response["questions"]), 9)
        self.assertEqual(response["totalQuestions"], 19)

    def test_get_questions_non_existing_page(self):
        res = self.client().get("/questions?page=10")
        response = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(
            response, {"error": 404, "message": "Not found", "success": False}
        )

    def test_delete_question(self):
        """ create question with SQL alchemy and delete with api"""
        data = {
            "question": "random",
            "answer": "random",
            "category": 1,
            "difficulty": 1,
        }
        question = Question(**data)
        question.insert()

        questions_count = len(Question.query.all())
        question_id = question.id

        res = self.client().delete(f"/questions/{question.id}")
        response = json.loads(res.data)
        self.assertEqual(response, {"success": True})

        res = self.client().get("/questions")
        response = json.loads(res.data)
        total_after = response["totalQuestions"]
        self.assertEqual(questions_count, total_after + 1)

    def test_delete_question_bad_id_returns_404(self):
        res = self.client().delete(f"/questions/1000001")
        response = json.loads(res.data)
        self.assertEqual(
            response, {"error": 404, "message": "Not found", "success": False}
        )

    def test_create_question_successfully_creates_question(self):
        question_text = "This is a dumb fake question"
        question_answer = "This is a dumb fake answer"
        question_category = "1"
        question_difficulty = 1
        data = {
            "question": question_text,
            "answer": question_answer,
            "difficulty": question_difficulty,
            "category": question_category,
        }
        res = self.client().post("/questions", json=data)
        response = json.loads(res.data)
        self.assertEqual(response, {"success": True})

        # delete the question we just created to keep database the same
        question_to_delete = Question.query.filter(
            Question.question == question_text
        ).one_or_none()
        question_to_delete.delete()

    def test_create_question_throws_error_if_fields_missing(self):
        question_text = "This is a dumb fake question"
        question_answer = "This is a dumb fake answer"
        question_category = "1"
        data = {
            "question": question_text,
            "answer": question_answer,
            "category": question_category,
        }
        res = self.client().post("/questions", json=data)
        response = json.loads(res.data)
        self.assertEqual(
            response,
            {"success": False, "error": 422, "message": "Unprocessable entity"},
        )

    def test_question_search(self):
        data = {"searchTerm": "title"}
        res = self.client().post("/questions", json=data)
        response = json.loads(res.data)
        self.assertEqual(response["success"], True)
        questions = response["questions"]
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0]["id"], 5)
        self.assertEqual(questions[1]["id"], 6)

    def test_get_category_questions(self):
        res = self.client().get("/categories/1/questions")
        response = json.loads(res.data)
        self.assertEqual(response["currentCategory"], {"id": 1, "type": "Science"})
        self.assertEqual(len(response["questions"]), 3)

    def test_get_questions_by_category_returns_error_for_bad_category(self):
        res = self.client().get("/categories/100000/questions")
        response = json.loads(res.data)
        self.assertEqual(
            response, {"error": 404, "message": "Not found", "success": False}
        )

    def test_create_quiz(self):
        data = {"previous_questions": [1], "quiz_category": {"id": 1}}
        res = self.client().post("/quizzes", json=data)
        response = json.loads(res.data)
        self.assertEqual(response["question"]["category"], 1)

        # assert previous doesn't reapper
        self.assertTrue(response["question"]["id"] != 1)


if __name__ == "__main__":
    unittest.main()
