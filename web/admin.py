from django.contrib import admin
from django.shortcuts import redirect
from .models import Partner, Post, Review, Ticket, Joke, Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'phone')
    list_editable = ('is_processed',)

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'phone')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'text')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'is_published', 'created_at')
    list_filter = ('is_published', 'rating')
    search_fields = ('name', 'text')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('manage_tickets')

@admin.register(Joke)
class JokeAdmin(admin.ModelAdmin):
    list_display = ('name', 'text', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('name', 'text')

