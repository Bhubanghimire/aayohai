from django.contrib import admin

from events.forms import EventAdminForm
from events.models import Event, EventCategory, FeatureEvent, EventPrice, TermsConditions


# Register your models here.
@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at", "updated_at")


# @admin.register(Event)
# class EventAdmin(admin.ModelAdmin):
#     list_display = ("id", "title","start_date", "event_date", "created_at", "updated_at")
#     list_filter = ("category",)


@admin.register(FeatureEvent)
class FeatureEventAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "start_date", "end_date", "created_at", "updated_at")


class EventPriceInline(admin.StackedInline):
    model = EventPrice
    extra = 1  # No extra empty form
    # max_num = 1


class EventTermsInline(admin.StackedInline):
    model = TermsConditions
    extra = 1
    # max_num = 1




@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     if not obj:  # Adding
    #         form.base_fields.pop('approved')  # Hide the field
    #     return form
    inlines = [EventPriceInline, EventTermsInline]


# @admin.register(EventPrice)
# class EventPriceAdmin(admin.ModelAdmin):
#     list_display = ("id", "event", "title", "price", "created_at", "updated_at")
#
#
# @admin.register(TermsConditions)
# class TermsConditionsAdmin(admin.ModelAdmin):
#     list_display = ("id", "event", "title", "created_at", "updated_at")
