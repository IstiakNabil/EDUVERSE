from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from django.core.mail import send_mail
from .models import TeacherApplication


# ---------- Bulk actions (Actions dropdown) ----------
@admin.action(description="Approve selected applications")
def approve_applications(modeladmin, request, queryset):
    updated = queryset.exclude(status=TeacherApplication.Status.APPROVED) \
                      .update(status=TeacherApplication.Status.APPROVED)
    if updated:
        messages.success(request, f"Approved {updated} application(s).")
    else:
        messages.info(request, "No applications needed approval.")

@admin.action(description="Reject selected applications")
def reject_applications(modeladmin, request, queryset):
    updated = queryset.exclude(status=TeacherApplication.Status.REJECTED) \
                      .update(status=TeacherApplication.Status.REJECTED)
    if updated:
        messages.success(request, f"Rejected {updated} application(s).")
    else:
        messages.info(request, "No applications needed rejection.")


@admin.register(TeacherApplication)
class TeacherApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "expertise",
        "years_experience",
        "status",
        "submitted_at",
        "user",
        "quick_actions",   # ← one-click buttons
    )
    list_filter = ("status", "submitted_at", "expertise")
    search_fields = ("full_name", "email", "expertise")
    readonly_fields = ("user", "submitted_at")
    actions = [approve_applications, reject_applications]

    # ---------- One-click buttons: Approve / Reject ----------
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:pk>/approve/",
                self.admin_site.admin_view(self.process_approve),
                name="teachers_teacherapplication_approve",
            ),
            path(
                "<int:pk>/reject/",
                self.admin_site.admin_view(self.process_reject),
                name="teachers_teacherapplication_reject",
            ),
        ]
        # Put our custom URLs before the default ones
        return custom + urls

    def process_approve(self, request, pk, *args, **kwargs):
        app = get_object_or_404(TeacherApplication, pk=pk)
        if app.status != TeacherApplication.Status.APPROVED:
            app.status = TeacherApplication.Status.APPROVED
            app.save(update_fields=["status"])
            messages.success(request, f"Approved {app.full_name}.")

            send_mail(
                subject="Your Teacher Application has been Approved",
                message=f"Dear {app.full_name},\n\n"
                        "Congratulations! Your teacher application has been approved. "
                        "You can now log in and start contributing as a teacher.\n\n"
                        "Best regards,\nEduverse Team",
                from_email="noreply@eduverse.com",  # replace with DEFAULT_FROM_EMAIL
                recipient_list=[app.user.email],
                fail_silently=True,
            )

        else:
            messages.info(request, f"{app.full_name} is already approved.")
        return redirect("admin:teachers_teacherapplication_changelist")

    def process_reject(self, request, pk, *args, **kwargs):
        app = get_object_or_404(TeacherApplication, pk=pk)
        if app.status != TeacherApplication.Status.REJECTED:
            app.status = TeacherApplication.Status.REJECTED
            app.save(update_fields=["status"])
            messages.success(request, f"Rejected {app.full_name}.")
            send_mail(
                subject="Your Teacher Application has been Rejected",
                message=f"Dear {app.full_name},\n\n"
                        "We regret to inform you that your teacher application has been rejected. "
                        "Thank you for your interest in joining us. "
                        "You may reapply in the future.\n\n"
                        "Best regards,\nEduverse Team",
                from_email="noreply@eduverse.com",
                recipient_list=[app.user.email],
                fail_silently=True,
            )
        else:
            messages.info(request, f"{app.full_name} is already rejected.")
        return redirect("admin:teachers_teacherapplication_changelist")

    @admin.display(description="Quick actions")
    def quick_actions(self, obj):
        # Only show buttons when status is pending
        if obj.status == TeacherApplication.Status.PENDING:
            approve_url = reverse("admin:teachers_teacherapplication_approve", args=[obj.pk])
            reject_url = reverse("admin:teachers_teacherapplication_reject", args=[obj.pk])
            return format_html(
                '<a class="button" href="{}">Approve</a>&nbsp;'
                '<a class="button" style="color:#b32d2e" href="{}">Reject</a>',
                approve_url,
                reject_url,
            )
        return "—"
