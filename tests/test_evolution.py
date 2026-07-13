from opendirector.evolution import (
    EvolutionEngine,
    SeedThenEvolveStrategy,
)


def test_engine_requires_strategy():
    class DummyStrategy:
        name = "dummy"

        def operators_for_generation(
            self,
            context,
            generation,
        ):
            return ()

    engine = EvolutionEngine(DummyStrategy())

    assert engine.strategy.name == "dummy"
