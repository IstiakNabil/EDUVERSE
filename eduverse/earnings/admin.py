# earnings/admin.py
from django.contrib import admin
from .models import Earning, Withdrawal

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'amount', 'status', 'requested_at', 'processed_at')
    list_filter = ('status',)
    list_editable = ('status',) # Allows you to change the status directly in the list
    search_fields = ('teacher__username',)