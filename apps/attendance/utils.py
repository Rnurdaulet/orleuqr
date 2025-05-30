from apps.attendance.models import TrustLog
from apps.participants.models import PersonProfile, BrowserFingerprint

def penalize_fingerprint(fingerprint, reason, delta, attendance=None):
    old_score = fingerprint.trust_score
    new_score = max(0, old_score + delta)
    if new_score != old_score:
        fingerprint.trust_score = new_score
        fingerprint.save(update_fields=["trust_score"])
        TrustLog.objects.create(
            fingerprint=fingerprint,
            attendance=attendance,
            reason=reason,
            delta=delta,
        )


def check_fingerprint_usage_conflicts(fingerprint, profile, session):
    others = (
        BrowserFingerprint.objects
        .filter(fingerprint_hash=fingerprint.fingerprint_hash)
        .exclude(profile=profile)
        .select_related("profile")
    )

    for other_fp in others:
        other = other_fp.profile
        if other == profile:
            continue

        is_trainer = other.role == PersonProfile.Role.TRAINER
        in_same_group = session.group in other.groups.all()

        if is_trainer:
            delta = -40
            reason = f"Отпечаток также используется тренером {other.full_name} ({other.iin})"
        elif in_same_group:
            delta = -20
            reason = f"Отпечаток ранее использовался участником той же группы: {other.full_name} ({other.iin})"
        else:
            delta = -10
            reason = f"Отпечаток ранее использовался участником из другой группы: {other.full_name} ({other.iin})"

        penalize_fingerprint(fingerprint, reason, delta)
