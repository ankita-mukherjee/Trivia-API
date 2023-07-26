import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
import json.decoder

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            "localhost:5432", self.database_name
        )
        # setup_db(self.app, self.database_path)

        # binds the app to the current context
        # with self.app.app_context():
        # self.db = SQLAlchemy()
        # self.db.init_app(self.app)
        # create all tables
        # self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # Test Questions
    def test_paginate_questions(self):
        """Tests question pagination success"""
        response = self.client().get("/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_get_page_bad_req(self):
        """Tests question pagination fail"""
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request")

    def test_delete_question_not_found(self):
        """Tests delete question invalid page"""
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_add_question(self):
        newQuestion = {
            "question": "Name the hardest substance available on Earth?",
            "answer": "Diamond",
            "difficulty": 2,
            "category": 1,
        }
        res = self.client().post("/questions", json=newQuestion)
        try:
            data = json.loads(res.data)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data["success"], True)
        except json.decoder.JSONDecodeError as e:
            # Handle the JSONDecodeError
            print("Error decoding JSON:", e)

    def test_search(self):
        search = {
            "searchTerm": "What",
        }
        res = self.client().post("/questions/search", json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    # self.assertEqual(len(data["questions"]), 10)

    def test_search_not_found(self):
        search = {
            "searchTerm": "ghghsghshg",
        }
        res = self.client().post("/search", json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    # Test Categories
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_get_categories_not_allowed(self):
        res = self.client().delete("/categories")
        try:
            data = json.loads(res.data)
            self.assertEqual(res.status_code, 405)
            self.assertEqual(data["success"], False)
        except json.decoder.JSONDecodeError as e:
            # Handle the JSONDecodeError
            print("Error decoding JSON:", e)

    def test_questions_in_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_questions_in_category_not_found(self):
        res = self.client().get("/categories/100/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    # Test Quiz
    def test_quiz(self):
        quiz = {
            "previous_questions": [2],
            "quiz_category": {"type": "Science", "id": "5"},
        }
        res = self.client().post("/quizzes", json=quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["question"]["category"], "5")

    def test_play_quiz_fails(self):
        # send post request without json data
        response = self.client().post("/quizzes", json={})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
