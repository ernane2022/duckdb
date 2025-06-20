# Generated by Django 4.2.7 on 2025-06-17 21:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SalesRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('customer_id', models.IntegerField()),
                ('product_name', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
                ('sale_date', models.DateTimeField()),
                ('region', models.CharField(max_length=50)),
                ('salesperson', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'indexes': [models.Index(fields=['customer_id'], name='benchmark_a_custome_fc5fba_idx'), models.Index(fields=['category'], name='benchmark_a_categor_479738_idx'), models.Index(fields=['sale_date'], name='benchmark_a_sale_da_8975ed_idx'), models.Index(fields=['region'], name='benchmark_a_region_dd1cf0_idx')],
            },
        ),
    ]
