from django import forms

from events.models import Event


class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ('is_deleted','deleted_at', 'created_at', 'updated_at')