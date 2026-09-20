from ai.scoring import calculate_scores
from tests.test_validators import make_valid_evaluation


def test_calculate_scores():
    evaluation = make_valid_evaluation()

    scores = calculate_scores(evaluation)

    assert scores["technical_skills"] == 14
    assert scores["competitive_achievement"] == 0
    assert scores["relevant_experience"] == 9
    assert scores["projects"] == 11
    assert scores["demonstrated_potential"] == 3
    assert scores["domain_relevance"] == 5

    assert scores["total_score"] == 42