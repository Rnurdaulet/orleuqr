import json
from django.core.management.base import BaseCommand
from apps.groups.models import Group, Session
from apps.participants.models import ParticipantProfile


class Command(BaseCommand):
    help = "Импорт групп, участников и сессий из JSON"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Путь к JSON-файлу")

    def handle(self, *args, **options):
        path = options["json_file"]
        with open(path, "r", encoding="utf-8") as f:
            groups_data = json.load(f)

        for group_data in groups_data:
            group, created = Group.objects.update_or_create(
                external_id=group_data["groupId"],
                defaults={
                    "code": group_data["groupUnique"],
                    "course_name": group_data["courseName"].strip(),
                    "supervisor_name": group_data["supervisorName"].strip(),
                    "supervisor_iin": group_data["supervisorIIN"],
                    "start_date": group_data["startingDate"][:10],
                    "end_date": group_data["endingDate"][:10],
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Создана группа {group.code}"))
            else:
                self.stdout.write(self.style.WARNING(f"Обновлена группа {group.code}"))

            # Участники
            for listener in group_data.get("listenersList", []):
                profile, _ = ParticipantProfile.objects.get_or_create(
                    iin=listener["iin"],
                    defaults={
                        "full_name": f"{listener['surname']} {listener['name']}".strip(),
                        "email": (listener.get("email") or "").strip()
                    },
                )
                group.participants.add(profile)

            # Сессии по дням
            for date_str in group_data.get("daysforAttendence", []):
                Session.objects.get_or_create(
                    group=group,
                    date=date_str[:10],
                )

        self.stdout.write(self.style.SUCCESS("Импорт завершён."))
