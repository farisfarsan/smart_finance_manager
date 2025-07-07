from django.db import models
from django.contrib.auth.models import User

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    platform = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_fetched = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.platform} - ₹{self.amount:.2f} on {self.date_fetched}"

    class Meta:
        ordering = ['-date_fetched']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
