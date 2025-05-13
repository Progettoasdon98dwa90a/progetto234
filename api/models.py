from django.db import models

from django.core.exceptions import ValidationError

from datetime import datetime

# Create your models here.

class Branch(models.Model):
    name = models.CharField(max_length=100)
    extra_data = models.JSONField(default=dict)

    def __str__(self):
        return f"BRANCH #{self.id} {self.name}"

    def get_brand(self):
        try:
            brand = self.extra_data["brand"]
            return brand
        except:
            return 0


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    genre = models.IntegerField(default=0)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    role = models.IntegerField(default=0)
    birth_date = models.CharField(default="", max_length=100)
    phone_number = models.CharField(default="", max_length=100)
    email = models.CharField(default="", max_length=100)
    skill_class = models.IntegerField(default=0)  # 0 = D, 1 = C, 2 = B, 3 = A
    contract_type = models.IntegerField(default=0)  # 0 = Part-time, 1 = Full-time
    contract_start = models.CharField(default="", max_length=100)
    contract_end = models.CharField(default="", max_length=100)
    max_hours_per_month = models.IntegerField(default=0)
    max_hours_per_week = models.IntegerField(default=0)
    max_hours_per_day = models.IntegerField(default=0)
    max_hours_per_shift = models.IntegerField(default=0)
    rest_days = models.JSONField(default=list, blank=True)

    hourly_cost = models.FloatField(default=0.0)

    extra_data = models.JSONField(default=dict)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Schedule(models.Model):

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    employees = models.JSONField(default=dict, blank=True)
    start_date = models.CharField(default="", max_length=100)
    end_date = models.CharField(default="", max_length=100)
    shift_data = models.JSONField(default=dict, blank=True)
    closing_days = models.JSONField(default=dict, blank=True)
    free_days = models.JSONField(default=dict, blank=True)

    schedule_data = models.JSONField(default=dict, blank=True)
    schedule_events = models.JSONField(default=dict, blank=True)

    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"SCHEDULE #{self.id}"

    def clean(self):
        """
        Validate that there is no overlapping schedule for the same branch.
        Assumes start_date and end_date are stored in ISO format (YYYY-MM-DD).
        """
        # Parse the start and end dates. If parsing fails, raise a ValidationError.
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
            end = datetime.strptime(self.end_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Formato data non valido. Utilizzare YYYY-MM-DD sia per la data di inizio che di fine.")

        # Check that the start date is not after the end date.
        if start > end:
            raise ValidationError("La data di inizio non può essere successiva alla data di fine.")

        # Query for overlapping schedules for the same branch.
        # Two schedules overlap if:
        #     schedule1.start_date <= schedule2.end_date and schedule1.end_date >= schedule2.start_date
        overlapping_schedules = Schedule.objects.filter(
            branch=self.branch,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
        )
        # Exclude this schedule (in case of updates)
        if self.pk:
            overlapping_schedules = overlapping_schedules.exclude(pk=self.pk)

        if overlapping_schedules.exists():
            raise ValidationError("Esiste già un orario per questa sede nel range di date selezionato.")

    def save(self, *args, **kwargs):
        # Call full_clean() to run the clean() method before saving.
        self.full_clean()
        super().save(*args, **kwargs)


class Import(models.Model):

    import_date = models.CharField(default="", max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    import_type = models.CharField(max_length=100, default="")
    data = models.JSONField(default=dict)

    def __str__(self):
        return f"IMPORT #{self.id}"


class Target(models.Model):

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    start_date = models.CharField(default="", max_length=100)
    end_date = models.CharField(default="", max_length=100)
    sales_target = models.FloatField(default=0.0)

    def __str__(self):
        return f"TARGET #{self.id}"


class ScheduleEvent(models.Model):
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, related_name="events")
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name="schedule_events")
    event = models.CharField(max_length=100, blank=True,
                             help_text="Brief description of the event (e.g., 'Morning Shift', 'Meeting').")

    # --- CRITICAL CHANGE: Use DateTimeField ---
    # If your events are always within a single day and the Schedule model defines the date,
    # you might use TimeField. But DateTimeField is more robust for general scheduling.
    # Assuming USE_TZ = True in your settings.py for proper timezone handling.
    start_datetime = models.DateTimeField(help_text="Start date and time of the event.")
    end_datetime = models.DateTimeField(help_text="End date and time of the event.")

    color = models.CharField(default="#3788D8", max_length=10, blank=True,
                             help_text="Hex color code for the event display (e.g., #FF5733).")

    class Meta:
        ordering = ['start_datetime', 'employee']
        # For more advanced database-level constraints (e.g., PostgreSQL):
        # constraints = [
        #     models.CheckConstraint(
        #         check=models.Q(end_datetime__gt=models.F('start_datetime')),
        #         name='end_datetime_after_start_datetime'
        #     ),
        #     # PostgreSQL specific: EXCLUDE constraint for non-overlapping times per employee
        #     # This requires enabling the 'btree_gist' extension in PostgreSQL.
        #     # models.UniqueConstraint(
        #     #     fields=['employee'],
        #     #     condition=..., # This is tricky, usually done with EXCLUDE USING gist
        #     #     name='unique_employee_event_time_slot'
        #     # )
        # ]

    def __str__(self):
        return f"{self.event or 'Event'} for {self.employee} ({self.start_datetime.strftime('%Y-%m-%d %H:%M')} - {self.end_datetime.strftime('%H:%M')})"

    @property
    def duration(self):
        """Returns the duration of the event as a timedelta object."""
        if self.start_datetime and self.end_datetime:
            return self.end_datetime - self.start_datetime
        return None

    def clean(self):
        """
        Custom validation for the model.
        This is called by ModelForms and during full_clean().
        """
        super().clean()  # Call parent's clean first

        # 1. Basic Validation: End time must be after start time
        if self.start_datetime and self.end_datetime:
            if self.start_datetime >= self.end_datetime:
                raise ValidationError({
                    'end_datetime': "End time must be after start time."
                })

            # Optional: Minimum event duration (e.g., 5 minutes)
            # min_duration = timezone.timedelta(minutes=5)
            # if (self.end_datetime - self.start_datetime) < min_duration:
            #     raise ValidationError({
            #         'end_datetime': f"Event duration must be at least {min_duration}."
            #     })

        # 2. Collision Detection for the SAME employee
        #    Different employees CAN have events at the same time.
        if self.employee and self.start_datetime and self.end_datetime:
            # Query for existing events for this employee that overlap with the current event's time range.
            # An overlap occurs if:
            # (ExistingStart < NewEnd) AND (ExistingEnd > NewStart)
            conflicting_events = ScheduleEvent.objects.filter(
                employee=self.employee,
                start_datetime__lt=self.end_datetime,  # Existing event starts before the new one ends
                end_datetime__gt=self.start_datetime  # Existing event ends after the new one starts
            )

            # If we are updating an existing event, we must exclude ITSELF from the conflict check.
            if self.pk:  # self.pk is None if this is a new object being created
                conflicting_events = conflicting_events.exclude(pk=self.pk)

            if conflicting_events.exists():
                # Provide a more detailed error message
                conflicts_details = []
                for ce in conflicting_events:
                    conflicts_details.append(
                        f"'{ce.event or 'Unnamed Event'}' from {ce.start_datetime.strftime('%H:%M')} to {ce.end_datetime.strftime('%H:%M')} on {ce.start_datetime.strftime('%Y-%m-%d')}"
                    )
                raise ValidationError({
                    'employee': f"This time slot for {self.employee.name if hasattr(self.employee, 'name') else self.employee} "
                                f"conflicts with existing event(s): {'; '.join(conflicts_details)}."
                })

        # 3. Ensure event is within the Schedule's timeframe (if Schedule has one)
        # Example: If your Schedule model has `start_date` and `end_date`
        # if self.schedule and hasattr(self.schedule, 'start_date') and hasattr(self.schedule, 'end_date'):
        #     if self.schedule.start_date and self.start_datetime.date() < self.schedule.start_date:
        #         raise ValidationError({'start_datetime': "Event starts before the schedule's period."})
        #     if self.schedule.end_date and self.end_datetime.date() > self.schedule.end_date:
        #         raise ValidationError({'end_datetime': "Event ends after the schedule's period."})

    def save(self, *args, **kwargs):
        """
        Override save to ensure clean() is called.
        Note: clean() is not called automatically by save() unless you're using a ModelForm.
        For direct model saves, it's good practice to call full_clean().
        """
        self.full_clean()  # This will call the clean() method
        super().save(*args, **kwargs)