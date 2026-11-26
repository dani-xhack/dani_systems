import re
from django.contrib import admin
from django.shortcuts import redirect
from .models import Partner, Post, Review, Ticket, Joke, HexJoke, Lead

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
    list_display = ('title', 'keywords', 'created_at', 'is_published')
    list_editable = ('is_published',)
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
    list_editable = ('is_published',)

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(text__startswith='[HEX]')

@admin.register(HexJoke)
class HexJokeAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview_text', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('name', 'text')
    list_editable = ('is_published',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(text__startswith='[HEX]')

    @admin.display(description='Текст анекдота')
    def preview_text(self, obj):
        raw = obj.text[5:].strip()
        clean = re.sub(r'[^0-9a-fA-F]', '', raw)
        try:
            return bytes.fromhex(clean).decode('utf-8')
        except Exception:
            return raw[:60]

    def save_model(self, request, obj, form, change):
        raw = obj.text.strip()
        if raw.startswith('[HEX]'):
            raw = raw[5:].strip()
        clean_hex = re.sub(r'\s+', '', raw)
        if re.fullmatch(r'(?:[0-9a-fA-F]{2})+', clean_hex):
            hex_str = ' '.join(clean_hex[i:i+2].lower() for i in range(0, len(clean_hex), 2))
        else:
            b = raw.encode('utf-8')
            hex_str = ' '.join(f'{x:02x}' for x in b)
        obj.text = '[HEX]' + hex_str
        super().save_model(request, obj, form, change)
