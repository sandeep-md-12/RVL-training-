import uuid 
import datetime

class Product :
    def __init__(self, product_id , name , price , stock_quantity, category ,description):
        self.product_id = product_id
        self.name = name
        self._price = 0.0
        self._stock_quantity = 0
        self.price = price
        self.stock_quantity = stock_quantity
        self.category = category
        self.description = description
    
    @property 
    def price(self):
        return self._price

    @price.setter
    def price(self , value ):
        if value < 0:
            raise ValueError("Price cannot be a negative integer")
        self._price = float (value)
    @property
    def stock_quantity(self):
        return self._stock_quantity
    
    @stock_quantity.setter
    def stock_quantity(self, value):
        if value <0 :
            raise ValueError("Stock quantity cannot be a negative integer")
        self._stock_quantity = int(value)
    
    def reduce_stock_quantity(self, quantity):
        if quantity > self.stock_quantity:
            return False
        self.stock_quantity -= quantity
        return True
    
    def increase_stock_quantity(self, quantity):
        self.stock_quantity +=quantity
    
    def stock_avaliablity(self, quantity):
        return self.stock_quantity > quantity
    
    def __str__(self):
        return f"product_name :{self.name}, price : {self.price}, product quantity : {self.stock_quantity}"
    
    def __repr__(self):
        return f"product_id : {self.product_id},product_name :{self.name} "
    def __eq__(self, other):
        if isinstance(other, Product):
            return self.product_id == other.product_id
        return False
    def __hash__(self):
        return hash(self.product_id)
    
# p1 = Product("A101", "Gaming Laptop", 1200.0, 10, "Electronics", "High-end gaming laptop")

# p2 = Product("B202", "Coffee Mug", 15.0, 50, "Kitchenware", "Ceramic 12oz mug")

# print(p1.stock_avaliablity(12))
# print(p2,p1)
# products = [p1,p2]

# print (products)
# print (hash(p1))

# if p1 == p2:
#     print ("Both P1 and P2 are same products")
# else :
#     print ("They are not the same product")

class DiscountedProduct (Product):
    def __init__(self, product_id, name, price, stock_quantity, category, description, discount_percentage):
        super().__init__(product_id, name, price, stock_quantity, category, description)

        self._discount_percentage = 0
        self.discount_percentage = discount_percentage

    @property
    def discount_percentage(self):
        return self._discount_percentage
    
    @discount_percentage.setter
    def discount_percentage(self,value):
        if 0 <= value <= 100:
            self._discount_percentage = float (value)
            return
        raise ValueError("Discount percentage must be between 0 and 100")
    
    @property
    def price(self):
        original = self.get_original_price()
        discount = self.discount_percentage
        return original - (original * (discount / 100))
    
    @price.setter
    def price(self, value):
        Product.price.fset(self, value)
    
    def get_original_price(self):
        return self._price
    
mouse = DiscountedProduct("M001", "Gaming Mouse", 100.0, 10, "Gear", "RGB Mouse", 20)

# print(f"Product: {mouse.name}")
# print(f"Original Price: ${mouse.get_original_price()}")
# print(f"Discounted Price: ${mouse.price}")


class Shoppingcart:
    def __init__(self):
        self._items = {}
    def add_item(self, Product, quantity=1):
        if Product.stock_avaliablity(quantity):
            if Product in self._items:
                self._items[Product] +=quantity
            else:
                self._items[Product] = quantity
            return True
        return False
    def remove_item(self, Product, quantity= 0):
        if Product in self._items:
            if quantity  == 0 or self._items[Product] <= quantity:
                del self._items[Product]
            else:
                self._items[Product] -= quantity

    def update_quantity(self, product, newquantity):
        if newquantity<=0:
            self.remove_item(product)
        elif product in self._items:
            self._items[product] = newquantity

    def get_total(self):
        total = 0.0
        for Product, quantity in self._items.items():
            total += Product.price * quantity
        return total
    def get_items(self):
        return [(p, q, p.price * q) for p, q in self._items.items()]
    def checkout(self):
        for product, quantity in self._items.items():
            if not product.reduce_stock_quantity(quantity):
                raise ValueError(f"Insufficient stock for {product.name}")
        self._items.clear()
    def is_empty(self):
        return len(self._items) == 0
    def __len__(self):
        return len(self._items)
    def __iter__(self):
        return iter(self._items.items())    
    def __str__(self):
        if self.is_empty():
            return "Shopping cart is empty."
        item_strs = [f"{p.name} (x{q}): ${p.price * q:.2f}" for p, q in self._items.items()]
        return "Shopping Cart:\n" + "\n".join(item_strs) + f"\nTotal: ${self.get_total():.2f}"
    
# Sample Products
# p1 = Product("A101", "Gaming Laptop", 1200.0, 10, "Electronics", "High-end gaming laptop")
# p2 = Product("B202", "Coffee Mug", 15.0, 50, "Kitchenware", "Ceramic 12oz mug")
# p3 = DiscountedProduct("C303", "Wireless Headset", 200.0, 5, "Electronics", "Noise cancelling", 25)

# # Create cart and add items
# cart = Shoppingcart()
# cart.add_item(p1, 2)
# cart.add_item(p2, 3)
# cart.add_item(p3, 1)

# # Print cart
# print(cart)

# # Update quantity
# cart.update_quantity(p2, 5)
# print("\nAfter updating Coffee Mug quantity to 5:")
# print(cart)

# # Remove one item
# cart.remove_item(p1, 1)
# print("\nAfter removing 1 Gaming Laptop:")
# print(cart)

# # Checkout
# print("\nChecking out...")
# cart.checkout()
# print("Stock after checkout:")
# print(f"Gaming Laptop stock: {p1.stock_quantity}")
# print(f"Coffee Mug stock: {p2.stock_quantity}")
# print(f"Wireless Headset stock: {p3.stock_quantity}")
# print(f"Cart empty: {cart.is_empty()}")

class Customer:
    def __init__(self,name ,email, address):
        self.name = name
        self.email = email
        self.address = address
    
    def __str__(self):
        return f"Customer Name: {self.name}, Email:{self.email}"

class Order :
    def __init__(self, Customer, Shoppingcart):
        self.customer = Customer 
        self.Shoppingcart = Shoppingcart
        self.order_id = str(uuid.uuid4())
        self.order_date = datetime.datetime.now()
        self.status = 'Pending'
        self.items = Shoppingcart.get_items()
        self.total_amount = Shoppingcart.get_total()

        for product, quantity, _ in self.items:
            product.reduce_stock_quantity(quantity)
    
    def confirm_order(self):
        self.status = 'Confirmed'
        return f"Order {self.order_id} confirmed."
    
    def cancel_order(self):
        if self.status == 'Pending':
            self.status = 'Cancelled'
            for product, quantity,_ in self.items:
                product.increase_stock_quantity(quantity)
            return f"Order id {self.order_id} is cancelled"
        return f"Order_id {self.order_id} cannot be cancelled as it is already {self.status}"
    
    def get_order_summary(self):
        summary = f"order_id: {self.order_id} " + f" \n customer: {self.customer.name}" +f" \n order date : {self.order_date}\n"
        for product , quantity, subtotal in self.items:
            summary += f"- {product.name} (x{quantity}): ${subtotal:.2f}\n"
        summary+= f"Total Cost :{self.total_amount}"
        return summary 



alice = Customer("Alice Smith", "alice@example.com", "123 Python Lane")

# 2. Create Products (Regular and Discounted)
laptop = Product("L101", "MacBook Pro", 2000.0, 5, "Electronics", "High-end laptop")
mouse = DiscountedProduct("M202", "Gaming Mouse", 100.0, 10, "Gear", "RGB Mouse", 20)

# 3. Setup Shopping Cart
cart = Shoppingcart() # Using your class name
cart.add_item(laptop, 1) # $2000
cart.add_item(mouse, 2)  # $160 (80 each)

print(f"Stock before Order: Laptop={laptop.stock_quantity}, Mouse={mouse.stock_quantity}")

# 4. Create the Order
# This should trigger the stock reduction automatically
order1 = Order(alice, cart)

print("\n--- Order Summary ---")
print(order1.get_order_summary())

print(f"\nStock after Order: Laptop={laptop.stock_quantity}, Mouse={mouse.stock_quantity}")

# 5. Test Cancellation
print("\n--- Testing Cancellation ---")
print(order1.cancel_order())
print(order1.cancel_order())
print(f"Stock after Cancellation: Laptop={laptop.stock_quantity}, Mouse={mouse.stock_quantity}")

