from rest_framework import serializers
from .models import Supplier,SaleItem,Transaction, Product,Asset,  Customer,Bill, Bank,ProductStock,StockBill,Unit



class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name']
class SupplierAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields ='__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductStockViewSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), source='supplier', write_only=True)

    class Meta:
        model = ProductStock
        fields = ['id', 'product', 'supplier', 'quantity', 'supplier_price_per_unit', 'date_purchased', 'product_id', 'supplier_id']

class ProductStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStock
        fields = '__all__'


        

class ProductStockSearchSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    supplier = SupplierSerializer()

    class Meta:
        model = ProductStock
        fields = ['id', 'product', 'supplier', 'quantity', 'supplier_price_per_unit', 'date_purchased']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['phone_number', 'name']

#=========================POS billing===============
class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = '__all__'
class BillSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Bill
        fields = '__all__'
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        bill = Bill.objects.create(**validated_data)
        for item_data in items_data:
            SaleItem.objects.create(bill=bill, **item_data)
        return bill

#=========================POS billing end===============

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'



#============stock bill ============




class StockBillSerializer(serializers.ModelSerializer):
    items = ProductStockSerializer(many=True)

    class Meta:
        model = StockBill
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        stock_bill = StockBill.objects.create(**validated_data)
        for item_data in items_data:
            # Remove 'stock_bill' from item_data if it exists
            item_data.pop('stock_bill', None)
            ProductStock.objects.create(stock_bill=stock_bill, **item_data)
        return stock_bill




#============stock bill end===========


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'




#=============assets ==============
class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'
class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'
class ViewTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        depth=2
        model = Transaction
        fields = '__all__'



#==========liability update===============
class LiabilityBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ['id', 'total_paid', 'total_due']  # Only allow these fields to be updated
