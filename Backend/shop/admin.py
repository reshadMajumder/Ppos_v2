from django.contrib import admin
from .models import Supplier,Asset, Product, Customer,Bill, SaleItem, ProductStock,Bank,StockBill,Unit,Transaction

# Register your models here.

admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(SaleItem)
admin.site.register(ProductStock)
admin.site.register(Bill)
admin.site.register(Bank)
admin.site.register(StockBill)
admin.site.register(Unit)
admin.site.register(Asset)
admin.site.register(Transaction)