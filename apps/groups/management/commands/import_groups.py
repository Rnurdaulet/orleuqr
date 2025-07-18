import json
import uuid
from datetime import time
from django.core.management.base import BaseCommand
from apps.groups.models import Group, Session
from apps.participants.models import PersonProfile

ENTRY_START = time(hour=9)
ENTRY_END = time(hour=10)
EXIT_START = time(hour=17)
EXIT_END = time(hour=18)

#python manage.py import_groups apps/groups/data/response.json


class Command(BaseCommand):
    help = "Импорт групп, участников, тренеров и сессий из JSON (PersonProfile)"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Путь к JSON-файлу")

    def handle(self, *args, **options):
        path = options["json_file"]
        with open(path, "r", encoding="utf-8") as f:
            groups_data = json.load(f)

        for group_data in groups_data:
            # Тренер — роль TRAINER
            trainer, _ = PersonProfile.objects.get_or_create(
                iin=group_data["supervisorIIN"],
                defaults={
                    "full_name": group_data["supervisorName"].strip(),
                    "role": PersonProfile.Role.TRAINER,
                }
            )
            # Если у профиля неверная роль — обновим
            if trainer.role != PersonProfile.Role.TRAINER:
                trainer.role = PersonProfile.Role.TRAINER
                trainer.save(update_fields=["role"])

            # Создание или обновление группы
            group, created = Group.objects.update_or_create(
                external_id=group_data["groupId"],
                defaults={
                    "code": group_data["groupUnique"],
                    "course_name": group_data["courseName"].strip(),
                    "supervisor_name": trainer.full_name,
                    "supervisor_iin": trainer.iin,
                    "start_date": group_data["startingDate"][:10],
                    "end_date": group_data["endingDate"][:10],
                }
            )

            # Добавляем тренера в группу
            group.trainers.add(trainer)

            if created:
                self.stdout.write(self.style.SUCCESS(f"Создана группа {group.code}"))
            else:
                self.stdout.write(self.style.WARNING(f"Обновлена группа {group.code}"))

            # Участники — роль PARTICIPANT
            for listener in group_data.get("listenersList", []):
                iin = listener["iin"]
                full_name = f"{listener['surname']} {listener['name']}".strip()
                email = (listener.get("email") or "").strip()

                participant, _ = PersonProfile.objects.get_or_create(
                    iin=iin,
                    defaults={
                        "full_name": full_name,
                        "email": email,
                        "role": PersonProfile.Role.PARTICIPANT,
                    }
                )
                # Обновим роль при необходимости
                if participant.role != PersonProfile.Role.PARTICIPANT:
                    participant.role = PersonProfile.Role.PARTICIPANT
                    participant.save(update_fields=["role"])

                group.participants.add(participant)

            # Сессии
            for date_str in group_data.get("daysforAttendence", []):
                Session.objects.get_or_create(
                    group=group,
                    date=date_str[:10],
                    defaults={
                        "entry_start": ENTRY_START,
                        "entry_end": ENTRY_END,
                        "exit_start": EXIT_START,
                        "exit_end": EXIT_END,
                        "qr_token_entry": uuid.uuid4(),
                        "qr_token_exit": uuid.uuid4() if group.track_exit else None,
                    }
                )

        self.stdout.write(self.style.SUCCESS("Импорт завершён."))
