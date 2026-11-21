"""One serialized decision only; never opens a dataset or trains a model."""
import json
import sys
from pathlib import Path
from dataclasses import asdict
from .schema import DecisionSnapshot
from .predictor import FrozenServiceModel,ConditionalScenario
from .planner import plan

if __name__=='__main__':
    data=json.loads(Path(sys.argv[1]).read_text())
    scenes=None if data['scenarios'] is None else tuple(ConditionalScenario.from_dict(x) for x in data['scenarios'])
    result=plan(DecisionSnapshot.from_dict(data['snapshot']),FrozenServiceModel.from_dict(data['model']),isolated_scenarios=scenes)
    with Path(sys.argv[2]).open('x') as f:json.dump(asdict(result),f,allow_nan=False)
