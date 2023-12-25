Steps to run Analytical Database GUI App
1. Please make sure you are connected to SJSU school network via Cisco Any connect
2. Update 'ecommerce_wh.ini' to the remote ini file in Windows.py file.
3. Open GUIApp.ipynb
4. Restart Kernel and run all cells
5. Explore the analytical db GUI app.


The tables are:

1. `customer_address_d`:
   - Columns:
     - `AddressId` (integer): Unique identifier for each address.
     - `AptNo` (varchar): Optional apartment number associated with the address.
     - `City` (varchar): Name of the city where the address is located.
     - `State` (varchar): Name of the state where the address is located.
     - `PinCode` (integer): Postal code or ZIP code of the address.
     - `StreetName` (varchar): Name of the street where the address is located.
   - Primary Key: `AddressId`

2. `customer_d`:
   - Columns:
     - `CustomerId` (integer): Unique identifier for each customer.
     - `FirstName` (varchar): First name of the customer.
     - `LastName` (varchar): Last name of the customer.
     - `Email` (varchar): Email address of the customer.
     - `Age` (integer): Age of the customer.
     - `Gender` (char): Gender of the customer (represented by a single character, e.g., 'M' or 'F').
     - `Phone` (varchar): Phone number of the customer.
   - Primary Key: `CustomerId`

3. `order_d`:
   - Columns:
     - `OrderId` (integer): Unique identifier for each order.
     - `DayofWeek` (integer): Numeric representation of the day of the week when the order was placed.
     - `OrderDate` (date): Date when the order was placed.
   - Primary Key: `OrderId`

4. `product_d`:
   - Columns:
     - `ProductId` (integer): Unique identifier for each product.
     - `ProductName` (varchar): Name of the product.
     - `ProductPrice` (decimal): Price of the product.
     - `InStock` (char): Indicates whether the product is in stock (represented by a single character, e.g., 'Y' or 'N').
     - `CategoryId` (integer): Unique identifier for the category of the product.
     - `CategoryName` (varchar): Name of the category.
     - `SubCategoryId` (integer): Unique identifier for the subcategory of the product.
     - `SubCategoryName` (varchar): Name of the subcategory.
   - Primary Key: `ProductId`

5. `review`:
   - Columns:
     - `Rating` (integer): Numeric rating given to a product in a review.
     - `Description` (varchar): Optional description or comment associated with the review.
     - `ProductId` (integer): Identifier of the product being reviewed.
     - `CustomerId` (integer): Identifier of the customer who provided the review.
   - Foreign Keys: `ProductId` references `product_d(ProductId)`, `CustomerId` references `customer_d(CustomerId)`

6. `sales`:
   - Columns:
     - `Quantity` (integer): Quantity of products sold in a particular sale.
     - `Amount` (float): Total amount of the sale.
     - `AddressId` (integer): Identifier of the customer address associated with the sale.
     - `OrderId` (integer): Identifier of the order to which the sale belongs.
     - `CustomerId` (integer): Identifier of the customer who made the purchase.
     - `ProductId` (integer): Identifier of the product being sold.
   - Foreign Keys: `AddressId` references `customer_address_d(AddressId)`, `OrderId` references `order_d(OrderId)`, `CustomerId` references `customer_d(CustomerId)`, `ProductId` references `product_d

(ProductId)`