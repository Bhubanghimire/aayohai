from django.contrib import admin
from events.models import Event, EventCategory, FeatureEvent, EventPrice, TermsConditions


# Register your models here.
@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at", "updated_at")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title","start_date", "event_date", "created_at", "updated_at")
    list_filter = ("category",)


@admin.register(FeatureEvent)
class FeatureEventAdmin(admin.ModelAdmin):
    list_display = ("id", "event","start_date","end_date",  "created_at", "updated_at")


@admin.register(EventPrice)
class EventPriceAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "title", "price", "created_at", "updated_at")


@admin.register(TermsConditions)
class TermsConditionsAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "title", "created_at", "updated_at")