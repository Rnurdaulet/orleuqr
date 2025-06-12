from django.utils.timezone import now
from django.shortcuts import render
from django.db.models import Q

from apps.accounts.decorators import sso_login_required
from apps.groups.models import Group

@sso_login_required
def my_groups_view(request):
    today = now().date()
    user = request.user_profile

    groups = (
        Group.objects
        .filter(
            Q(participants=user) | Q(trainers=user),
            end_date__gte=today
        )
        .distinct()
        .prefetch_related("sessions", "participants", "trainers")
        .order_by("start_date")
    )

    return render(request, "groups/my_groups.html", {
        "groups": groups,
        "user": user,
    })
