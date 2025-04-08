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


class Role(models.Model):

    name = models.CharField(default="", max_length=50)

    max_hours_per_day = models.IntegerField(default=0)
    max_services_per_week = models.IntegerField(default=0)
    max_hours_per_week = models.IntegerField(default=0)
    max_hours_per_month = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, default="F")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, default=1)
    extra_data = models.JSONField(default=dict)

    def __str__(self):
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