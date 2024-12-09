from django.db import models

class MailMessage(models.Model):
    subject = models.CharField(max_length=255, help_text="The subject of the email.")
    body = models.TextField(help_text="The main content of the email.")
    attachment = models.FileField(upload_to='mail_attachments/', blank=True, null=True, help_text="Optional file attachment.")
    sender_email = models.EmailField(help_text="Email address of the sender.")
    recipient_emails = models.TextField(help_text="Comma-separated list of recipient email addresses.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.subject
