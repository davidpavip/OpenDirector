from pathlib import Path

import pytest

from opendirector.products import (
    AnimationProduct,
    CreativeProduct,
    ProductType,
    ReviewProduct,
    SketchProduct,
)


def test_production_owned_product():
    product = CreativeProduct(
        product_type=ProductType.FINAL,
        path=Path("products/final/movie.mp4"),
        production_id="little_robot",
    )

    assert product.scope == "production"
    assert product.scene_id is None
    assert product.shot_id is None


def test_scene_owned_product():
    product = CreativeProduct(
        product_type=ProductType.MUSIC,
        path=Path("scenes/scene-001/products/audio/music.wav"),
        production_id="little_robot",
        scene_id="scene-001",
    )

    assert product.scope == "scene"


def test_shot_owned_product():
    product = SketchProduct(
        product_type=ProductType.SKETCH,
        path=Path("scenes/scene-001/products/sketch/shot-001.svg"),
        production_id="little_robot",
        scene_id="scene-001",
        shot_id="shot-001",
        provider_id="mock.sketch",
        media_type="image/svg+xml",
    )

    assert product.scope == "shot"
    assert product.provider_id == "mock.sketch"


def test_shot_product_requires_scene():
    with pytest.raises(
        ValueError,
        match="must also belong to a scene",
    ):
        CreativeProduct(
            product_type=ProductType.ANIMATION,
            path=Path("shot-001.mp4"),
            production_id="little_robot",
            shot_id="shot-001",
        )


def test_animation_product_validates_duration():
    with pytest.raises(
        ValueError,
        match="duration cannot be negative",
    ):
        AnimationProduct(
            product_type=ProductType.ANIMATION,
            path=Path("shot-001.mp4"),
            production_id="little_robot",
            scene_id="scene-001",
            shot_id="shot-001",
            duration_seconds=-1,
        )


def test_review_product_validates_score():
    with pytest.raises(
        ValueError,
        match="between 0 and 1",
    ):
        ReviewProduct(
            product_type=ProductType.REVIEW,
            path=Path("review.md"),
            production_id="little_robot",
            scene_id="scene-001",
            score=1.5,
        )
