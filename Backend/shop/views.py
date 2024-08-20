
# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Asset,Supplier,Bill, Product, Customer, Bank,ProductStock,StockBill,Unit,Transaction
from .serializers import AssetSerializer,TransactionSerializer,ProductStockSearchSerializer, StockBillSerializer,SupplierAddSerializer,ProductStockViewSerializer, BillSerializer,ProductSerializer, CustomerSerializer, BankSerializer,UnitSerializer,ViewTransactionSerializer,LiabilityBillSerializer
from django.db.models import Q,Sum,F,DecimalField
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

# this one adds a new supplier and views allsupplier
@api_view(['GET', 'POST'])
def supplier_list_create(request):
    if request.method == 'GET':
        suppliers = Supplier.objects.all()
        serializer = SupplierAddSerializer(suppliers, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = SupplierAddSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



#=============stock ===================
#create new product and view all the available products
@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)




#search for adding in table for sale
@api_view(['GET'])
def search_products(request):
    query = request.query_params.get('search', '')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.none()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

#search products from the stock available. ignores 0 qty products
@api_view(['GET'])
def search_product_stock(request):
    query = request.GET.get('query', '')
    if query:
        stocks = ProductStock.objects.filter(
            quantity__gt=0
        ).filter(
            Q(product__name__icontains=query) 
        )
    else:
        stocks = ProductStock.objects.filter(quantity__gt=0)
    
    serializer = ProductStockSearchSerializer(stocks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#==============stock end=================




#========================billing section=========
#handels the pos billing funtcionality ony post
@api_view(['POST'])
def create_bill(request):
    serializer = BillSerializer(data=request.data)
    if serializer.is_valid():
        bill = serializer.save()

        # Collect items to be deducted
        items_to_deduct = request.data.get('items', [])

        try:
            with transaction.atomic():
                for item in items_to_deduct:
                    product_id = item.get('product')
                    quantity = item.get('quantity')

                    # Fetch all ProductStock entries for the given product
                    product_stocks = ProductStock.objects.filter(product_id=product_id).order_by('date_purchased')

                    total_quantity = sum([product_stock.quantity for product_stock in product_stocks])

                    if quantity > total_quantity:
                        return Response({'error': f'Not enough stock for product {product_id}'}, status=status.HTTP_400_BAD_REQUEST)

                    for product_stock in product_stocks:
                        if quantity <= 0:
                            break

                        if product_stock.quantity > 0:
                            if product_stock.quantity >= quantity:
                                product_stock.quantity -= quantity
                                product_stock.save()
                                quantity = 0
                            else:
                                quantity -= product_stock.quantity
                                product_stock.quantity = 0
                                product_stock.save()

                # Update the bank balance

                bank = Bank.objects.get(id=bill.payment_method)
                if bank:
                    bank.balance += bill.total_paid
                    bank.save()
                
        except ProductStock.DoesNotExist:
            return Response({'error': 'ProductStock entry not found'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
#view all the bills
@api_view (['GET'])
def bill_list(request):
    if request.method == 'GET':
        bills = Bill.objects.all()
        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data)

#========================billing section end=========

#================== stock bill start==================================
#view available product stock quantity 
@api_view(['GET', 'POST'])
def product_stock_list(request):
    if request.method == 'GET':
        stocks = ProductStock.objects.filter(quantity__gt=0)
        serializer = ProductStockViewSerializer(stocks, many=True)
        return Response(serializer.data)
    
    

@api_view(['GET', 'POST'])
def add_or_list_stock(request):
    if request.method == 'POST':
        serializer = StockBillSerializer(data=request.data)
        if serializer.is_valid():
            stock_bill = serializer.save()

            # Optionally, update bank balance if payment is made via bank
            if stock_bill.payment_method:
                bank = Bank.objects.get(id=stock_bill.payment_method)
                if bank:
                    if bank.balance < stock_bill.total_paid:
                        stock_bill.delete()  # Remove the created stock bill
                        return Response({'error': 'Insufficient bank balance'}, status=status.HTTP_400_BAD_REQUEST)
                    bank.balance -= stock_bill.total_paid
                    bank.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        stock_bills = StockBill.objects.all()
        serializer = StockBillSerializer(stock_bills, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



#================== stock bill end==================================


#create customers and get customers
@api_view(['GET', 'POST'])
def customer_list_create(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





#view add update delete all the bank
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def bank_list_create(request, pk=None):
    if request.method == 'GET':
        if pk:
            try:
                bank = Bank.objects.get(pk=pk)
                serializer = BankSerializer(bank)
                return Response(serializer.data)
            except Bank.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            banks = Bank.objects.all()
            serializer = BankSerializer(banks, many=True)
            return Response(serializer.data)
    elif request.method == 'POST':
        serializer = BankSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PUT':
        try:
            bank = Bank.objects.get(pk=pk)
        except Bank.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BankSerializer(bank, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            bank = Bank.objects.get(pk=pk)
        except Bank.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        bank.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



#view add update delete all the unit
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def unit_list_create(request, pk=None):
    if request.method == 'GET':
        if pk:
            try:
                unit = Unit.objects.get(pk=pk)
                serializer = UnitSerializer(unit)
                return Response(serializer.data)
            except Unit.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            units = Unit.objects.all()
            serializer = UnitSerializer(units, many=True)
            return Response(serializer.data)
    elif request.method == 'POST':
        serializer = UnitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PUT':
        try:
            unit = Unit.objects.get(pk=pk)
        except Unit.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UnitSerializer(unit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            unit = Unit.objects.get(pk=pk)
        except Unit.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        unit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET'])
def dashboard_summary(request):
    today = timezone.now().date()

    # Total sold amount for today
    total_sold_today = Bill.objects.filter(
        created_at__day=today.day,
        created_at__month=today.month,
        created_at__year=today.year
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Total sold amount for this month
    total_sold_month = Bill.objects.filter(
        created_at__month=today.month,
        created_at__year=today.year
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Total sold amount for this year
    total_sold_year = Bill.objects.filter(
        created_at__year=today.year
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Total sold amount overall
    total_sold_total = Bill.objects.aggregate(total=Sum('total_amount'))['total'] or 0

    # Total profit for today
    total_profit_today = Bill.objects.filter(
        created_at__day=today.day,
        created_at__month=today.month,
        created_at__year=today.year
    ).aggregate(profit=Sum(F('total_amount') - F('total_cost')))['profit'] or 0

    # Total profit for this month
    total_profit_month = Bill.objects.filter(
        created_at__month=today.month,
        created_at__year=today.year
    ).aggregate(profit=Sum(F('total_amount') - F('total_cost')))['profit'] or 0

    # Total profit for this year
    total_profit_year = Bill.objects.filter(
        created_at__year=today.year
    ).aggregate(profit=Sum(F('total_amount') - F('total_cost')))['profit'] or 0

    # Total profit overall
    total_profit_total = Bill.objects.aggregate(profit=Sum(F('total_amount') - F('total_cost')))['profit'] or 0

    # Total stock amount
    total_stock_amount = ProductStock.objects.aggregate(stock_value=Sum(F('quantity') * F('supplier_price_per_unit')))['stock_value'] or 0
    data={
        'total_sold_today': total_sold_today,
        'total_sold_month': total_sold_month,
        'total_sold_year': total_sold_year,
        'total_sold_total': total_sold_total,
        'total_profit_today': total_profit_today,
        'total_profit_month': total_profit_month,
        'total_profit_year': total_profit_year,
        'total_profit_total': total_profit_total,
        'total_stock_amount': total_stock_amount,
    }
    return Response(data)


#add view edit assets

@api_view(['GET'])
def view_assets(request):
    assets = Asset.objects.all()
    serializer = AssetSerializer(assets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Add Asset
@api_view(['POST'])
def add_asset(request):
    serializer = AssetSerializer(data=request.data)
    if serializer.is_valid():
        # Retrieve the selected bank instance
        bank = Bank.objects.get(id=request.data['bank'])
        
        # Check if the bank has enough balance
        if bank.balance < serializer.validated_data['amount']:
            return Response({'error': 'Insufficient balance in the selected bank.'}, status=status.HTTP_400_BAD_REQUEST)

        # Save the asset since the bank has enough balance
        asset = serializer.save()

        # Deduct the asset amount from the bank's balance
        bank.balance -= asset.amount
        bank.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Update Asset
@api_view(['PUT'])
def update_asset(request, pk):
    #need to roll back previous money then update
    try:
        asset = Asset.objects.get(pk=pk)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AssetSerializer(asset, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete Asset
@api_view(['DELETE'])
def delete_asset(request, pk):
    try:
        asset = Asset.objects.get(pk=pk)
    except Asset.DoesNotExist:
        return Response({'error': 'Asset not found'}, status=status.HTTP_404_NOT_FOUND)

    asset.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)




@api_view(['POST','GET'])
def add_transaction(request):
    if request.method=="POST":
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            transaction_type = serializer.validated_data['transaction_type']
            amount = serializer.validated_data['amount']
            bank = serializer.validated_data['bank']

            # Update bank balance based on transaction type
            if transaction_type == 'ADD':
                bank.balance += amount
            else:
                if bank.balance >= amount:
                    bank.balance -= amount
                else:
                    return Response(
                        {"error": "Insufficient funds in the selected bank."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            bank.save()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method=="GET":
        transaction=Transaction.objects.all()
        serializer = ViewTransactionSerializer(transaction, many=True)
        return Response(serializer.data)
    
@api_view(['DELETE'])
def delete_transaction(request, pk):
    try:
        transaction = Transaction.objects.get(pk=pk)
        bank = transaction.bank  # Get the associated bank
        
        # Roll back the bank's balance based on the transaction type
        if transaction.transaction_type == 'ADD':
            bank.balance -= transaction.amount
        else:
            bank.balance += transaction.amount
        
        bank.save()  # Save the updated bank balance
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Transaction.DoesNotExist:
        return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)






#==================Liabilities====================
@api_view(['PATCH','GET'])
def update_liability(request, pk):
    if request.method=="PATCH":
        try:
            liability = Bill.objects.get(pk=pk)
            serializer = LiabilityBillSerializer(liability, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Bill.DoesNotExist:
            return Response({'error': 'Liability not found'}, status=status.HTTP_404_NOT_FOUND)
        
@api_view(['PATCH','GET'])
def view_liability(request):

    if request.method=="GET": 
        liabilities = Bill.objects.filter(total_due__gt=0)
        serializer = BillSerializer(liabilities, many=True)
        return Response(serializer.data)




