from django.apps import AppConfig


class ApplicationTrackingConfig(AppConfig):
    """
    Epic 5: Job Application Tracking with Resume Used
    Configuration for the application tracking Django app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'application_tracking'
    verbose_name = 'Application Tracking'
    
    def ready(self):
        """Import signals when the app is ready."""
        try:
            import application_tracking.signals  # noqa
        except ImportError:
            pass
