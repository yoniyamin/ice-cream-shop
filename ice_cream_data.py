import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import pyodbc
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json


def get_ice_cream_flavors():
    """
    Scrape a list of ice cream flavors from a website,
    falling back to defaults if the scrape fails or returns none.
    Ensures all returned flavors are unique.

    The flavors page uses <h5> tags formatted as "Letter – Flavor1, Flavor2, ...".
    We split on the dash and commas to extract individual flavor names.
    """
    default = ["Vanilla", "Chocolate", "Strawberry", "Mint"]
    url = "https://www.carpigiani.co.uk/news/ice-cream-flavours"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = set()  # Use set to ensure uniqueness
        for h in soup.select('.post-content h5'):
            text = h.get_text(strip=True)
            if '–' in text:
                parts = text.split('–', 1)[1]
            elif '-' in text:
                parts = text.split('-', 1)[1]
            else:
                continue
            for flavor in parts.split(','):
                name = flavor.strip()
                if name and len(name) > 1:  # Filter out single characters
                    items.add(name)
        # Convert to list and limit to 20 unique items
        unique_flavors = list(items)[:20] if items else default
        return unique_flavors
    except Exception:
        return default


def connect_to_db(server, database, user, password, driver, encrypt, trust_cert):
    """
    Build and return a pyodbc connection string that matches DBeaver's
    "Trust Server Certificate" behavior.
    """
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};DATABASE={database};"
        f"UID={user};PWD={password};"
        f"Encrypt={'yes' if encrypt else 'no'};"
        f"{('TrustServerCertificate=yes;' if trust_cert else '')}"
    )
    return pyodbc.connect(conn_str)


def generate_customers(cursor, schema, count):
    """Insert `count` random customers with expanded variety."""
    first_names = [
        "Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "Grace", "Henry", 
        "Isabella", "Jack", "Katherine", "Liam", "Mia", "Noah", "Olivia", "Paul",
        "Quinn", "Rachel", "Samuel", "Taylor", "Uma", "Victor", "Wendy", "Xavier",
        "Yara", "Zachary", "Sophia", "James", "Emma", "William", "Ava", "Benjamin",
        "Charlotte", "Lucas", "Amelia", "Mason", "Harper", "Elijah", "Evelyn", "Oliver",
        "Abigail", "Jacob", "Emily", "Michael", "Elizabeth", "Alexander", "Sofia",
        "Daniel", "Madison", "Matthew", "Scarlett", "Jackson", "Victoria", "David"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
        "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell"
    ]
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "company.com", "email.com"]
    
    for _ in range(count):
        fn, ln = random.choice(first_names), random.choice(last_names)
        domain = random.choice(domains)
        email = f"{fn.lower()}.{ln.lower()}@{domain}"
        phone = f"{random.choice(['555', '123', '456', '789'])}-{random.randint(1000,9999)}"
        cursor.execute(
            f"INSERT INTO {schema}.Customers (FirstName,LastName,Email,Phone) VALUES (?,?,?,?)",
            fn, ln, email, phone
        )


def generate_flavors(cursor, schema, count):
    """Insert `count` random flavors with expanded variety."""
    # Get scraped flavors and add more variety
    scraped_flavors = get_ice_cream_flavors()
    additional_flavors = [
        "Rocky Road", "Cookies and Cream", "Butter Pecan", "Pistachio", "Rum Raisin",
        "Neapolitan", "Mint Chocolate Chip", "Cherry Garcia", "Salted Caramel", "Tiramisu",
        "Green Tea", "Lavender", "Birthday Cake", "Cotton Candy", "Bubblegum", "Coconut",
        "Peanut Butter", "Maple Walnut", "Coffee", "Espresso", "Mocha", "Caramel Swirl",
        "Chocolate Fudge Brownie", "Strawberry Cheesecake", "Lemon Sorbet", "Mango",
        "Passion Fruit", "Blackberry", "Blueberry", "Raspberry Ripple", "Orange Sherbet",
        "Banana Split", "Pralines and Cream", "Dulce de Leche", "Honeycomb", "Toffee"
    ]
    
    all_flavors = list(set(scraped_flavors + additional_flavors))  # Ensure uniqueness
    descriptions = [
        "Rich and creamy", "Sweet and smooth", "Refreshing and light", "Decadent and indulgent",
        "Classic favorite", "Artisanal blend", "Premium quality", "Traditional recipe",
        "Exotic taste", "Seasonal special", "Chef's recommendation", "Customer favorite"
    ]
    
    for _ in range(count):
        flavor_name = random.choice(all_flavors)
        desc = f"{random.choice(descriptions)} {flavor_name.lower()} flavor"
        avail = random.choice([0, 1])
        cursor.execute(
            f"INSERT INTO {schema}.Flavors (Name,Description,IsAvailable) VALUES (?,?,?)",
            flavor_name, desc, avail
        )


def generate_toppings(cursor, schema, count):
    """Insert `count` random toppings with expanded variety."""
    toppings_list = [
        "Rainbow Sprinkles", "Chocolate Sprinkles", "Hot Fudge", "Caramel Sauce", 
        "Chopped Walnuts", "Chopped Almonds", "Chopped Pecans", "Peanuts", "Whipped Cream",
        "Chocolate Chips", "Mini Marshmallows", "Gummy Bears", "Oreo Crumbs", "Graham Crackers",
        "Fresh Strawberries", "Fresh Blueberries", "Banana Slices", "Cherry", "Pineapple",
        "Coconut Flakes", "Crushed Cookies", "Brownie Pieces", "Cookie Dough", "Fudge Chunks",
        "Toffee Bits", "Butterscotch Chips", "White Chocolate", "Dark Chocolate Shavings",
        "Honey Drizzle", "Maple Syrup", "Strawberry Sauce", "Raspberry Sauce", "Nutella"
    ]
    
    for _ in range(count):
        topping_name = random.choice(toppings_list)
        cost = round(random.uniform(0.25, 2.50), 2)  # More realistic price range
        avail = random.choice([0, 1])
        cursor.execute(
            f"INSERT INTO {schema}.Toppings (Name,ExtraCost,IsAvailable) VALUES (?,?,?)",
            topping_name, cost, avail
        )


def generate_inventory(cursor, schema):
    """Generate inventory records based on existing flavors and toppings."""
    # Get all flavors
    cursor.execute(f"SELECT FlavorID, Name FROM {schema}.Flavors")
    flavors = cursor.fetchall()
    
    # Get all toppings
    cursor.execute(f"SELECT ToppingID, Name FROM {schema}.Toppings")
    toppings = cursor.fetchall()
    
    inventory_count = 0
    
    # Add inventory for flavors
    for flavor_id, flavor_name in flavors:
        # Generate realistic inventory quantities for flavors
        if "Vanilla" in flavor_name or "Chocolate" in flavor_name:
            # Popular flavors have more stock
            quantity = random.randint(50, 150)
        elif "Seasonal" in flavor_name or "Limited" in flavor_name:
            # Seasonal/limited flavors have less stock
            quantity = random.randint(5, 25)
        else:
            # Regular flavors
            quantity = random.randint(20, 80)
        
        cursor.execute(
            f"INSERT INTO {schema}.Inventory (ItemType, ItemName, QuantityInStock) VALUES (?,?,?)",
            "Flavor", flavor_name, quantity
        )
        inventory_count += 1
    
    # Add inventory for toppings
    for topping_id, topping_name in toppings:
        # Generate realistic inventory quantities for toppings
        if "Sprinkles" in topping_name or "Sauce" in topping_name:
            # Popular toppings have more stock
            quantity = random.randint(30, 100)
        elif "Fresh" in topping_name:
            # Perishable items have less stock
            quantity = random.randint(5, 20)
        else:
            # Regular toppings
            quantity = random.randint(15, 60)
        
        cursor.execute(
            f"INSERT INTO {schema}.Inventory (ItemType, ItemName, QuantityInStock) VALUES (?,?,?)",
            "Topping", topping_name, quantity
        )
        inventory_count += 1
    
    return inventory_count


def generate_orders(cursor, schema, count):
    """Insert `count` random orders for existing customers with more realistic data."""
    cursor.execute(f"SELECT CustomerID FROM {schema}.Customers")
    custs = [r[0] for r in cursor.fetchall()]
    if not custs:
        raise RuntimeError("No customers found: generate customers first.")
    
    for _ in range(count):
        # More varied date range (last 90 days)
        days_ago = random.randint(0, 90)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        dt = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # More realistic pricing tiers
        price_ranges = [
            (3.50, 8.00),   # Single scoop range
            (6.00, 12.00),  # Double scoop range  
            (10.00, 18.00), # Sundae range
            (15.00, 25.00)  # Family size range
        ]
        min_price, max_price = random.choice(price_ranges)
        total = round(random.uniform(min_price, max_price), 2)
        
        cursor.execute(
            f"INSERT INTO {schema}.Orders (CustomerID,OrderDate,TotalAmount) VALUES (?,?,?)",
            random.choice(custs), dt, total
        )


def generate_detailed_orders(cursor, schema, count, order_date=None, temperature=None):
    """Insert detailed orders with OrderDetails and OrderToppings."""
    # Get required data
    cursor.execute(f"SELECT CustomerID FROM {schema}.Customers")
    custs = [r[0] for r in cursor.fetchall()]
    if not custs:
        raise RuntimeError("No customers found: generate customers first.")
    
    cursor.execute(f"SELECT FlavorID, Name FROM {schema}.Flavors WHERE IsAvailable = 1")
    flavors = cursor.fetchall()
    if not flavors:
        raise RuntimeError("No available flavors found: generate flavors first.")
    
    cursor.execute(f"SELECT ToppingID, Name, ExtraCost FROM {schema}.Toppings WHERE IsAvailable = 1")
    toppings = cursor.fetchall()
    
    orders_created = 0
    details_created = 0
    toppings_added = 0
    
    for _ in range(count):
        # Use provided date or generate random date
        if order_date:
            # Random time during business hours for the specific date
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            dt = order_date.replace(hour=hour, minute=minute)
        else:
            # Random date in last 90 days
            days_ago = random.randint(0, 90)
            hours_ago = random.randint(8, 22)
            minutes_ago = random.randint(0, 59)
            dt = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # Calculate pricing based on temperature and season
        if temperature and temperature >= 85:  # Very hot day pricing
            base_prices = {"Small": 4.50, "Medium": 7.00, "Large": 9.50}
            scoop_prices = {"Small": 2.50, "Medium": 3.50, "Large": 4.50}
        elif temperature and temperature >= 75:  # Hot day pricing
            base_prices = {"Small": 4.00, "Medium": 6.50, "Large": 9.00}
            scoop_prices = {"Small": 2.25, "Medium": 3.25, "Large": 4.25}
        elif temperature and temperature >= 55:  # Normal pricing
            base_prices = {"Small": 3.50, "Medium": 6.00, "Large": 8.50}
            scoop_prices = {"Small": 2.00, "Medium": 3.00, "Large": 4.00}
        else:  # Cold day pricing
            base_prices = {"Small": 3.00, "Medium": 5.50, "Large": 8.00}
            scoop_prices = {"Small": 1.75, "Medium": 2.75, "Large": 3.75}
        
        # Create the order
        cursor.execute(
            f"INSERT INTO {schema}.Orders (CustomerID, OrderDate, TotalAmount) OUTPUT INSERTED.OrderID VALUES (?,?,?)",
            random.choice(custs), dt, 0  # Will calculate total later
        )
        order_id = cursor.fetchone()[0]
        
        # Determine number of items in this order (1-4 items per order)
        num_items = random.choices([1, 2, 3, 4], weights=[40, 35, 20, 5])[0]
        order_total = 0
        
        for item_num in range(num_items):
            # Choose size based on temperature (hot days = larger sizes)
            if temperature and temperature >= 80:
                size = random.choices(["Small", "Medium", "Large"], weights=[20, 40, 40])[0]
            elif temperature and temperature >= 65:
                size = random.choices(["Small", "Medium", "Large"], weights=[30, 45, 25])[0]
            else:
                size = random.choices(["Small", "Medium", "Large"], weights=[50, 35, 15])[0]
            
            # Choose number of scoops (1-3 scoops, larger sizes more likely to have more scoops)
            if size == "Large":
                scoop_count = random.choices([1, 2, 3], weights=[10, 50, 40])[0]
            elif size == "Medium":
                scoop_count = random.choices([1, 2, 3], weights=[25, 60, 15])[0]
            else:  # Small
                scoop_count = random.choices([1, 2], weights=[70, 30])[0]
            
            # Choose flavor(s)
            selected_flavors = random.sample(flavors, min(scoop_count, len(flavors)))
            primary_flavor = selected_flavors[0]
            
            # Calculate item price
            base_price = base_prices[size]
            scoop_price = scoop_prices[size] * scoop_count
            item_price = base_price + scoop_price
            
            # Create OrderDetail
            cursor.execute(
                f"INSERT INTO {schema}.OrderDetails (OrderID, FlavorID, ScoopCount, Size, Price) OUTPUT INSERTED.OrderDetailID VALUES (?,?,?,?,?)",
                order_id, primary_flavor[0], scoop_count, size, round(item_price, 2)
            )
            order_detail_id = cursor.fetchone()[0]
            details_created += 1
            
            # Add toppings (30% chance per item, more likely on larger sizes)
            topping_chance = 0.15 if size == "Small" else 0.25 if size == "Medium" else 0.40
            if random.random() < topping_chance and toppings:
                # Choose 1-3 toppings
                num_toppings = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
                selected_toppings = random.sample(toppings, min(num_toppings, len(toppings)))
                
                for topping_id, topping_name, extra_cost in selected_toppings:
                    cursor.execute(
                        f"INSERT INTO {schema}.OrderToppings (OrderDetailID, ToppingID) VALUES (?,?)",
                        order_detail_id, topping_id
                    )
                    item_price += float(extra_cost)  # Convert Decimal to float
                    toppings_added += 1
            
            order_total += item_price
        
        # Update order total
        cursor.execute(
            f"UPDATE {schema}.Orders SET TotalAmount = ? WHERE OrderID = ?",
            round(order_total, 2), order_id
        )
        
        orders_created += 1
    
    return {"orders": orders_created, "details": details_created, "toppings": toppings_added}


def generate_yearly_orders(cursor, schema, count, year=None, weather_data=None):
    """Insert `count` random orders distributed across a full year for existing customers, influenced by weather."""
    cursor.execute(f"SELECT CustomerID FROM {schema}.Customers")
    custs = [r[0] for r in cursor.fetchall()]
    if not custs:
        raise RuntimeError("No customers found: generate customers first.")
    
    # Use specified year or current year
    if year is None:
        year = datetime.now().year
    
    # Calculate date range for the specified year
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    days_in_year = (end_date - start_date).days + 1
    
    # If no weather data provided, try to fetch it
    if weather_data is None:
        weather_data = get_boston_weather_data(year)
    
    # Calculate daily order distribution based on weather and habits
    daily_orders = []
    total_weight = 0
    
    for day_offset in range(days_in_year):
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Get temperature for this date
        temperature = weather_data.get(date_str)
        
        # Calculate base weight from temperature
        temp_multiplier = calculate_order_multiplier(temperature)
        
        # Add buying habit variations
        base_daily_orders = count / days_in_year  # Average orders per day
        adjusted_orders = add_buying_habit_variations(base_daily_orders, current_date, temperature)
        
        # Apply temperature multiplier
        daily_weight = adjusted_orders * temp_multiplier
        daily_orders.append((current_date, daily_weight, temperature))
        total_weight += daily_weight
    
    # Determine order counts per day while keeping total close to requested count
    day_counts = []
    for _, daily_weight, _ in daily_orders:
        if total_weight > 0:
            dc = int((daily_weight / total_weight) * count)
            if random.random() < 0.3:  # slight randomness
                dc += random.randint(-2, 3)
            dc = max(0, dc)
        else:
            dc = 0
        day_counts.append(dc)

    # Adjust to exactly match requested total count
    diff = count - sum(day_counts)
    i = 0
    while diff != 0 and day_counts:
        idx = i % len(day_counts)
        if diff > 0:
            day_counts[idx] += 1
            diff -= 1
        elif day_counts[idx] > 0:
            day_counts[idx] -= 1
            diff += 1
        i += 1

    # Generate orders based on final day counts
    orders_generated = 0
    for (current_date, _, temperature), dc in zip(daily_orders, day_counts):
        if dc > 0:
            stats = generate_detailed_orders(cursor, schema, dc, current_date, temperature)
            orders_generated += stats["orders"]

    return orders_generated


def generate_date_range_orders(cursor, schema, count, start_date, end_date, weather_data=None):
    """Insert `count` random orders distributed across a date range for existing customers, influenced by weather."""
    cursor.execute(f"SELECT CustomerID FROM {schema}.Customers")
    custs = [r[0] for r in cursor.fetchall()]
    if not custs:
        raise RuntimeError("No customers found: generate customers first.")
    
    # Calculate date range
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    if start_date > end_date:
        raise ValueError("Start date must be before or equal to end date")
    
    # Calculate number of days in range
    days_in_range = (end_date - start_date).days + 1
    
    # Get weather data for the specific date range if not provided
    if weather_data is None:
        weather_data = get_boston_weather_data_range(start_date, end_date)
    
    # Calculate daily order distribution based on weather and habits
    daily_orders = []
    total_weight = 0
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Get temperature for this date
        temperature = weather_data.get(date_str)
        
        # Calculate base weight from temperature
        temp_multiplier = calculate_order_multiplier(temperature)
        
        # Add buying habit variations
        base_daily_orders = count / days_in_range  # Average orders per day
        adjusted_orders = add_buying_habit_variations(base_daily_orders, current_date, temperature)
        
        # Apply temperature multiplier
        daily_weight = adjusted_orders * temp_multiplier
        daily_orders.append((current_date, daily_weight, temperature))
        total_weight += daily_weight
        
        current_date += timedelta(days=1)
    
    # Generate orders for each day based on calculated weights
    orders_generated = 0
    for current_date, daily_weight, temperature in daily_orders:
        if total_weight > 0:
            # Calculate number of orders for this day
            day_orders = int((daily_weight / total_weight) * count)
            
            # Add some randomness to avoid too predictable patterns
            if random.random() < 0.3:  # 30% chance of slight variation
                day_orders += random.randint(-1, 2)
            
            day_orders = max(0, day_orders)  # Ensure non-negative
            
            # Generate orders for this day
            if day_orders > 0:
                stats = generate_detailed_orders(cursor, schema, day_orders, current_date, temperature)
                orders_generated += stats["orders"]
    
    return orders_generated


def recreate_schema(conn, schema='dbo'):
    """Drop and recreate all tables under given schema."""
    cursor = conn.cursor()
    for tbl in ["OrderToppings", "OrderDetails", "Orders", "Toppings", "Flavors", "Customers", "Inventory"]:
        cursor.execute(
            f"IF OBJECT_ID('{schema}.{tbl}','U') IS NOT NULL DROP TABLE {schema}.{tbl}"
        )
    stmts = [
        f"CREATE TABLE {schema}.Customers (CustomerID INT IDENTITY(1,1) PRIMARY KEY, FirstName NVARCHAR(50), LastName NVARCHAR(50), Email NVARCHAR(100), Phone NVARCHAR(20), CreatedAt DATETIME DEFAULT GETDATE())",
        f"CREATE TABLE {schema}.Flavors (FlavorID INT IDENTITY(1,1) PRIMARY KEY, Name NVARCHAR(50) NOT NULL, Description NVARCHAR(255), IsAvailable BIT DEFAULT 1)",
        f"CREATE TABLE {schema}.Toppings (ToppingID INT IDENTITY(1,1) PRIMARY KEY, Name NVARCHAR(50) NOT NULL, ExtraCost DECIMAL(5,2) DEFAULT 0.00, IsAvailable BIT DEFAULT 1)",
        f"CREATE TABLE {schema}.Orders (OrderID INT IDENTITY(1,1) PRIMARY KEY, CustomerID INT REFERENCES {schema}.Customers(CustomerID), OrderDate DATETIME DEFAULT GETDATE(), TotalAmount DECIMAL(10,2))",
        f"CREATE TABLE {schema}.OrderDetails (OrderDetailID INT IDENTITY(1,1) PRIMARY KEY, OrderID INT REFERENCES {schema}.Orders(OrderID), FlavorID INT REFERENCES {schema}.Flavors(FlavorID), ScoopCount INT CHECK(ScoopCount>0), Size NVARCHAR(10) CHECK(Size IN ('Small','Medium','Large')), Price DECIMAL(6,2))",
        f"CREATE TABLE {schema}.OrderToppings (OrderDetailID INT REFERENCES {schema}.OrderDetails(OrderDetailID), ToppingID INT REFERENCES {schema}.Toppings(ToppingID), PRIMARY KEY(OrderDetailID,ToppingID))",
        f"CREATE TABLE {schema}.Inventory (ItemID INT IDENTITY(1,1) PRIMARY KEY, ItemType NVARCHAR(20) CHECK(ItemType IN ('Flavor','Topping')), ItemName NVARCHAR(50), QuantityInStock INT DEFAULT 0)"
    ]
    for s in stmts:
        cursor.execute(s)
    conn.commit()
    return "Schema recreated successfully."


def get_boston_weather_data(year, log_callback=None):
    """
    Fetch daily temperature data for Boston from Open-Meteo API for the specified year.
    Returns a dictionary mapping date strings to temperature values.
    For future years or API failures, generates realistic weather patterns.
    """
    def log_msg(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)
    
    current_year = datetime.now().year
    
    # For future years, generate realistic weather patterns based on Boston climate
    if year > current_year:
        log_msg(f"⚠️ Year {year} is in the future, using realistic weather patterns for Boston")
        return generate_boston_weather_pattern(year)
    
    try:
        # Boston coordinates: latitude=42.35, longitude=-71.05
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": 42.35,
            "longitude": -71.05,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_max",
            "temperature_unit": "fahrenheit",
            "timezone": "America/New_York"
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        # Handle HTTP errors with detailed messages
        if response.status_code == 400:
            try:
                error_data = response.json()
                if 'reason' in error_data:
                    error_msg = error_data['reason']
                    log_msg(f"❌ Weather API Error: {error_msg}")
                    log_msg(f"📊 Switching to realistic weather patterns for Boston {year}")
                    return generate_boston_weather_pattern(year)
                else:
                    log_msg(f"❌ Weather API returned 400 error for year {year}")
                    log_msg(f"📊 Switching to realistic weather patterns for Boston {year}")
                    return generate_boston_weather_pattern(year)
            except:
                log_msg(f"❌ Weather API returned 400 error for year {year}")
                log_msg(f"📊 Switching to realistic weather patterns for Boston {year}")
                return generate_boston_weather_pattern(year)
        
        response.raise_for_status()
        
        data = response.json()
        weather_dict = {}
        
        if 'daily' in data and 'time' in data['daily'] and 'temperature_2m_max' in data['daily']:
            dates = data['daily']['time']
            temps = data['daily']['temperature_2m_max']
            
            for date_str, temp in zip(dates, temps):
                if temp is not None:  # Handle missing data
                    weather_dict[date_str] = temp
        
        # If we got good data, return it
        if weather_dict:
            log_msg(f"✅ Retrieved {len(weather_dict)} days of historical weather data for {year}")
            return weather_dict
        else:
            log_msg(f"⚠️ No temperature data in API response for {year}")
            log_msg(f"📊 Switching to realistic weather patterns for Boston {year}")
            return generate_boston_weather_pattern(year)
        
    except requests.exceptions.Timeout:
        log_msg(f"⏰ Weather API timeout for year {year}")
        log_msg(f"📊 Switching to realistic weather patterns for Boston {year}")
        return generate_boston_weather_pattern(year)
    except requests.exceptions.RequestException as e:
        log_msg(f"🌐 Weather API connection error for year {year}: {e}")
        log_msg(f"📊 Switching to realistic weather patterns for Boston {year}")
        return generate_boston_weather_pattern(year)
    except Exception as e:
        log_msg(f"❌ Weather API error for year {year}: {e}")
        log_msg(f"📊 Switching to realistic weather patterns for Boston {year}")
        return generate_boston_weather_pattern(year)


def generate_boston_weather_pattern(year):
    """
    Generate realistic weather patterns for Boston based on historical climate data.
    Used as fallback when API is unavailable or for future years.
    """
    weather_dict = {}
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    
    # Boston monthly average temperatures (high temperatures in °F)
    monthly_avg_temps = {
        1: 36,   # January
        2: 39,   # February  
        3: 46,   # March
        4: 56,   # April
        5: 67,   # May
        6: 76,   # June
        7: 82,   # July - peak summer
        8: 80,   # August
        9: 72,   # September
        10: 62,  # October
        11: 52,  # November
        12: 42   # December
    }
    
    # Temperature variation ranges for each month
    monthly_ranges = {
        1: 25,   # January: can vary ±25°F from average
        2: 22,   # February
        3: 20,   # March
        4: 18,   # April
        5: 15,   # May
        6: 12,   # June
        7: 10,   # July - most stable
        8: 12,   # August
        9: 15,   # September
        10: 18,  # October
        11: 20,  # November
        12: 23   # December
    }
    
    current_date = start_date
    while current_date <= end_date:
        month = current_date.month
        day_of_year = current_date.timetuple().tm_yday
        
        # Base temperature for this month
        base_temp = monthly_avg_temps[month]
        temp_range = monthly_ranges[month]
        
        # Add seasonal progression within the month
        # Create smooth transitions between months
        if month < 12:
            next_month_temp = monthly_avg_temps[month + 1]
        else:
            next_month_temp = monthly_avg_temps[1]
        
        # Progress through the month (0.0 to 1.0)
        days_in_month = (datetime(year, month + 1, 1) - datetime(year, month, 1)).days if month < 12 else 31
        if month == 12:
            days_in_month = 31
        month_progress = (current_date.day - 1) / days_in_month
        
        # Interpolate between current and next month
        interpolated_temp = base_temp + (next_month_temp - base_temp) * month_progress * 0.3
        
        # Add daily variation
        daily_variation = random.uniform(-temp_range/2, temp_range/2)
        
        # Add weather patterns (simulate multi-day trends)
        # Use day of year to create consistent but varied patterns
        pattern_seed = (day_of_year * 17 + year) % 100  # Pseudo-random but consistent
        if pattern_seed < 20:  # 20% chance of heat wave
            daily_variation += random.uniform(5, 15)
        elif pattern_seed > 80:  # 20% chance of cold snap
            daily_variation -= random.uniform(5, 12)
        
        # Calculate final temperature
        final_temp = interpolated_temp + daily_variation
        
        # Apply realistic bounds for Boston
        final_temp = max(-10, min(105, final_temp))  # Extreme bounds for Boston
        
        # Round to reasonable precision
        final_temp = round(final_temp, 1)
        
        date_str = current_date.strftime('%Y-%m-%d')
        weather_dict[date_str] = final_temp
        
        current_date += timedelta(days=1)
    
    return weather_dict


def calculate_order_multiplier(temperature, base_temp=65):
    """
    Calculate order multiplier based on temperature.
    Base temperature is 65°F - comfortable temperature with normal ordering.
    Returns a multiplier between 0.3 and 3.0.
    """
    if temperature is None:
        return 1.0  # Default multiplier if no temperature data
    
    # Temperature effect curve - more orders when hotter
    if temperature >= 85:  # Very hot days
        return 2.5 + random.uniform(0, 0.5)  # 2.5-3.0x orders
    elif temperature >= 75:  # Hot days
        return 1.8 + random.uniform(0, 0.4)  # 1.8-2.2x orders
    elif temperature >= 65:  # Warm days
        return 1.2 + random.uniform(0, 0.3)  # 1.2-1.5x orders
    elif temperature >= 55:  # Cool days
        return 0.8 + random.uniform(0, 0.2)  # 0.8-1.0x orders
    elif temperature >= 45:  # Cold days
        return 0.5 + random.uniform(0, 0.2)  # 0.5-0.7x orders
    else:  # Very cold days
        return 0.3 + random.uniform(0, 0.2)  # 0.3-0.5x orders


def add_buying_habit_variations(base_orders, date_obj, temperature):
    """
    Add random buying habit variations based on day of week, holidays, and weather patterns.
    """
    multiplier = 1.0
    
    # Weekend effect - more people out and about
    if date_obj.weekday() in [5, 6]:  # Saturday = 5, Sunday = 6
        multiplier *= 1.3 + random.uniform(0, 0.2)  # 1.3-1.5x on weekends
    
    # Summer vacation effect (June-August)
    if date_obj.month in [6, 7, 8]:
        multiplier *= 1.1 + random.uniform(0, 0.15)  # 1.1-1.25x in summer
    
    # Holiday periods - reduced business hours but higher intensity when open
    if date_obj.month == 12 and date_obj.day in range(20, 32):  # Christmas week
        multiplier *= 0.7 + random.uniform(0, 0.2)  # 0.7-0.9x during holidays
    elif date_obj.month == 7 and date_obj.day == 4:  # July 4th
        multiplier *= 1.5 + random.uniform(0, 0.3)  # 1.5-1.8x on July 4th
    elif date_obj.month == 5 and date_obj.weekday() == 0 and date_obj.day >= 25:  # Memorial Day
        multiplier *= 1.4 + random.uniform(0, 0.2)  # 1.4-1.6x on Memorial Day
    
    # Rainy day effect - assume fewer orders on very hot days that might have storms
    if temperature and temperature > 90:
        # Very hot days might have afternoon storms, slight reduction
        multiplier *= 0.9 + random.uniform(0, 0.1)  # 0.9-1.0x
    
    # School schedule effect - more kids during school holidays
    if date_obj.month in [6, 7, 8] and date_obj.weekday() < 5:  # Summer weekdays
        multiplier *= 1.2 + random.uniform(0, 0.1)  # 1.2-1.3x (kids out of school)
    
    # Apply all multipliers
    adjusted_orders = int(base_orders * multiplier)
    
    # Ensure minimum of 0 orders
    return max(0, adjusted_orders)


def get_single_day_weather_data(year, month, day, log_callback=None):
    """
    Fetch temperature data for a single specific date from Open-Meteo API.
    Returns temperature value or None if not available.
    Provides detailed logging of API request and response.
    """
    def log_msg(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)
    
    current_year = datetime.now().year
    test_date = f"{year}-{month:02d}-{day:02d}"
    
    # For future years, generate realistic weather patterns
    if year > current_year:
        log_msg(f"⚠️ Date {test_date} is in the future, using realistic weather pattern")
        weather_pattern = generate_boston_weather_pattern(year)
        return weather_pattern.get(test_date)
    
    try:
        # Boston coordinates: latitude=42.35, longitude=-71.05
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": 42.35,
            "longitude": -71.05,
            "start_date": test_date,
            "end_date": test_date,  # Same date for single day
            "daily": "temperature_2m_max",
            "temperature_unit": "fahrenheit",
            "timezone": "America/New_York"
        }
        
        # Log the actual API request being made
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{param_string}"
        log_msg(f"🌐 API Request: {full_url}")
        
        response = requests.get(url, params=params, timeout=15)
        
        # Handle HTTP errors with detailed messages
        if response.status_code == 400:
            try:
                error_data = response.json()
                if 'reason' in error_data:
                    error_msg = error_data['reason']
                    log_msg(f"❌ Weather API Error (400): {error_msg}")
                    log_msg(f"📊 Request URL: {full_url}")
                    log_msg(f"📊 Switching to realistic weather pattern for {test_date}")
                    weather_pattern = generate_boston_weather_pattern(year)
                    return weather_pattern.get(test_date)
                else:
                    log_msg(f"❌ Weather API returned 400 error for date {test_date}")
                    log_msg(f"📊 Request URL: {full_url}")
                    log_msg(f"📊 Switching to realistic weather pattern for {test_date}")
                    weather_pattern = generate_boston_weather_pattern(year)
                    return weather_pattern.get(test_date)
            except:
                log_msg(f"❌ Weather API returned 400 error for date {test_date}")
                log_msg(f"📊 Request URL: {full_url}")
                log_msg(f"📊 Switching to realistic weather pattern for {test_date}")
                weather_pattern = generate_boston_weather_pattern(year)
                return weather_pattern.get(test_date)
        
        response.raise_for_status()
        
        data = response.json()
        log_msg(f"✅ API Response received for {test_date}")
        
        if 'daily' in data and 'time' in data['daily'] and 'temperature_2m_max' in data['daily']:
            dates = data['daily']['time']
            temps = data['daily']['temperature_2m_max']
            
            if dates and temps and len(dates) > 0 and len(temps) > 0:
                temp = temps[0]  # Should only be one day
                if temp is not None:
                    log_msg(f"📊 Historical weather data retrieved from API")
                    return temp
        
        # If we got here, no valid data
        log_msg(f"⚠️ No temperature data in API response for {test_date}")
        log_msg(f"📊 Switching to realistic weather pattern for {test_date}")
        weather_pattern = generate_boston_weather_pattern(year)
        return weather_pattern.get(test_date)
        
    except requests.exceptions.Timeout:
        log_msg(f"⏰ Weather API timeout for date {test_date}")
        log_msg(f"📊 Switching to realistic weather pattern for {test_date}")
        weather_pattern = generate_boston_weather_pattern(year)
        return weather_pattern.get(test_date)
    except requests.exceptions.RequestException as e:
        log_msg(f"🌐 Weather API connection error for date {test_date}: {e}")
        log_msg(f"📊 Switching to realistic weather pattern for {test_date}")
        weather_pattern = generate_boston_weather_pattern(year)
        return weather_pattern.get(test_date)
    except Exception as e:
        log_msg(f"❌ Weather API error for date {test_date}: {e}")
        log_msg(f"📊 Switching to realistic weather pattern for {test_date}")
        weather_pattern = generate_boston_weather_pattern(year)
        return weather_pattern.get(test_date)


def get_boston_weather_data_range(start_date, end_date, log_callback=None):
    """
    Fetch daily temperature data for Boston from Open-Meteo API for a specific date range.
    Returns a dictionary mapping date strings to temperature values.
    For future dates or API failures, generates realistic weather patterns.
    """
    def log_msg(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)
    
    # Convert string dates to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    current_date = datetime.now().date()
    
    # Check if any part of the range is in the future
    if start_date.date() > current_date or end_date.date() > current_date:
        # For future dates, generate realistic weather patterns
        log_msg(f"⚠️ Date range {start_date_str} to {end_date_str} includes future dates, using realistic weather patterns")
        
        # Generate patterns for all years in the range
        weather_data = {}
        years_needed = set()
        current_check = start_date
        while current_check <= end_date:
            years_needed.add(current_check.year)
            current_check += timedelta(days=1)
        
        for year in years_needed:
            year_weather = generate_boston_weather_pattern(year)
            weather_data.update(year_weather)
        
        # Filter to only the requested date range
        filtered_weather = {}
        current_check = start_date
        while current_check <= end_date:
            date_str = current_check.strftime('%Y-%m-%d')
            if date_str in weather_data:
                filtered_weather[date_str] = weather_data[date_str]
            current_check += timedelta(days=1)
        
        return filtered_weather
    
    try:
        # Boston coordinates: latitude=42.35, longitude=-71.05
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": 42.35,
            "longitude": -71.05,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "daily": "temperature_2m_max",
            "temperature_unit": "fahrenheit",
            "timezone": "America/New_York"
        }
        
        # Log the actual API request being made
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{param_string}"
        log_msg(f"🌐 API Request for date range: {full_url}")
        
        response = requests.get(url, params=params, timeout=15)
        
        # Handle HTTP errors with detailed messages
        if response.status_code == 400:
            try:
                error_data = response.json()
                if 'reason' in error_data:
                    error_msg = error_data['reason']
                    log_msg(f"❌ Weather API Error (400): {error_msg}")
                    log_msg(f"📊 Request URL: {full_url}")
                    log_msg(f"📊 Switching to realistic weather patterns for date range {start_date_str} to {end_date_str}")
                    
                    # Generate patterns for all years in the range
                    weather_data = {}
                    years_needed = set()
                    current_check = start_date
                    while current_check <= end_date:
                        years_needed.add(current_check.year)
                        current_check += timedelta(days=1)
                    
                    for year in years_needed:
                        year_weather = generate_boston_weather_pattern(year)
                        weather_data.update(year_weather)
                    
                    # Filter to only the requested date range
                    filtered_weather = {}
                    current_check = start_date
                    while current_check <= end_date:
                        date_str = current_check.strftime('%Y-%m-%d')
                        if date_str in weather_data:
                            filtered_weather[date_str] = weather_data[date_str]
                        current_check += timedelta(days=1)
                    
                    return filtered_weather
                else:
                    log_msg(f"❌ Weather API returned 400 error for date range {start_date_str} to {end_date_str}")
                    log_msg(f"📊 Request URL: {full_url}")
                    log_msg(f"📊 Switching to realistic weather patterns")
                    
                    # Generate fallback patterns
                    weather_data = {}
                    years_needed = set()
                    current_check = start_date
                    while current_check <= end_date:
                        years_needed.add(current_check.year)
                        current_check += timedelta(days=1)
                    
                    for year in years_needed:
                        year_weather = generate_boston_weather_pattern(year)
                        weather_data.update(year_weather)
                    
                    # Filter to only the requested date range
                    filtered_weather = {}
                    current_check = start_date
                    while current_check <= end_date:
                        date_str = current_check.strftime('%Y-%m-%d')
                        if date_str in weather_data:
                            filtered_weather[date_str] = weather_data[date_str]
                        current_check += timedelta(days=1)
                    
                    return filtered_weather
            except:
                log_msg(f"❌ Weather API returned 400 error for date range {start_date_str} to {end_date_str}")
                log_msg(f"📊 Request URL: {full_url}")
                log_msg(f"📊 Switching to realistic weather patterns")
                
                # Generate fallback patterns
                weather_data = {}
                years_needed = set()
                current_check = start_date
                while current_check <= end_date:
                    years_needed.add(current_check.year)
                    current_check += timedelta(days=1)
                
                for year in years_needed:
                    year_weather = generate_boston_weather_pattern(year)
                    weather_data.update(year_weather)
                
                # Filter to only the requested date range
                filtered_weather = {}
                current_check = start_date
                while current_check <= end_date:
                    date_str = current_check.strftime('%Y-%m-%d')
                    if date_str in weather_data:
                        filtered_weather[date_str] = weather_data[date_str]
                    current_check += timedelta(days=1)
                
                return filtered_weather
        
        response.raise_for_status()
        
        data = response.json()
        log_msg(f"✅ API Response received for date range {start_date_str} to {end_date_str}")
        
        weather_dict = {}
        if 'daily' in data and 'time' in data['daily'] and 'temperature_2m_max' in data['daily']:
            dates = data['daily']['time']
            temps = data['daily']['temperature_2m_max']
            
            for date_str, temp in zip(dates, temps):
                if temp is not None:  # Handle missing data
                    weather_dict[date_str] = temp
        
        # If we got good data, return it
        if weather_dict:
            log_msg(f"📊 Retrieved {len(weather_dict)} days of historical weather data from API")
            return weather_dict
        else:
            log_msg(f"⚠️ No temperature data in API response for date range {start_date_str} to {end_date_str}")
            log_msg(f"📊 Switching to realistic weather patterns")
            
            # Generate fallback patterns
            weather_data = {}
            years_needed = set()
            current_check = start_date
            while current_check <= end_date:
                years_needed.add(current_check.year)
                current_check += timedelta(days=1)
            
            for year in years_needed:
                year_weather = generate_boston_weather_pattern(year)
                weather_data.update(year_weather)
            
            # Filter to only the requested date range
            filtered_weather = {}
            current_check = start_date
            while current_check <= end_date:
                date_str = current_check.strftime('%Y-%m-%d')
                if date_str in weather_data:
                    filtered_weather[date_str] = weather_data[date_str]
                current_check += timedelta(days=1)
            
            return filtered_weather
        
    except requests.exceptions.Timeout:
        log_msg(f"⏰ Weather API timeout for date range {start_date_str} to {end_date_str}")
        log_msg(f"📊 Switching to realistic weather patterns")
        
        # Generate fallback patterns
        weather_data = {}
        years_needed = set()
        current_check = start_date
        while current_check <= end_date:
            years_needed.add(current_check.year)
            current_check += timedelta(days=1)
        
        for year in years_needed:
            year_weather = generate_boston_weather_pattern(year)
            weather_data.update(year_weather)
        
        # Filter to only the requested date range
        filtered_weather = {}
        current_check = start_date
        while current_check <= end_date:
            date_str = current_check.strftime('%Y-%m-%d')
            if date_str in weather_data:
                filtered_weather[date_str] = weather_data[date_str]
            current_check += timedelta(days=1)
        
        return filtered_weather
    except requests.exceptions.RequestException as e:
        log_msg(f"🌐 Weather API connection error for date range {start_date_str} to {end_date_str}: {e}")
        log_msg(f"📊 Switching to realistic weather patterns")
        
        # Generate fallback patterns
        weather_data = {}
        years_needed = set()
        current_check = start_date
        while current_check <= end_date:
            years_needed.add(current_check.year)
            current_check += timedelta(days=1)
        
        for year in years_needed:
            year_weather = generate_boston_weather_pattern(year)
            weather_data.update(year_weather)
        
        # Filter to only the requested date range
        filtered_weather = {}
        current_check = start_date
        while current_check <= end_date:
            date_str = current_check.strftime('%Y-%m-%d')
            if date_str in weather_data:
                filtered_weather[date_str] = weather_data[date_str]
            current_check += timedelta(days=1)
        
        return filtered_weather
    except Exception as e:
        log_msg(f"❌ Weather API error for date range {start_date_str} to {end_date_str}: {e}")
        log_msg(f"📊 Switching to realistic weather patterns")
        
        # Generate fallback patterns
        weather_data = {}
        years_needed = set()
        current_check = start_date
        while current_check <= end_date:
            years_needed.add(current_check.year)
            current_check += timedelta(days=1)
        
        for year in years_needed:
            year_weather = generate_boston_weather_pattern(year)
            weather_data.update(year_weather)
        
        # Filter to only the requested date range
        filtered_weather = {}
        current_check = start_date
        while current_check <= end_date:
            date_str = current_check.strftime('%Y-%m-%d')
            if date_str in weather_data:
                filtered_weather[date_str] = weather_data[date_str]
            current_check += timedelta(days=1)
        
        return filtered_weather


class IceCreamApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.title("🍦 Ice Cream Database Generator")
        master.geometry("1400x900")  # Much wider to accommodate side-by-side layout
        master.minsize(1300, 850)   # Wider minimum size
        
        # Configure ice cream themed colors
        style = ttk.Style()
        
        # Ice cream themed color palette
        colors = {
            'vanilla': '#FFF8DC',      # Vanilla cream
            'strawberry': '#FFB6C1',   # Light pink
            'chocolate': '#D2691E',    # Chocolate brown
            'mint': '#98FB98',         # Mint green
            'caramel': '#DEB887',      # Caramel tan
            'berry': '#DA70D6',        # Berry purple
            'cream': '#FFFACD'         # Light cream
        }
        
        # Configure custom styles with ice cream colors
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground='#8B4513', background=colors['vanilla'])
        style.configure('Header.TLabelframe.Label', font=('Arial', 11, 'bold'), foreground='#8B4513')
        style.configure('Connection.TLabelframe', background=colors['vanilla'])
        style.configure('Generation.TLabelframe', background=colors['mint'])
        style.configure('Range.TLabelframe', background=colors['strawberry'])
        style.configure('Weather.TLabelframe', background=colors['caramel'])
        style.configure('Log.TLabelframe', background=colors['cream'])
        
        # Custom button styles
        style.configure('Connect.TButton', background=colors['mint'], font=('Arial', 10, 'bold'))
        style.configure('Generate.TButton', background=colors['strawberry'], font=('Arial', 10, 'bold'))
        style.configure('Range.TButton', background=colors['berry'], font=('Arial', 10, 'bold'))
        style.configure('Weather.TButton', background=colors['caramel'], font=('Arial', 10, 'bold'))
        style.configure('Schema.TButton', background=colors['mint'], font=('Arial', 10, 'bold'))
        
        # Force button styling to override theme defaults
        style.map('Schema.TButton',
                 background=[('active', '#8B4513'), ('pressed', '#654321')],
                 foreground=[('active', 'white'), ('pressed', 'white')])
        style.map('Connect.TButton',
                 background=[('active', '#90EE90'), ('pressed', '#7CFC00')])
        style.map('Generate.TButton',
                 background=[('active', '#FFC0CB'), ('pressed', '#FF69B4')])
        style.map('Range.TButton',
                 background=[('active', '#DDA0DD'), ('pressed', '#BA55D3')])
        style.map('Weather.TButton',
                 background=[('active', '#F4A460'), ('pressed', '#D2691E')])
        
        self.grid(sticky="nsew")
        self.configure(style='Main.TFrame')
        
        # Configure main grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        # Main container with ice cream background
        main_container = ttk.Frame(self)
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_container.configure(style='Main.TFrame')
        
        # Configure main container grid - 3 columns for side-by-side layout
        main_container.columnconfigure(0, weight=1)  # Left column
        main_container.columnconfigure(1, weight=1)  # Middle column  
        main_container.columnconfigure(2, weight=1)  # Right column
        main_container.rowconfigure(2, weight=1)     # Log section expandable

        # Title spanning all columns
        title_label = ttk.Label(main_container, text="🍦 Ice Cream Database Generator", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # LEFT COLUMN - Connection Settings
        cf = ttk.LabelFrame(main_container, text="🔗 Connection Settings", 
                           style='Header.TLabelframe')
        cf.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        cf.columnconfigure(1, weight=1)

        # Server
        ttk.Label(cf, text="Server:").grid(row=0, column=0, sticky="e", pady=5, padx=(10, 5))
        self.server_var = tk.StringVar(value="172.21.20.35")
        server_entry = ttk.Entry(cf, textvariable=self.server_var, font=('Arial', 10), width=25)
        server_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=(0, 10))

        # Database
        ttk.Label(cf, text="Database:").grid(row=1, column=0, sticky="e", pady=5, padx=(10, 5))
        self.db_var = tk.StringVar(value="IceCreamShop")
        db_entry = ttk.Entry(cf, textvariable=self.db_var, font=('Arial', 10), width=25)
        db_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(0, 10))

        # Schema
        ttk.Label(cf, text="Schema:").grid(row=2, column=0, sticky="e", pady=5, padx=(10, 5))
        self.schema_var = tk.StringVar(value="dbo")
        schema_entry = ttk.Entry(cf, textvariable=self.schema_var, font=('Arial', 10), width=15)
        schema_entry.grid(row=2, column=1, sticky="w", pady=5, padx=(0, 10))

        # Driver
        ttk.Label(cf, text="Driver:").grid(row=3, column=0, sticky="e", pady=5, padx=(10, 5))
        drivers = pyodbc.drivers()
        preferred_driver = "ODBC Driver 17 for SQL Server"
        if preferred_driver in drivers:
            default_driver = preferred_driver
        else:
            default_driver = next((d for d in drivers if "ODBC Driver" in d), drivers[-1] if drivers else "")
        
        self.driver_cb = ttk.Combobox(cf, values=drivers, state="readonly", font=('Arial', 10), width=22)
        self.driver_cb.set(default_driver)
        self.driver_cb.grid(row=3, column=1, sticky="ew", pady=5, padx=(0, 10))

        # User
        ttk.Label(cf, text="Username:").grid(row=4, column=0, sticky="e", pady=5, padx=(10, 5))
        self.user_var = tk.StringVar()
        user_entry = ttk.Entry(cf, textvariable=self.user_var, font=('Arial', 10), width=25)
        user_entry.grid(row=4, column=1, sticky="ew", pady=5, padx=(0, 10))

        # Password
        ttk.Label(cf, text="Password:").grid(row=5, column=0, sticky="e", pady=5, padx=(10, 5))
        self.pwd_var = tk.StringVar()
        pwd_entry = ttk.Entry(cf, textvariable=self.pwd_var, show="*", font=('Arial', 10), width=25)
        pwd_entry.grid(row=5, column=1, sticky="ew", pady=5, padx=(0, 10))

        # Connection Options
        options_frame = ttk.Frame(cf)
        options_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        self.encrypt_var = tk.BooleanVar(value=True)
        encrypt_cb = ttk.Checkbutton(options_frame, text="🔒 Encrypt", variable=self.encrypt_var)
        encrypt_cb.grid(row=0, column=0, sticky="w", padx=(10, 20))
        
        self.trust_var = tk.BooleanVar(value=True)
        trust_cb = ttk.Checkbutton(options_frame, text="🛡️ Trust Cert", variable=self.trust_var)
        trust_cb.grid(row=0, column=1, sticky="w")

        # Connection action buttons
        conn_buttons = ttk.Frame(cf)
        conn_buttons.grid(row=7, column=0, columnspan=2, pady=(15, 10))
        
        test_conn_btn = ttk.Button(conn_buttons, text="🔍 Test Connection", 
                                  command=self.on_test_connection, style='Connect.TButton')
        test_conn_btn.grid(row=0, column=0, padx=(0, 10))
        
        recreate_btn = ttk.Button(conn_buttons, text="🔄 Recreate Schema", 
                                 command=self.on_recreate, style='Schema.TButton')
        recreate_btn.grid(row=0, column=1)

        # MIDDLE COLUMN - Data Generation & Date Range
        middle_frame = ttk.Frame(main_container)
        middle_frame.grid(row=1, column=1, sticky="nsew", padx=10)
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.rowconfigure(2, weight=1)  # Make date range section expandable

        # Data Generation Frame
        rf = ttk.LabelFrame(middle_frame, text="📊 Basic Data Generation", 
                           style='Header.TLabelframe')
        rf.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        rf.columnconfigure(1, weight=1)

        self.row_counts = {}
        table_icons = {"Customers": "👥", "Flavors": "🍨", "Toppings": "🎂", "Orders": "📋"}
        
        for i, tbl in enumerate(["Customers", "Flavors", "Toppings", "Orders"]):
            icon_label = ttk.Label(rf, text=f"{table_icons[tbl]} {tbl}:")
            icon_label.grid(row=i, column=0, sticky="e", pady=5, padx=(10, 5))
            
            v = tk.IntVar(value=10 if tbl == "Customers" else 15 if tbl in ["Flavors", "Toppings"] else 25)
            count_entry = ttk.Entry(rf, textvariable=v, font=('Arial', 10), width=8)
            count_entry.grid(row=i, column=1, sticky="w", pady=5)
            self.row_counts[tbl] = v

        # Add inventory control
        inventory_icon_label = ttk.Label(rf, text="📦 Inventory:")
        inventory_icon_label.grid(row=4, column=0, sticky="e", pady=5, padx=(10, 5))
        
        self.inventory_var = tk.IntVar(value=1)  # Default to populate inventory
        inventory_cb = ttk.Checkbutton(rf, text="Populate from Flavors/Toppings", variable=self.inventory_var)
        inventory_cb.grid(row=4, column=1, sticky="w", pady=5)

        # Basic generation action button
        gen_buttons = ttk.Frame(rf)
        gen_buttons.grid(row=5, column=0, columnspan=2, pady=(15, 10))
        
        generate_btn = ttk.Button(gen_buttons, text="⚡ Generate Basic Data", 
                                 command=self.on_generate, style='Generate.TButton')
        generate_btn.grid(row=0, column=0)

        # Yearly Orders Section (separate from basic data)
        yearly_frame_section = ttk.LabelFrame(middle_frame, text="📅 Yearly Order Generation", 
                                             style='Header.TLabelframe')
        yearly_frame_section.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        yearly_frame_section.columnconfigure(1, weight=1)

        # Yearly orders control
        yearly_icon_label = ttk.Label(yearly_frame_section, text="📅 Order Count:")
        yearly_icon_label.grid(row=0, column=0, sticky="e", pady=5, padx=(10, 5))
        
        yearly_controls = ttk.Frame(yearly_frame_section)
        yearly_controls.grid(row=0, column=1, sticky="w", pady=5)
        
        self.yearly_orders_var = tk.IntVar(value=500)
        yearly_count_entry = ttk.Entry(yearly_controls, textvariable=self.yearly_orders_var, font=('Arial', 10), width=8)
        yearly_count_entry.grid(row=0, column=0, sticky="w")
        
        year_label = ttk.Label(yearly_controls, text="Year:")
        year_label.grid(row=0, column=1, sticky="w", padx=(10, 5))
        
        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year + 1))  # Only past and current year
        self.year_var = tk.IntVar(value=current_year)
        year_combo = ttk.Combobox(yearly_controls, textvariable=self.year_var, values=years, 
                                 state="readonly", font=('Arial', 10), width=8)
        year_combo.grid(row=0, column=2, sticky="w")

        # Yearly generation action button
        yearly_gen_buttons = ttk.Frame(yearly_frame_section)
        yearly_gen_buttons.grid(row=1, column=0, columnspan=2, pady=(15, 10))
        
        yearly_btn = ttk.Button(yearly_gen_buttons, text="📅 Generate Yearly Orders", 
                               command=self.on_generate_yearly, style='Generate.TButton')
        yearly_btn.grid(row=0, column=0)

        # Date Range Orders Section
        range_frame = ttk.LabelFrame(middle_frame, text="📆 Date Range Orders", 
                                    style='Header.TLabelframe')
        range_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 0))
        range_frame.columnconfigure(1, weight=1)

        # Order count for date range
        range_count_label = ttk.Label(range_frame, text="📋 Order Count:")
        range_count_label.grid(row=0, column=0, sticky="e", pady=5, padx=(10, 5))
        
        self.range_orders_var = tk.IntVar(value=50)
        range_count_entry = ttk.Entry(range_frame, textvariable=self.range_orders_var, font=('Arial', 10), width=8)
        range_count_entry.grid(row=0, column=1, sticky="w", pady=5)

        # Start date selection
        start_label = ttk.Label(range_frame, text="📅 Start Date:")
        start_label.grid(row=1, column=0, sticky="e", pady=5, padx=(10, 5))
        
        start_date_frame = ttk.Frame(range_frame)
        start_date_frame.grid(row=1, column=1, sticky="w", pady=5)
        
        # Only allow past and current years for date range
        range_years = list(range(current_year - 3, current_year + 1))
        self.start_year_var = tk.IntVar(value=current_year)
        start_year_combo = ttk.Combobox(start_date_frame, textvariable=self.start_year_var, values=range_years, 
                                       state="readonly", font=('Arial', 10), width=6)
        start_year_combo.grid(row=0, column=0, sticky="w")
        
        months = [("Jan", 1), ("Feb", 2), ("Mar", 3), ("Apr", 4), ("May", 5), ("Jun", 6),
                 ("Jul", 7), ("Aug", 8), ("Sep", 9), ("Oct", 10), ("Nov", 11), ("Dec", 12)]
        month_values = [f"{name} ({num:02d})" for name, num in months]
        self.start_month_var = tk.StringVar(value=f"Jan (01)")
        start_month_combo = ttk.Combobox(start_date_frame, textvariable=self.start_month_var, values=month_values,
                                        state="readonly", font=('Arial', 10), width=8)
        start_month_combo.grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        days = [f"{i:02d}" for i in range(1, 32)]
        self.start_day_var = tk.StringVar(value="01")
        start_day_combo = ttk.Combobox(start_date_frame, textvariable=self.start_day_var, values=days,
                                      state="readonly", font=('Arial', 10), width=4)
        start_day_combo.grid(row=0, column=2, sticky="w", padx=(5, 0))

        # End date selection
        end_label = ttk.Label(range_frame, text="📅 End Date:")
        end_label.grid(row=2, column=0, sticky="e", pady=5, padx=(10, 5))
        
        end_date_frame = ttk.Frame(range_frame)
        end_date_frame.grid(row=2, column=1, sticky="w", pady=5)
        
        self.end_year_var = tk.IntVar(value=current_year)
        end_year_combo = ttk.Combobox(end_date_frame, textvariable=self.end_year_var, values=range_years, 
                                     state="readonly", font=('Arial', 10), width=6)
        end_year_combo.grid(row=0, column=0, sticky="w")
        
        # Set default end date to today
        today = datetime.now()
        self.end_month_var = tk.StringVar(value=f"{today.strftime('%b')} ({today.month:02d})")
        end_month_combo = ttk.Combobox(end_date_frame, textvariable=self.end_month_var, values=month_values,
                                      state="readonly", font=('Arial', 10), width=8)
        end_month_combo.grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        self.end_day_var = tk.StringVar(value=f"{today.day:02d}")
        end_day_combo = ttk.Combobox(end_date_frame, textvariable=self.end_day_var, values=days,
                                    state="readonly", font=('Arial', 10), width=4)
        end_day_combo.grid(row=0, column=2, sticky="w", padx=(5, 0))

        # Bind events to update end date options based on current date
        def update_end_date_options(*args):
            """Update end date options to prevent future dates."""
            today = datetime.now().date()
            selected_year = self.end_year_var.get()
            selected_month_str = self.end_month_var.get()
            
            if selected_month_str and '(' in selected_month_str:
                selected_month = int(selected_month_str.split('(')[1].split(')')[0])
                
                # If selected year/month is current year/month, limit days to today
                if selected_year == today.year and selected_month == today.month:
                    available_days = [f"{i:02d}" for i in range(1, today.day + 1)]
                    end_day_combo.configure(values=available_days)
                    # If current day selection is beyond today, reset to today
                    current_day = int(self.end_day_var.get())
                    if current_day > today.day:
                        self.end_day_var.set(f"{today.day:02d}")
                else:
                    # Normal day range for past months
                    end_day_combo.configure(values=days)
        
        end_year_combo.bind('<<ComboboxSelected>>', update_end_date_options)
        end_month_combo.bind('<<ComboboxSelected>>', update_end_date_options)

        # Quick preset buttons
        preset_label = ttk.Label(range_frame, text="🎯 Quick Presets:")
        preset_label.grid(row=3, column=0, sticky="e", pady=5, padx=(10, 5))
        
        preset_frame = ttk.Frame(range_frame)
        preset_frame.grid(row=3, column=1, sticky="w", pady=5)
        
        today_btn = ttk.Button(preset_frame, text="Today", command=self.set_today_range, width=8)
        today_btn.grid(row=0, column=0, padx=(0, 5))
        
        week_btn = ttk.Button(preset_frame, text="This Week", command=self.set_week_range, width=10)
        week_btn.grid(row=0, column=1, padx=(0, 5))
        
        month_btn = ttk.Button(preset_frame, text="This Month", command=self.set_month_range, width=10)
        month_btn.grid(row=0, column=2, padx=(0, 5))
        
        summer_btn = ttk.Button(preset_frame, text="Summer", command=self.set_summer_range, width=8)
        summer_btn.grid(row=0, column=3)

        # Add inventory checkbox to yearly section
        yearly_inventory_label = ttk.Label(yearly_frame_section, text="📦 Inventory:")
        yearly_inventory_label.grid(row=2, column=0, sticky="e", pady=5, padx=(10, 5))
        
        self.yearly_inventory_var = tk.IntVar(value=0)  # Default unchecked for yearly
        yearly_inventory_cb = ttk.Checkbutton(yearly_frame_section, text="Update inventory after generation", 
                                             variable=self.yearly_inventory_var)
        yearly_inventory_cb.grid(row=2, column=1, sticky="w", pady=5)

        # Update yearly button grid position
        yearly_gen_buttons.grid(row=3, column=0, columnspan=2, pady=(15, 10))

        # Add inventory checkbox to range section  
        range_inventory_label = ttk.Label(range_frame, text="📦 Inventory:")
        range_inventory_label.grid(row=4, column=0, sticky="e", pady=5, padx=(10, 5))
        
        self.range_inventory_var = tk.IntVar(value=0)  # Default unchecked for range
        range_inventory_cb = ttk.Checkbutton(range_frame, text="Update inventory after generation", 
                                            variable=self.range_inventory_var)
        range_inventory_cb.grid(row=4, column=1, sticky="w", pady=5)

        # Date range action button
        range_buttons = ttk.Frame(range_frame)
        range_buttons.grid(row=5, column=0, columnspan=2, pady=(15, 10))
        
        range_btn = ttk.Button(range_buttons, text="📆 Generate Date Range Orders", 
                              command=self.on_generate_date_range, style='Range.TButton')
        range_btn.grid(row=0, column=0)

        # RIGHT COLUMN - Weather API Test
        test_frame = ttk.LabelFrame(main_container, text="🌡️ Test Weather API", 
                                   style='Header.TLabelframe')
        test_frame.grid(row=1, column=2, sticky="nsew", padx=(10, 0), pady=(0, 15))
        test_frame.columnconfigure(1, weight=1)

        # Test date selection
        test_label = ttk.Label(test_frame, text="Test Date:")
        test_label.grid(row=0, column=0, sticky="e", pady=8, padx=(10, 5))
        
        # Date input frame
        date_frame = ttk.Frame(test_frame)
        date_frame.grid(row=0, column=1, sticky="w", pady=8, padx=(0, 10))
        
        # Year selection for test
        test_years = list(range(current_year - 3, current_year + 2))
        self.test_year_var = tk.IntVar(value=current_year)
        test_year_combo = ttk.Combobox(date_frame, textvariable=self.test_year_var, values=test_years, 
                                      state="readonly", font=('Arial', 10), width=6)
        test_year_combo.grid(row=0, column=0, sticky="w")
        
        self.test_month_var = tk.StringVar(value=f"Jan (01)")
        test_month_combo = ttk.Combobox(date_frame, textvariable=self.test_month_var, values=month_values,
                                       state="readonly", font=('Arial', 10), width=8)
        test_month_combo.grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        self.test_day_var = tk.StringVar(value="01")
        test_day_combo = ttk.Combobox(date_frame, textvariable=self.test_day_var, values=days,
                                     state="readonly", font=('Arial', 10), width=4)
        test_day_combo.grid(row=0, column=2, sticky="w", padx=(5, 0))

        # Weather test action button
        weather_buttons = ttk.Frame(test_frame)
        weather_buttons.grid(row=1, column=0, columnspan=2, pady=(15, 10))
        
        test_btn = ttk.Button(weather_buttons, text="🔍 Test Weather API", 
                             command=self.on_test_weather_api, style='Weather.TButton')
        test_btn.grid(row=0, column=0)

        # Log Frame spanning all columns
        lf = ttk.LabelFrame(main_container, text="📝 Activity Log", 
                           style='Header.TLabelframe')
        lf.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(15, 0))
        lf.columnconfigure(0, weight=1)
        lf.rowconfigure(0, weight=1)
        
        self.log = ScrolledText(lf, state='disabled', height=12, font=('Consolas', 10),
                               wrap=tk.WORD, bg='#FFFACD', fg='#8B4513')  # Cream background, brown text
        self.log.grid(sticky="nsew", padx=5, pady=5)

        # Add some initial welcome message
        self.log_msg("🍦 Welcome to Ice Cream Database Generator!")
        self.log_msg("Configure your connection settings and generate sample data.")
        self.log_msg(f"📊 Available drivers: {len(drivers)} found")

    def log_msg(self, msg):
        self.log.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.insert('end', f"[{timestamp}] {msg}\n")
        self.log.yview('end')
        self.log.config(state='disabled')
        # Update the UI
        self.update_idletasks()

    def on_recreate(self):
        self.log_msg("Recreating schema…")
        try:
            cn = connect_to_db(
                self.server_var.get(), self.db_var.get(), self.user_var.get(), self.pwd_var.get(),
                self.driver_cb.get(), self.encrypt_var.get(), self.trust_var.get()
            )
            msg = recreate_schema(cn, self.schema_var.get())
            cn.close()
            self.log_msg(msg)
            messagebox.showinfo("Success", msg)
        except Exception as e:
            self.log_msg(f"Error: {e}")
            messagebox.showerror("Schema Error", str(e))

    def on_generate(self):
        self.log_msg("Generating data…")
        try:
            cn = connect_to_db(
                self.server_var.get(), self.db_var.get(), self.user_var.get(), self.pwd_var.get(),
                self.driver_cb.get(), self.encrypt_var.get(), self.trust_var.get()
            )
            cur = cn.cursor()
            schema = self.schema_var.get()
            cur.execute(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=? AND TABLE_NAME='Customers'", schema
            )
            if cur.fetchone()[0] == 0:
                self.log_msg("Schema missing—recreating…")
                recreate_schema(cn, schema)
                self.log_msg("Schema recreated on-the-fly.")

            if self.row_counts['Customers'].get():
                generate_customers(cur, schema, self.row_counts['Customers'].get())
                self.log_msg(f"Inserted {self.row_counts['Customers'].get()} customers")
            if self.row_counts['Flavors'].get():
                generate_flavors(cur, schema, self.row_counts['Flavors'].get())
                self.log_msg(f"Inserted {self.row_counts['Flavors'].get()} flavors")
            if self.row_counts['Toppings'].get():
                generate_toppings(cur, schema, self.row_counts['Toppings'].get())
                self.log_msg(f"Inserted {self.row_counts['Toppings'].get()} toppings")
            if self.row_counts['Orders'].get():
                stats = generate_detailed_orders(cur, schema, self.row_counts['Orders'].get())
                self.log_msg(f"Generated {stats['orders']} orders with {stats['details']} order details and {stats['toppings']} toppings")

            # Generate inventory if requested
            if self.inventory_var.get():
                inventory_count = generate_inventory(cur, schema)
                self.log_msg(f"Generated {inventory_count} inventory records")

            cn.commit()
            cn.close()
            messagebox.showinfo("Success", "Data generated successfully.")
        except Exception as e:
            self.log_msg(f"Error: {e}")
            messagebox.showerror("Error", str(e))

    def on_generate_yearly(self):
        self.log_msg("Generating yearly orders…")
        try:
            cn = connect_to_db(
                self.server_var.get(), self.db_var.get(), self.user_var.get(), self.pwd_var.get(),
                self.driver_cb.get(), self.encrypt_var.get(), self.trust_var.get()
            )
            cur = cn.cursor()
            schema = self.schema_var.get()
            
            # Check if schema exists
            cur.execute(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=? AND TABLE_NAME='Orders'", schema
            )
            if cur.fetchone()[0] == 0:
                self.log_msg("Schema missing—recreating…")
                recreate_schema(cn, schema)
                self.log_msg("Schema recreated on-the-fly.")

            self.log_msg(f"Fetching Boston weather data for {self.year_var.get()}…")
            weather_data = get_boston_weather_data(self.year_var.get(), self.log_msg)
            
            if weather_data:
                # Show sample temperature info
                temps = list(weather_data.values())
                if temps:
                    avg_temp = sum(temps) / len(temps)
                    max_temp = max(temps)
                    min_temp = min(temps)
                    
                    # Get first and last day temperatures
                    year = self.year_var.get()
                    first_day = f"{year}-01-01"
                    last_day = f"{year}-12-31"
                    
                    first_temp = weather_data.get(first_day)
                    last_temp = weather_data.get(last_day)
                    
                    # Convert to Celsius for display
                    if first_temp is not None:
                        first_temp_c = round((first_temp - 32) * 5/9, 1)
                        self.log_msg(f"The avg temp on 1.1.{year} was {first_temp_c}°C ({first_temp:.1f}°F)")
                    
                    if last_temp is not None:
                        last_temp_c = round((last_temp - 32) * 5/9, 1)
                        self.log_msg(f"The avg temp on 31.12.{year} was {last_temp_c}°C ({last_temp:.1f}°F)")
                    
                    self.log_msg(f"Temperature range: {min_temp:.1f}°F to {max_temp:.1f}°F (avg: {avg_temp:.1f}°F)")
            else:
                self.log_msg("Warning: No weather data available, using default patterns")
            
            self.log_msg("Generating orders based on weather patterns and buying habits…")
            orders_generated = generate_yearly_orders(cur, schema, self.yearly_orders_var.get(), self.year_var.get(), weather_data)
            
            self.log_msg(f"Inserted {orders_generated} orders for year {self.year_var.get()}")
            if weather_data:
                self.log_msg("Orders distributed based on Boston temperature data and seasonal patterns")

            # Generate inventory if requested
            if self.yearly_inventory_var.get():
                inventory_count = generate_inventory(cur, schema)
                self.log_msg(f"Updated {inventory_count} inventory records")

            cn.commit()
            cn.close()
            messagebox.showinfo("Success", f"Generated {orders_generated} weather-influenced orders for {self.year_var.get()}.")
        except Exception as e:
            self.log_msg(f"Error: {e}")
            messagebox.showerror("Error", str(e))

    def on_test_weather_api(self):
        self.log_msg("🔍 Testing weather API for single date…")
        try:
            year = self.test_year_var.get()
            # Parse month from "Jan (01)" format
            month_text = self.test_month_var.get()
            month = int(month_text.split('(')[1].split(')')[0])  # Extract "01" from "Jan (01)"
            day = int(self.test_day_var.get())
            
            # Validate date
            test_date = f"{year}-{month:02d}-{day:02d}"
            try:
                # Validate the date is real (e.g., not Feb 30)
                datetime.strptime(test_date, '%Y-%m-%d')
            except ValueError:
                self.log_msg(f"❌ Invalid date: {test_date}")
                messagebox.showerror("Invalid Date", f"The date {test_date} is not valid.")
                return
            
            self.log_msg(f"🔍 Testing API for specific date: {test_date}")
            
            # Use the new single-day weather function
            temp_f = get_single_day_weather_data(year, month, day, self.log_msg)
            
            if temp_f is not None:
                temp_c = round((temp_f - 32) * 5/9, 1)
                
                self.log_msg(f"✅ Success! Temperature on {test_date}: {temp_f:.1f}°F ({temp_c}°C)")
                
                # Show order multiplier that would be used
                multiplier = calculate_order_multiplier(temp_f)
                self.log_msg(f"🍦 Order multiplier for this temperature: {multiplier:.2f}x")
                
                # Determine data source
                current_year = datetime.now().year
                data_source = "Generated Pattern" if year > current_year else "Historical API"
                
                messagebox.showinfo("API Test Success", 
                                   f"Date: {test_date}\n"
                                   f"Temperature: {temp_f:.1f}°F ({temp_c}°C)\n"
                                   f"Data source: {data_source}\n"
                                   f"Order multiplier: {multiplier:.2f}x")
            else:
                self.log_msg(f"❌ No temperature data found for {test_date}")
                messagebox.showwarning("No Data", f"No temperature data available for {test_date}")
                
        except Exception as e:
            self.log_msg(f"❌ API Test Error: {e}")
            messagebox.showerror("API Test Error", str(e))

    def on_test_connection(self):
        """Test database connection without making any changes."""
        self.log_msg("🔍 Testing database connection…")
        try:
            cn = connect_to_db(
                self.server_var.get(), self.db_var.get(), self.user_var.get(), self.pwd_var.get(),
                self.driver_cb.get(), self.encrypt_var.get(), self.trust_var.get()
            )
            
            # Test basic connection with a simple query
            cursor = cn.cursor()
            cursor.execute("SELECT @@VERSION")
            version_info = cursor.fetchone()[0]
            
            # Get database name
            cursor.execute("SELECT DB_NAME()")
            db_name = cursor.fetchone()[0]
            
            cn.close()
            
            # Extract SQL Server version (first part)
            version_short = version_info.split('\n')[0] if '\n' in version_info else version_info[:100]
            
            self.log_msg(f"✅ Connection successful!")
            self.log_msg(f"📊 Database: {db_name}")
            self.log_msg(f"🔧 Server: {version_short}")
            
            messagebox.showinfo("Connection Test", 
                               f"✅ Connection successful!\n\n"
                               f"Database: {db_name}\n"
                               f"Server: {self.server_var.get()}\n"
                               f"Schema: {self.schema_var.get()}")
        except Exception as e:
            self.log_msg(f"❌ Connection failed: {e}")
            messagebox.showerror("Connection Test Failed", 
                               f"❌ Could not connect to database.\n\n"
                               f"Error: {str(e)}\n\n"
                               f"Please check your connection settings.")

    def set_today_range(self):
        today = datetime.now()
        self.start_year_var.set(today.year)
        self.start_month_var.set(f"{today.strftime('%b')} ({today.month:02d})")
        self.start_day_var.set(today.strftime('%d'))
        self.end_year_var.set(today.year)
        self.end_month_var.set(f"{today.strftime('%b')} ({today.month:02d})")
        self.end_day_var.set(today.strftime('%d'))

    def set_week_range(self):
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        self.start_year_var.set(start_of_week.year)
        self.start_month_var.set(f"{start_of_week.strftime('%b')} ({start_of_week.month:02d})")
        self.start_day_var.set(start_of_week.strftime('%d'))
        self.end_year_var.set(today.year)
        self.end_month_var.set(f"{today.strftime('%b')} ({today.month:02d})")
        self.end_day_var.set(today.strftime('%d'))

    def set_month_range(self):
        today = datetime.now()
        start_of_month = datetime(today.year, today.month, 1)
        self.start_year_var.set(start_of_month.year)
        self.start_month_var.set(f"{start_of_month.strftime('%b')} ({start_of_month.month:02d})")
        self.start_day_var.set(start_of_month.strftime('%d'))
        self.end_year_var.set(today.year)
        self.end_month_var.set(f"{today.strftime('%b')} ({today.month:02d})")
        self.end_day_var.set(today.strftime('%d'))

    def set_summer_range(self):
        today = datetime.now()
        start_of_summer = datetime(today.year, 6, 1)
        self.start_year_var.set(start_of_summer.year)
        self.start_month_var.set(f"{start_of_summer.strftime('%b')} ({start_of_summer.month:02d})")
        self.start_day_var.set(start_of_summer.strftime('%d'))
        self.end_year_var.set(today.year)
        self.end_month_var.set(f"{today.strftime('%b')} ({today.month:02d})")
        self.end_day_var.set(today.strftime('%d'))

    def on_generate_date_range(self):
        self.log_msg("Generating date range orders…")
        try:
            cn = connect_to_db(
                self.server_var.get(), self.db_var.get(), self.user_var.get(), self.pwd_var.get(),
                self.driver_cb.get(), self.encrypt_var.get(), self.trust_var.get()
            )
            cur = cn.cursor()
            schema = self.schema_var.get()
            
            # Check if schema exists
            cur.execute(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=? AND TABLE_NAME='Orders'", schema
            )
            if cur.fetchone()[0] == 0:
                self.log_msg("Schema missing—recreating…")
                recreate_schema(cn, schema)
                self.log_msg("Schema recreated on-the-fly.")

            # Parse start date
            start_year = self.start_year_var.get()
            start_month = self.start_month_var.get().split('(')[1].split(')')[0]  # Extract "01" from "Jan (01)"
            start_day = self.start_day_var.get()
            start_date_str = f"{start_year}-{start_month}-{start_day}"
            
            # Parse end date
            end_year = self.end_year_var.get()
            end_month = self.end_month_var.get().split('(')[1].split(')')[0]  # Extract "12" from "Dec (12)"
            end_day = self.end_day_var.get()
            end_date_str = f"{end_year}-{end_month}-{end_day}"
            
            # Validate dates
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError as ve:
                self.log_msg(f"❌ Invalid date format: {ve}")
                messagebox.showerror("Invalid Date", f"Invalid date format: {ve}")
                return
            
            # Check for future dates
            today = datetime.now().date()
            if start_date.date() > today:
                self.log_msg("❌ Start date cannot be in the future")
                messagebox.showerror("Invalid Date Range", "Start date cannot be in the future. Please select a past or current date.")
                return
            
            if end_date.date() > today:
                self.log_msg("❌ End date cannot be in the future")
                messagebox.showerror("Invalid Date Range", "End date cannot be in the future. Please select a past or current date.")
                return
            
            if start_date > end_date:
                self.log_msg("❌ Start date must be before or equal to end date")
                messagebox.showerror("Invalid Date Range", "Start date must be before or equal to end date")
                return
            
            days_in_range = (end_date - start_date).days + 1
            self.log_msg(f"📅 Date range: {start_date_str} to {end_date_str} ({days_in_range} days)")

            # Get weather data for the specific date range
            self.log_msg(f"🌡️ Fetching weather data for date range: {start_date_str} to {end_date_str}")
            weather_data = get_boston_weather_data_range(start_date, end_date, self.log_msg)
            
            if weather_data:
                # Show temperature range for the selected date range
                range_temps = []
                current_date = start_date
                while current_date <= end_date:
                    date_str = current_date.strftime('%Y-%m-%d')
                    if date_str in weather_data:
                        range_temps.append(weather_data[date_str])
                    current_date += timedelta(days=1)
                
                if range_temps:
                    avg_temp = sum(range_temps) / len(range_temps)
                    max_temp = max(range_temps)
                    min_temp = min(range_temps)
                    
                    # Show first and last day temperatures
                    first_temp = weather_data.get(start_date_str)
                    last_temp = weather_data.get(end_date_str)
                    
                    if first_temp is not None:
                        first_temp_c = round((first_temp - 32) * 5/9, 1)
                        self.log_msg(f"🌡️ Start date temp: {first_temp_c}°C ({first_temp:.1f}°F)")
                    
                    if last_temp is not None:
                        last_temp_c = round((last_temp - 32) * 5/9, 1)
                        self.log_msg(f"🌡️ End date temp: {last_temp_c}°C ({last_temp:.1f}°F)")
                    
                    self.log_msg(f"🌡️ Temperature range: {min_temp:.1f}°F to {max_temp:.1f}°F (avg: {avg_temp:.1f}°F)")
            else:
                self.log_msg("⚠️ No weather data available, using default patterns")
            
            self.log_msg("🍦 Generating orders based on weather patterns and buying habits…")
            orders_generated = generate_date_range_orders(cur, schema, self.range_orders_var.get(), 
                                                         start_date_str, end_date_str, weather_data)
            
            self.log_msg(f"✅ Generated {orders_generated} orders for date range {start_date_str} to {end_date_str}")
            if weather_data:
                self.log_msg("📊 Orders distributed based on Boston temperature data and seasonal patterns")

            # Generate inventory if requested
            if self.range_inventory_var.get():
                inventory_count = generate_inventory(cur, schema)
                self.log_msg(f"Updated {inventory_count} inventory records")

            cn.commit()
            cn.close()
            messagebox.showinfo("Success", f"Generated {orders_generated} weather-influenced orders for date range {start_date_str} to {end_date_str}.")
        except Exception as e:
            self.log_msg(f"❌ Error: {e}")
            messagebox.showerror("Error", str(e))

if __name__ == '__main__':
    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    IceCreamApp(root)
    root.mainloop()
