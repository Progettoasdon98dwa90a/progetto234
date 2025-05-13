from django.http import JsonResponse
from api.models import Employee, Schedule, ScheduleEvent
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_schedule_event(request, schedule_id):
    if request.method != 'POST':
        return JsonResponse({"status" : "error"}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    try:
        schedule_id = int(schedule_id)
        schedule = Schedule.objects.get(id=schedule_id)
    except:
        return JsonResponse({"status" : "error", 'message': 'Invalid schedule ID'}, status=400)
    try:
        employee_id = int(data.get('employeeId'))
        employee = Employee.objects.get(id=employee_id)
    except Exception as e:
        print(e)
        return JsonResponse({"status" : "error", 'message': 'Invalid employee ID'}, status=400)

    if data.get('id'):
        try:
            event_to_update_id = int(data.get('id'))
            event_to_update = ScheduleEvent.objects.get(id=event_to_update_id)
            event_to_update.employee = employee
            event_to_update.date = data.get('date', event_to_update.date)
            event_to_update.start_time = data.get('startTime', event_to_update.start_time)
            event_to_update.end_time = data.get('endTime', event_to_update.end_time)
            event_to_update.color = data.get('color', event_to_update.color)
            event_to_update.save()
            print(f"Schedule event updated successfully: {event_to_update}")
            # return all events of this schedule
            all_schedule_events = ScheduleEvent.objects.filter(schedule_id=schedule_id)
            events_data = [event.format_json() for event in all_schedule_events]

            return JsonResponse({"status": "success", "events": events_data, "scope": "update"}, status=200)
        except Exception as e:
            print(f"Error updating schedule event: {e}")
            return JsonResponse({"status" : "error", 'message': 'Error updating schedule event'}, status=500)
    
    date = data.get('date', None)
    start_time = data.get('startTime', None)
    end_time = data.get('endTime', None)
    color = data.get('color', None)

    if not all([date, start_time, end_time, color]):
        return JsonResponse({"status" : "error", 'message': 'Missing required fields'}, status=400)

    try:
        schedule_event = ScheduleEvent.objects.create(
            schedule=schedule, 
            employee=employee, 
            date = date,
            start_time=start_time, 
            end_time=end_time, 
            color=color)
        
        schedule_event.save()
        print(f"Schedule event created successfully: {schedule_event}")
        # return all events of this schedule
        all_schedule_events = ScheduleEvent.objects.filter(schedule_id=schedule_id)
        events_data = [event.format_json() for event in all_schedule_events]

        return JsonResponse({"status": "success", "events": events_data}, status=200)
    except Exception as e:
        print(f"Error creating schedule event: {e}")
        schedule_event = None
        return JsonResponse({"status" : "error", 'message': 'Error creating schedule event'}, status=500)
    

def get_schedule_events(request, schedule_id):
    if request.method == 'GET':
        try:
            schedule_events = ScheduleEvent.objects.filter(schedule_id=schedule_id)
            events_data = [event.format_json() for event in schedule_events]
            return JsonResponse({"status": "success", 'events': events_data}, status=200)
        
        except ScheduleEvent.DoesNotExist:
            return JsonResponse({"status" : "error", 'message': 'Schedule events not found'}, status=404)
        except Exception as e:
            print(f"Error getting schedule events: {e}")
            return JsonResponse({"status" : "error", 'message': 'Error getting schedule events'}, status=500)
    else:
        return JsonResponse({"status" : "error", 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def delete_schedule_event(request, schedule_id, event_id):
    if request.method == 'DELETE':
        try:
            event_to_delete = ScheduleEvent.objects.get(id=event_id)
            event_to_delete.delete()
            print(f"Schedule event deleted successfully: {event_to_delete}")
            # return all events of this schedule
            all_schedule_events = ScheduleEvent.objects.filter(schedule_id=schedule_id)
            events_data = [event.format_json() for event in all_schedule_events]

            return JsonResponse({"status": "success", "events": events_data}, status=200)
        except ScheduleEvent.DoesNotExist:
            return JsonResponse({"status" : "error", 'message': 'Schedule event not found'}, status=404)
        except Exception as e:
            print(f"Error deleting schedule event: {e}")
            return JsonResponse({"status" : "error", 'message': 'Error deleting schedule event'}, status=500)
    else:
        return JsonResponse({"status" : "error", 'message': 'Invalid request method'}, status=405)
    
