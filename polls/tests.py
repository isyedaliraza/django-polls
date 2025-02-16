from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls.models import Question


def create_question(question_text, days):
    """
    Creates a Question object with `question_text` and published the
    given number of `days` offset to now (negative for past and positive
    for future questions).
    """
    time = timezone.now() + timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTestCase(TestCase):
    def test_was_published_with_future_question(self):
        question = create_question(question_text="Hello, World!", days=30)
        self.assertIs(question.was_published_recently(), False)

    def test_was_published_with_past_question(self):
        question = create_question(question_text="Hello, World!", days=-30)
        self.assertIs(question.was_published_recently(), False)

    def test_was_published_with_recent_question(self):
        time = timezone.now() - timedelta(hours=23, minutes=59, seconds=59)
        question = Question(question_text="Hello, World!", pub_date=time)
        self.assertIs(question.was_published_recently(), True)


class IndexViewTestCase(TestCase):
    def test_no_questions(self):
        """
        When there are no questions appropriate message should be displayed
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["latest_questions_list"], [])
        self.assertContains(response, "No polls are available.")

    def test_future_questions(self):
        """
        Future questions aren't displayed on the index page.
        """
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_questions_list"], [])
        self.assertContains(response, "No polls are available.")

    def test_past_questions(self):
        """
        Past questions are displayed on the index page.
        """
        question = create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_questions_list"], [question])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(question_text="Future question", days=30)
        question = create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_questions_list"], [question])

    def test_two_past_questions(self):
        """
        The index page may display more than one question.
        """
        q1 = create_question(question_text="Question 1", days=-30)
        q2 = create_question(question_text="Question 2", days=-15)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_questions_list"], [q2, q1])

    class QuestionDetailViewTests(TestCase):
        def test_future_question(self):
            """
            The detail view of a future question returns a 404 not found.
            """
            question = create_question(question_text="Future question", days=30)
            response = self.client.get(reverse("polls:detail", args=(question.id)))
            self.assertEqual(response.status_code, 404)

        def test_past_question(self):
            """
            The detail view of a past question displays the question's text.
            """
            question = create_question(question_text="Past question", days=-5)
            response = self.client.get(reverse("polls:detail", (question.id,)))
            self.assertContains(response, "Past question")
