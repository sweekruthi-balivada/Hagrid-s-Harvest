Steps to run Operational Database GUI App
1. Please make sure you are connected to SJSU school network via Cisco Any connect
2. Update 'ecommerce.ini' to the remote ini file in Windows.py file.
3. Open GUIApp.ipynb
4. Restart Kernel and run all cells
5. Explore the operational db GUI app.


The tables are:

category: stores information about the categories of products available on the website.
sub_category: stores information about subcategories of products.
reviews: stores information about product reviews, including ratings, descriptions, and the customer and product IDs associated with each review.
products: stores information about products, including their names, prices, stock availability, and the category and subcategory IDs they belong to.
payment: stores information about payments made for orders, including the payment mode and amount, as well as the order ID associated with each payment.
orders: stores information about orders placed by customers, including the day of the week they were placed, the order date, and the customer ID associated with each order.
order_details: stores information about the details of each order, including the quantity of each product ordered and the product and order IDs associated with each order detail.
customer_address: stores information about customer addresses, including the apartment number, city, state, PIN code, and street name associated with each address, as well as the customer ID associated with each address.
customer: stores information about customers, including their first and last names, email addresses, ages and age ranges, genders, phone numbers, and dates of birth.