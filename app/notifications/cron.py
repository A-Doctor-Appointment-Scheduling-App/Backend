# notifications/cron.py
from django_cron import CronJobBase, Schedule
from .views import send_appointment_reminders

class SendRemindersCronJob(CronJobBase):
    RUN_EVERY_MINS = 60  # Run every hour (adjust as needed)

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'notifications.send_reminders_cron_job'  # Unique identifier for the cron job

    def do(self):
        # Call the function to send reminders
        send_appointment_reminders()