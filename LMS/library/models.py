from django.db import models
from datetime import timedelta
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=200)
    authors = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True)
    publisher = models.CharField(max_length=100)
    page_count = models.IntegerField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Member(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    outstanding_debt = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(null=True, blank=True)
    fee = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def is_overdue(self):
        if self.return_date:
            overdue_days = (self.return_date - self.issue_date).days - 14  # 14-day debt period
            return max(0, overdue_days)
        return 0

    def calculate_fee(self):
        overdue_days = self.is_overdue()
        return overdue_days * 5  # Assuming Rs. 5 per day as fee
