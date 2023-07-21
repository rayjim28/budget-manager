# Generated by Django 4.2.1 on 2023-07-20 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_personalbudget_budget_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenseitem',
            name='item_category',
            field=models.CharField(choices=[('🏠', 'Housing'), ('🏥', 'Medical'), ('🛒', 'Groceries'), ('🚙', 'Car')], max_length=2),
        ),
    ]
