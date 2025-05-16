from datetime import datetime, timedelta
from django.conf import settings

masterplan_app = settings.MASTERPLAN_APP
masterplan_port = settings.MASTERPLAN_PORT

def insert_absence(session, free_day_data):
    if not free_day_data['dates']:
        print(f"No free days for employee {free_day_data['employee_id']}")
        return
    for date in free_day_data['dates']:
        payload_data = {
            'action' : 'absence',
            'user' : int(free_day_data['employee_id']) + 2,
            'type' : 1,
            'start' : date,
            'end' : date,
            'comment' : ""
        }

        absence_request_url = f"http://{masterplan_app}:{masterplan_port}/masterplan/frontend/index.php?view=absenceLastMinute"

        response = session.post(absence_request_url, data=payload_data)

        if response.status_code != 200:
            raise Exception(f"Failed to insert absence for employee {free_day_data['employee_id']} on date {date}")

        print(f"Inserted absence for employee {free_day_data['employee_id']} on date {date}")

    print(f"Finished inserting absences for employee {free_day_data['employee_id']}")