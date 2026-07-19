from opendirector.production import (
    ProductionSpecification,
    ProductionSpecificationParser,
)


def test_defaults_are_simple_and_safe():
    specification = ProductionSpecification()

    assert specification.creative_profile == "movie"
    assert specification.preferred_orientation == "landscape"
    assert specification.aspect_ratio == "16:9"
    assert specification.narration_language == "English"
    assert specification.subtitle_languages == ("English",)


def test_parser_understands_filmmaker_brief():
    source = """
    Make a 50-second movie for X in landscape format.

    The story is about a lonely boy and a lost robot.

    The tone should be warm and hopeful.

    Narration in English.

    Generate subtitles in English and Chinese.

    Visual style: cinematic 3D animation.
    """

    specification = ProductionSpecificationParser().parse(source)

    assert specification.creative_profile == "movie"
    assert specification.distribution == "x"
    assert specification.preferred_orientation == "landscape"
    assert specification.aspect_ratio == "16:9"
    assert specification.target_duration_seconds == 50
    assert specification.narration_language == "English"
    assert specification.subtitle_languages == (
        "English",
        "Chinese",
    )
    assert specification.tone == "warm and hopeful"
    assert specification.visual_style == ("cinematic 3D animation")


def test_parser_understands_portrait_distribution():
    source = """
    Make a 45 second news video for TikTok.
    Use portrait composition.
    """

    specification = ProductionSpecificationParser().parse(source)

    assert specification.creative_profile == "news"
    assert specification.distribution == "tiktok"
    assert specification.preferred_orientation == "portrait"
    assert specification.aspect_ratio == "9:16"
    assert specification.target_duration_seconds == 45


def test_minutes_are_converted_to_seconds():
    specification = ProductionSpecificationParser().parse(
        "Create a 3-minute documentary for YouTube."
    )

    assert specification.target_duration_seconds == 180
    assert specification.distribution == "youtube"
    assert specification.creative_profile == "documentary"


def test_prompt_text_contains_shared_context():
    specification = ProductionSpecification(
        creative_profile="movie",
        distribution="x",
        preferred_orientation="landscape",
        target_duration_seconds=50,
        narration_language="English",
        subtitle_languages=("English", "Chinese"),
        visual_style="cinematic animation",
        tone="warm and hopeful",
    )

    prompt = specification.to_prompt_text()

    assert "Creative profile: movie" in prompt
    assert "Distribution: x" in prompt
    assert "Aspect ratio: 16:9" in prompt
    assert "Target duration: 50 seconds" in prompt
    assert "Subtitle languages: English, Chinese" in prompt
