# Generated by Django 4.2.2 on 2023-08-11 05:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0002_alter_product_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="paid_price",
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="product",
            name="stock_quantity",
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="ConsumerDebt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("type", models.SmallIntegerField(choices=[(-1, -1), (1, 1)])),
                ("price", models.PositiveBigIntegerField()),
                (
                    "consumer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="debts",
                        to="shop.consumer",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="debts",
                        to="shop.order",
                    ),
                ),
            ],
            options={
                "db_table": "consumer_debt",
            },
        ),
    ]