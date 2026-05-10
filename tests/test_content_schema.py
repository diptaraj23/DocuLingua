from app.learning.content_schema import DocumentOverview, LearningGuide, LearningStatistics


def test_minimal_learning_guide_can_be_created() -> None:
    guide = LearningGuide(
        title="Minimal Guide",
        overview=DocumentOverview(
            learning_statistics=LearningStatistics(vocabulary_count=1),
        ),
    )

    assert guide.title == "Minimal Guide"
    assert guide.overview.learning_statistics.vocabulary_count == 1
    assert guide.answer_key == []
