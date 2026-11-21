"""Unchanged finite event and learning identity, new conditional q domain."""
from raven_mcs.control.calibration_identity import ClockNamespace,endpoint,service_parameters_hash
from raven_mcs.control.calibration_identity import applicability as _base_applicability
from . import METHOD_VERSION

def applicability(**kwargs):
    value=_base_applicability(**kwargs)
    value.update(schema='q_policy_applicability_RE_interval_v3',consumption_policy=METHOD_VERSION,
        conditional_domain='R=1,E=1',q_estimand='P_pi(I(100)=1|H,R=1,E=1)',
        eligibility='registration_age<=5; not positivity',
        service_fit_rule='all-registration joint R/resource/client/age; conditional competing risks and same-client marks; frozen at warmup20',
        evidence_status='DIAGNOSTIC_OR_EXTERNAL_EVIDENCE_REQUIRED')
    return value
