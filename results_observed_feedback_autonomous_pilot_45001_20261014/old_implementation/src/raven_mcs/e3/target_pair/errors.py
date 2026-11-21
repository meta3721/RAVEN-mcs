"""Explicit production runner hard-stop errors."""


class TargetWiringError(RuntimeError):
    CODE = "TARGET_WIRING_ERROR"


class PairSupportError(RuntimeError):
    CODE = "PAIR_SUPPORT_ERROR"


class PairWeightBindingError(RuntimeError):
    CODE = "PAIR_WEIGHT_BINDING_ERROR"


class HeadTailWiringError(RuntimeError):
    CODE = "HEAD_TAIL_WIRING_ERROR"


class RhoWeightError(RuntimeError):
    CODE = "RHO_WEIGHT_ERROR"


class AtomicPobsError(RuntimeError):
    CODE = "ATOMIC_POBS_ERROR"


class PiOppScaleError(RuntimeError):
    CODE = "PIOPP_SCALE_ERROR"


class CentralMetricApplicabilityError(RuntimeError):
    CODE = "CENTRAL_METRIC_APPLICABILITY_ERROR"
