from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from api.models import ScheduleEvent, Schedule # Import your models

# Assume your check logic is in a function or a method on the Schedule model
# For example, let's define a placeholder function here or on the Schedule model

def run_schedule_check(schedule):
    """
    Placeholder function for the check logic.
    This function will be called whenever a ScheduleEvent
    related to this schedule is saved or deleted.

    Args:
        schedule: The Schedule instance affected by the event change.
    """
    print(f"DEBUG: Running check for Schedule #{schedule.id}...")
    backup_exists = schedule.backup_exists()
    if not backup_exists:
        schedule.backup_to_json()
    else:
        pass


@receiver(post_save, sender=ScheduleEvent)
def schedule_event_saved(sender, instance, created, **kwargs):
    """
    Signal receiver for ScheduleEvent post-save (create or update).
    """
    # instance is the ScheduleEvent object that was just saved
    # created is True if the object was created, False if updated
    print(f"DEBUG: ScheduleEvent #{instance.id} was {'created' if created else 'updated'}.")
    run_schedule_check(instance.schedule) # Call the check logic on the related schedule

@receiver(post_delete, sender=ScheduleEvent)
def schedule_event_deleted(sender, instance, **kwargs):
    """
    Signal receiver for ScheduleEvent post-delete.
    """
    # instance is the ScheduleEvent object that was just deleted
    print(f"DEBUG: ScheduleEvent #{instance.id} was deleted.")
    # Access the schedule ID before the object is fully gone from the DB
    # Note: accessing instance.schedule might still work here as the related
    # object is usually still in memory, but using the ID is sometimes safer
    # depending on how deletion happened (e.g., cascade).
    # Let's assume instance.schedule is available here.
    run_schedule_check(instance.schedule) # Ca