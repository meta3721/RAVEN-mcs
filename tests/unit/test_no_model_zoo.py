from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    "src/raven_mcs/sag/r1m_features.py",
    "src/raven_mcs/sag/r1m_predictor.py",
    "src/raven_mcs/sag/r1m_reset.py",
    "src/raven_mcs/sag/r1m_track.py",
]
FORBIDDEN = (
    "RandomForest",
    "XGBClassifier",
    "XGBRegressor",
    "MLPRegressor",
    "ARIMA",
    "LogisticRegression",
    "GradientBoosting",
)


def test_no_model_zoo() -> None:
    blob = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in FILES)
    for name in FORBIDDEN:
        assert name not in blob
    assert "sklearn" not in (ROOT / "src/raven_mcs/sag/r1m_predictor.py").read_text(encoding="utf-8")
