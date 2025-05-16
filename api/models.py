import json
from pathlib import Path

from django.conf import settings
from django.db import models, transaction

from django.core.exceptions import ValidationError

from datetime import datetime, timedelta


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

    def get_total_medium_receipts_number(self):
        from api.formulas.receipts import get_scontrini_dipendente_date_range
        total_worked_days = self.get_total_working_days()

        data = int(get_scontrini_dipendente_date_range(self.id, None, None) / total_worked_days)
        return data

    def get_total_medium_sales(self):
        from api.formulas.sales import get_total_sales_dipendente
        total_worked_days = self.get_total_working_days()
        data = round(get_total_sales_dipendente(self.id) / total_worked_days, 2)
        return data

    def get_total_working_days(self):
        from api.formulas.work_calculation import get_total_working_days_dipendente
        data = get_total_working_days_dipendente(self.id)
        return data





class Schedule(models.Model):

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    title = models.CharField(default="", max_length=100)
    employees = models.JSONField(default=dict, blank=True)
    start_date = models.CharField(default="", max_length=100)
    end_date = models.CharField(default="", max_length=100)
    shifts_data = models.JSONField(default=dict, blank=True)
    closing_days = models.JSONField(default=dict, blank=True)
    free_days = models.JSONField(default=dict, blank=True)
    particular_days = models.JSONField(default=dict, blank=True)

    can_modify = models.BooleanField(default=False)

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

    # Helper to get shifts by name
    def _get_shifts_map(self):
        """Creates a dictionary mapping shift name to shift details."""
        shifts_map = {}
        # Ensure shifts_data is a list, default can be empty list
        if isinstance(self.shifts_data, list):
            for shift in self.shifts_data:
                if 'name' in shift:
                    shifts_map[shift['name']] = shift
        return shifts_map

    def generate_schedule_periods(self):
        """
        Generates a list of schedule periods based on the overall dates
        and particular days.

        Returns:
            list: A list of dictionaries, each representing a period:
                  [
                      {
                          "start_date": "YYYY-MM-DD",
                          "end_date": "YYYY-MM-DD",
                          "shifts": [...] # List of shift dictionaries valid for this period
                      },
                      ...
                  ]
        """
        periods = []

        try:
            # Convert start and end dates to date objects
            start_d = datetime.strptime(self.start_date, "%Y-%m-%d").date()
            end_d = datetime.strptime(self.end_date, "%Y-%m-%d").date()
        except ValueError:
            # This should ideally be caught by clean(), but good to handle defensively
            print(f"Warning: Invalid date format in schedule {self.id}. Cannot generate periods.")
            return periods  # Return empty list if dates are invalid

        # Parse and sort particular days' dates
        particular_days_data = {}
        particular_dates_list = []
        for date_str, data in self.particular_days.items():
            try:
                p_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                # Check if the particular day is within the overall schedule range
                if start_d <= p_date <= end_d:
                    particular_days_data[p_date] = data  # Store data using date object as key
                    particular_dates_list.append(p_date)
                else:
                    print(
                        f"Warning: Particular day {date_str} is outside schedule range for schedule {self.id} and will be ignored.")
            except ValueError:
                # This should also be caught by clean(), print warning and skip
                print(
                    f"Warning: Invalid date format '{date_str}' in particular_days for schedule {self.id}. Ignoring.")
                continue  # Skip this particular day

        particular_dates_list.sort()

        # Create a map of standard shifts for quick lookup
        shifts_map = self._get_shifts_map()
        standard_shifts = list(shifts_map.values())  # List of all standard shifts

        current_start_date = start_d

        # Iterate through sorted particular days to define periods
        for p_date in particular_dates_list:
            # 1. Add a normal period *before* the particular day (if any)
            end_of_normal_period = p_date - timedelta(days=1)

            if current_start_date <= end_of_normal_period:
                periods.append({
                    "start_date": current_start_date.strftime("%Y-%m-%d"),
                    "end_date": end_of_normal_period.strftime("%Y-%m-%d"),
                    "shifts": standard_shifts  # Apply all standard shifts
                })

            # 2. Add the particular day period
            p_shift_info = particular_days_data[p_date]  # Get the [count, shift_name]
            if len(p_shift_info) == 2 and isinstance(p_shift_info[1], str):
                p_shift_name = p_shift_info[1]
                particular_shift_details = shifts_map.get(p_shift_name)  # Get details by name

                if particular_shift_details:
                    # Create a temporary shift dictionary for the particular day, potentially adjusting minEmployees
                    # The structure requires a list of shift dicts
                    period_shifts = [{
                        "name": particular_shift_details.get('name'),
                        "start": particular_shift_details.get('start'),
                        "end": particular_shift_details.get('end'),
                        "minEmployees": p_shift_info[0]  # Use the count from particular_days
                    }]
                    periods.append({
                        "start_date": p_date.strftime("%Y-%m-%d"),
                        "end_date": p_date.strftime("%Y-%m-%d"),  # Particular day is a 1-day period
                        "shifts": period_shifts  # Apply only the specified particular shift
                    })
                else:
                    print(
                        f"Warning: Shift name '{p_shift_name}' in particular_days for date {p_date.strftime('%Y-%m-%d')} not found in shifts_data for schedule {self.id}. Skipping this particular day period.")

            else:
                print(
                    f"Warning: Invalid data format for particular day {p_date.strftime('%Y-%m-%m')} in particular_days for schedule {self.id}. Expected [count, 'ShiftName']. Skipping this day.")

            # 3. Update current_start_date to the day *after* the particular day
            current_start_date = p_date + timedelta(days=1)

        # 4. Add the final normal period *after* the last particular day (if any)
        if current_start_date <= end_d:
            periods.append({
                "start_date": current_start_date.strftime("%Y-%m-%d"),
                "end_date": end_d.strftime("%Y-%m-%d"),
                "shifts": standard_shifts  # Apply all standard shifts
            })

        return periods

    def create_payload(self):
        employee_data = {}
        services_data = {}
        shifts_data = {}
        employees_qs = Employee.objects.filter(id__in=self.employees)
        for employee_id in self.employees:
            employee = employees_qs.get(id=employee_id)
            employee_data[employee.id] = {
                "id": employee.id,
                "max_hours_per_day": employee.max_hours_per_day,
                "max_services_per_week": 99, # constraint solver will respect the hours parameters
                "max_hours_per_week": employee.max_hours_per_week,
                "max_hours_per_month": employee.max_hours_per_month
            }

        for shift_data in self.shifts_data:
            service_data = {
                "name": shift_data['name'],
                "minEmployees": shift_data['minEmployees'],
                "start": shift_data['start'],
                "end": shift_data['end']
            }
            services_data[shift_data['name']] = service_data



        # Create the payload
        payload = {
            "roster_id": self.id,
            "employees": employee_data,
            "shifts_data": services_data,
            "periods": self.generate_schedule_periods(),
            "free_days": self.free_days,
            "particular_days": self.particular_days

        }
        return payload



    def backup_to_json(self):
        """
        Backs up specified fields of the Schedule instance AND its related events
        to a JSON file.
        """
        if not hasattr(settings, 'SCHEDULES_BACKUP_DIR'):
             raise AttributeError("settings.BACKUP_DIR is not configured.")

        backup_dir = Path(settings.SCHEDULES_BACKUP_DIR) # Convert to pathlib.Path for easy handling

        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Error creating backup directory {backup_dir}: {e}")
            raise

        # Fields from the Schedule model itself
        fields_to_backup_schedule = [
            'id',
            'branch_id',
            'employees',
            'start_date',
            'end_date',
            'shift_data',
            'closing_days',
            'free_days',
            'can_modify',
            'processed', # Exclude schedule_events JSONField if ScheduleEvent model is canonical
        ]

        # Create the dictionary for the main Schedule data
        backup_data = {field: getattr(self, field) for field in fields_to_backup_schedule}

        # --- Backup Related ScheduleEvent objects ---
        related_events_data = []
        # Fetch all related ScheduleEvent objects
        # The 'events' is the related_name on the ForeignKey in ScheduleEvent
        related_events = self.events.all()

        # Define which fields to back up for each related event
        # Exclude the 'id' and the ForeignKey back to Schedule ('schedule_id' or 'schedule')
        fields_to_backup_event = [
             'date', 'start_time', 'end_time', 'employee', 'color' # Add other fields from ScheduleEvent, use _id for FKs
        ]

        for event in related_events:
            event_data = {}
            for field in fields_to_backup_event:
                 # Safely get the attribute value, handling potential errors
                 try:
                     value = getattr(event, field)
                     # Handle non-JSON serializable types like datetime if necessary
                     # For simple types and FK IDs this is usually fine.
                     # If you have complex types, you might need custom serialization here.
                     if isinstance(value, models.Model): # Should not happen if using _id
                         value = value.id
                     elif hasattr(value, 'isoformat'): # Basic datetime handling
                          value = value.isoformat()
                     event_data[field] = value
                 except AttributeError:
                      print(f"Warning: Field '{field}' not found on ScheduleEvent {event.id} during backup.")
                 except Exception as e:
                      print(f"Warning: Could not get field '{field}' from ScheduleEvent {event.id} during backup. Error: {e}")

            related_events_data.append(event_data)

        # Add the list of related events to the main backup dictionary
        backup_data['related_events_data'] = related_events_data


        # --- Write to file ---
        backup_filename = f"{self.id}.json"
        backup_path = backup_dir / backup_filename

        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                # Use json.dump with default handler for datetime if needed
                json.dump(backup_data, f, indent=4) # If you added complex types, you might need default=str or a custom handler

            print(f"Backup saved to {backup_path}")

        except (OSError, TypeError) as e:
             print(f"Error saving backup to {backup_path}: {e}")
             raise

        return backup_path

    def restore_from_json(self):
        """
        Restores the fields of the current Schedule instance and its related events
        from a JSON backup file.

        This method will DELETE all existing related events for this Schedule
        instance and recreate them from the backup data.
        """
        backup_dir = Path(settings.SCHEDULES_BACKUP_DIR) # Convert to pathlib.Path for easy handling
        backup_path = backup_dir / f"{self.id}.json"

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {backup_path}: {e}")
            raise
        except OSError as e:
             print(f"Error reading backup file {backup_path}: {e}")
             raise

        # --- Process the data for updating the *current* instance and related events ---
        # Use a transaction to ensure atomic database operations
        try:
            with transaction.atomic():
                # 1. Handle the main Schedule instance fields
                branch_id = backup_data.pop('branch_id', None)

                if branch_id is None:
                     raise KeyError(f"Backup data from {backup_path} is missing the required 'branch_id' field.")

                try:
                    branch_instance = Branch.objects.get(id=branch_id)
                    self.branch = branch_instance
                except Branch.DoesNotExist:
                    print(f"Branch with ID {branch_id} from backup {backup_path} does not exist in the database.")
                    raise Branch.DoesNotExist(f"Cannot restore Schedule {self.id}: Branch ID {branch_id} not found.")
                except Exception as e:
                     print(f"An unexpected error occurred while looking up Branch ID {branch_id} from {backup_path} for Schedule {self.id}: {e}")
                     raise

                # Ignore the original 'id' field
                backup_data.pop('id', None)
                # Ignore the 'related_events_data' key as we handle it separately
                related_events_data = backup_data.pop('related_events_data', None)
                # Ignore the original schedule_events JSONField if ScheduleEvent model is canonical
                backup_data.pop('schedule_events', None)


                # Update remaining fields on the current instance (self)
                for field_name, value in backup_data.items():
                    if hasattr(self, field_name):
                         try:
                             setattr(self, field_name, value)
                         except Exception as e:
                              print(f"Warning: Could not set field '{field_name}' on Schedule {self.id} from backup {backup_path}. Error: {e}")
                    else:
                         print(f"Warning: Field '{field_name}' found in backup {backup_path} but not on Schedule model {self.id}. Skipping.")

                # Save the updated Schedule instance
                self.save()
                print(f"Main Schedule {self.id} fields updated.")


                # --- Restore Related ScheduleEvent objects ---
                if related_events_data is not None and isinstance(related_events_data, list):
                    # CRITICAL: Delete existing related events for this schedule
                    # This ensures a clean restore state matching the backup
                    print(f"Deleting existing related events for Schedule {self.id}...")
                    self.events.all().delete() # Using the related_name 'events'

                    print(f"Restoring {len(related_events_data)} related events from backup...")
                    restored_event_ids = [] # Optional: keep track of restored event IDs if needed
                    for i, event_backup_data in enumerate(related_events_data):
                        try:
                            # Create a dictionary for the new event instance
                            new_event_data = {}
                            # Set the ForeignKey to the current Schedule instance
                            new_event_data['schedule'] = self

                            # Copy data from the backup, handling potential FK lookups
                            for field_name, value in event_backup_data.items():
                                 # Handle FKs like employee_id - need to fetch the object
                                 if field_name == 'employee':
                                     try:
                                         employee = Employee.objects.get(id=value)
                                         new_event_data[field_name] = employee
                                     except Employee.DoesNotExist:
                                         print(f"Employee with ID {value} from backup for Schedule {self.id} event #{i+1} does not exist in the database. Skipping.")
                                     except Exception as e:
                                          print(f"An unexpected error occurred while looking up Employee ID {value} from {backup_path} for Schedule {self.id} event #{i+1}: {e}")
                                          raise


                                 elif field_name == 'id':
                                      # Ignore the original event ID
                                      pass
                                 elif field_name == 'schedule' or field_name == 'schedule_id':
                                      # Ignore the old schedule link
                                      pass
                                 else:
                                      # Handle regular fields (CharField, JSONField, etc.)
                                      if hasattr(ScheduleEvent, field_name): # Check if the field exists on the target model
                                           try:
                                                new_event_data[field_name] = value
                                           except Exception as e:
                                                print(f"Warning: Could not set field '{field_name}' on new ScheduleEvent for Schedule {self.id} event #{i+1} from backup. Error: {e}. Skipping field.")
                                      else:
                                           print(f"Warning: Field '{field_name}' found in event backup data for Schedule {self.id} event #{i+1} but not on ScheduleEvent model. Skipping.")


                            # Create the new ScheduleEvent instance
                            # Use .objects.create within the transaction
                            new_event = ScheduleEvent.objects.create(**new_event_data)
                            restored_event_ids.append(new_event.id)
                            # print(f"Created ScheduleEvent {new_event.id}") # Optional detail logging

                        except ValidationError as e:
                            print(f"Data validation error creating ScheduleEvent for Schedule {self.id} event #{i+1}: {e}")
                            # Depending on severity, you might want to raise here or continue and log
                            # For now, just print and continue to try the next event
                        except Exception as e:
                            print(f"An unexpected error occurred creating ScheduleEvent for Schedule {self.id} event #{i+1} from backup data: {event_backup_data}. Error: {e}")
                            # Again, decide if this should stop the whole transaction or just skip this event


                    print(f"Finished restoring related events for Schedule {self.id}. Created {len(restored_event_ids)} events.")
                elif related_events_data is not None:
                     print(f"Warning: 'related_events_data' key in backup {backup_path} was not a list. Skipping related event restore.")
                else:
                     print(f"No 'related_events_data' found in backup {backup_path} for Schedule {self.id}. No related events to restore.")


                print(f"Successfully restored/updated Schedule {self.id} and related events from {backup_path}")

                # Return the updated instance (self)
                return self

        except ValidationError as e:
             print(f"Data validation error during restore from {backup_path} for Schedule {self.id}: {e}")
             raise
        except KeyError as e:
             print(f"Missing required data field during restore from {backup_path} for Schedule {self.id}: {e}")
             raise
        except (Branch.DoesNotExist, ScheduleEvent.DoesNotExist, Employee.DoesNotExist, transaction.TransactionManagementError) as e:
             # Catch DoesNotExist for related models if you added lookups
             print(f"A related object lookup failed during restore: {e}")
             raise
        except Exception as e:
             print(f"An unexpected error occurred during the restore process for Schedule {self.id} from {backup_path}: {e}")
             raise

    def get_settings(self):
        employees_data=[]
        employees_scontrino_medio = []
        all_employees = Employee.objects.filter(branch=self.branch)
        for employee_obj in all_employees :
            try:
                emp_medium_receipt_number = employee_obj.get_total_medium_receipts_number()
                emp_medium_receipt_value = employee_obj.get_total_medium_sales()
            except Employee.DoesNotExist:
                employees_scontrino_medio.append(None)
            employees_data.append({
                "id": employee_obj.id,
                'fullName': employee_obj.get_full_name(),
                'mediumReceiptsNumber': emp_medium_receipt_number, # num scontrini
                'mediumReceiptSale': emp_medium_receipt_value, # valore medio scontrini
                'role': employee_obj.role,
                'class': employee_obj.skill_class,
            })

        shifts_data = []
        for shift in self.shifts_data:
            shifts_data.append({
                "id": shift["id"],
                "name": shift["name"],
                "start": shift["start"],
                "end": shift["end"],
                "minEmployees": shift["minEmployees"],
            })


        obj = {
            "employees": employees_data,
            "savedShift": shifts_data,
        }
        return obj


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

    COLORS = [
            '#F44336', '#E91E63', '#9C27B0', '#673AB7',
            '#3F51B5', '#2196F3', '#03A9F4', '#00BCD4',
            '#009688', '#4CAF50', '#8BC34A', '#CDDC39',
            '#FFEB3B', '#FFC107', '#FF9800', '#FF5722'
            ]

    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, related_name="events")
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name="schedule_events")
    date = models.CharField(default="", max_length=100)
    start_time = models.CharField(default="", max_length=100)
    end_time = models.CharField(default="", max_length=100)
    color = models.CharField(default="", max_length=100)

    def format_json(self):
        data= {
            'id': self.id,
            'employeeId': self.employee.id,
            'date': self.date,
            'startTime': self.start_time,
            'endTime': self.end_time,
            'color': self.color,
        }
        return data

