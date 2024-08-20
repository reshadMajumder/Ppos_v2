from django.urls import path
from authentication.views import login_view,logout_view
from shop.views import view_assets,add_asset,update_asset,delete_asset,add_transaction, bill_list,create_bill,search_products,product_list,search_product_stock, supplier_list_create, bank_list_create,product_stock_list,add_or_list_stock,unit_list_create,dashboard_summary,delete_transaction ,update_liability,view_liability

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),


    path('suppliers/', supplier_list_create, name='supplier_list_create'),
    path('products/', product_list, name='product-list'),
    path('stocks/', product_stock_list,name='product-stock-list'),
    path('stocks/search/', search_product_stock, name='search-product-stock'),

    path('search-products/', search_products, name='search_products'),
    path('bills/', create_bill, name='create_bill'),
    path('bills-recipt/', bill_list, name='bills_recipt'),
    path('banks/', bank_list_create, name='bank_list_create'),
    path('stock-bill/', add_or_list_stock, name='stock_bill_list_create'),
    path('units/', unit_list_create, name='unit_list_create'),
    path('dashboard/', dashboard_summary, name='dashboard_summary'),

    path('assets/', view_assets, name='view_assets'),
    path('assets/add/', add_asset, name='add_asset'),
    path('assets/<int:pk>/update/', update_asset, name='update_asset'),
    path('assets/<int:pk>/delete/', delete_asset, name='delete_asset'),
    path('transactions/', add_transaction, name='add_transaction'),
    path('transactions/<int:pk>/',delete_transaction, name='delete_transaction'),
    
    path('liability/<int:pk>/update/', update_liability, name='update_liability'),
    path('liability/', view_liability, name='update_liability'),


]



#path('products/', product_list_create, name='product_list_create'),
    # # path('supplier-products/', supplier_product_list_create, name='supplier_product_list_create'),
    # path('customers/', customer_list_create, name='customer_list_create'),
    # path('sales/', sale_list_create, name='sale_list_create'),
      # path('product-stock/', product_stock_list, name='product-stock-list'),
    # path('sales/', sale_list),
