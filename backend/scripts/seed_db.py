import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, Base, engine
from app.models.order import Order
from app.models.product import Product
from app.models.user_preference import UserPreference

PRODUCTS_DATA = [
    # Honey & Sweeteners (Key benchmark items)
    {
        "name": "Organic Raw Wildflower Honey",
        "description": "100% pure unfiltered raw organic wildflower honey harvested from sustainable apiaries.",
        "category": "Honey & Sweeteners",
        "price": 14.99,
        "is_organic": True,
        "stock": 45,
        "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Standard Clover Honey",
        "description": "Everyday sweet clover honey in an easy-squeeze bear bottle.",
        "category": "Honey & Sweeteners",
        "price": 6.99,
        "is_organic": False,
        "stock": 80,
        "image_url": "https://images.unsplash.com/photo-1558642452-9d2a7deb7f62?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Premium Imported Manuka Honey MGO 400+",
        "description": "Authentic New Zealand raw active Manuka honey with powerful natural properties.",
        "category": "Honey & Sweeteners",
        "price": 35.00,
        "is_organic": True,
        "stock": 15,
        "image_url": "https://images.unsplash.com/photo-1587049352847-4a222e784d38?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Pure Maple Syrup Grade A",
        "description": "Rich dark amber 100% pure organic Vermont maple syrup.",
        "category": "Honey & Sweeteners",
        "price": 12.50,
        "is_organic": True,
        "stock": 35,
        "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Raw Blue Agave Nectar",
        "description": "Low-glycemic plant-based natural liquid sweetener.",
        "category": "Honey & Sweeteners",
        "price": 8.99,
        "is_organic": False,
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80",
    },

    # Pantry & Grains
    {
        "name": "Organic Rolled Oats",
        "description": "Gluten-free certified organic whole grain rolled oats for creamy morning oatmeal.",
        "category": "Pantry & Grains",
        "price": 4.50,
        "is_organic": True,
        "stock": 100,
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Standard Quick 1-Minute Oats",
        "description": "Fast-cooking fortified rolled oats.",
        "category": "Pantry & Grains",
        "price": 2.99,
        "is_organic": False,
        "stock": 120,
        "image_url": "https://images.unsplash.com/photo-1517093157656-b9ec91b3ba71?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Royal White Quinoa",
        "description": "High-protein ancient Andean grain, pre-washed and saponin-free.",
        "category": "Pantry & Grains",
        "price": 5.99,
        "is_organic": True,
        "stock": 60,
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Aromatic Jasmine Rice",
        "description": "Long-grain fragrant Thai jasmine rice.",
        "category": "Pantry & Grains",
        "price": 4.29,
        "is_organic": False,
        "stock": 90,
        "image_url": "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Sprouted Brown Rice",
        "description": "Nutrient-dense GABA germinated brown rice.",
        "category": "Pantry & Grains",
        "price": 6.49,
        "is_organic": True,
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Gluten-Free Brown Rice Penne Pasta",
        "description": "Classic Italian style gluten-free penne made of 100% whole grain brown rice.",
        "category": "Pantry & Grains",
        "price": 3.89,
        "is_organic": True,
        "stock": 75,
        "image_url": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Sprouted Whole Wheat Bread",
        "description": "Flourless sprouted 7-grain loaf packed with fiber and enzymes.",
        "category": "Bakery",
        "price": 5.49,
        "is_organic": True,
        "stock": 30,
        "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Artisanal Country Sourdough Loaf",
        "description": "Slow-fermented naturally leavened crispy crust sourdough bread.",
        "category": "Bakery",
        "price": 6.50,
        "is_organic": False,
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?auto=format&fit=crop&w=600&q=80",
    },

    # Dairy & Plant-Based Milk
    {
        "name": "Organic Oat Milk Barista Edition",
        "description": "Creamy plant milk crafted specifically to foam and blend smoothly into hot coffee.",
        "category": "Dairy & Alternatives",
        "price": 4.29,
        "is_organic": True,
        "stock": 65,
        "image_url": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Almond Milk Unsweetened",
        "description": "Light, dairy-free, sugar-free almond milk with calcium & vitamin D.",
        "category": "Dairy & Alternatives",
        "price": 3.49,
        "is_organic": False,
        "stock": 70,
        "image_url": "https://images.unsplash.com/photo-1568651318494-03487f9e8a00?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Whole Grass-Fed Milk 1 Gallon",
        "description": "Pasteurized non-homogenized organic milk from pasture-raised cows.",
        "category": "Dairy & Alternatives",
        "price": 5.99,
        "is_organic": True,
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Greek Yogurt Whole Milk Plain 32oz",
        "description": "Thick triple-strained authentic Greek yogurt with live active probiotics.",
        "category": "Dairy & Alternatives",
        "price": 5.49,
        "is_organic": False,
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Cultured Grass-Fed Butter",
        "description": "Rich golden European-style salted churned organic butter 82% fat.",
        "category": "Dairy & Alternatives",
        "price": 6.99,
        "is_organic": True,
        "stock": 35,
        "image_url": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Standard Unsalted Butter 4 Sticks",
        "description": "Everyday baking butter sticks.",
        "category": "Dairy & Alternatives",
        "price": 3.99,
        "is_organic": False,
        "stock": 80,
        "image_url": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?auto=format&fit=crop&w=600&q=80",
    },

    # Snacks & Healthy Bites
    {
        "name": "Gluten-Free Sea Salt Almond Flour Crackers",
        "description": "Crispy baked crackers made with nutrient-dense almond flour and sea salt.",
        "category": "Snacks",
        "price": 4.79,
        "is_organic": False,
        "stock": 85,
        "image_url": "https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Dry Roasted Salted Almonds 16oz",
        "description": "Crunchy California almonds roasted in small batches with pink Himalayan salt.",
        "category": "Snacks",
        "price": 9.99,
        "is_organic": True,
        "stock": 45,
        "image_url": "https://images.unsplash.com/photo-1508746829417-e6f548d8d6ed?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Dark Chocolate 85% Cacao Bar",
        "description": "Fair-trade single origin single batch dark chocolate bar with intense notes.",
        "category": "Snacks",
        "price": 3.99,
        "is_organic": True,
        "stock": 110,
        "image_url": "https://images.unsplash.com/photo-1549007994-cb92caebd54b?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Chia Seed Granola Clusters",
        "description": "Crunchy whole oat clusters sweetened with coconut sugar and loaded with chia seeds.",
        "category": "Snacks",
        "price": 5.49,
        "is_organic": True,
        "stock": 60,
        "image_url": "https://images.unsplash.com/photo-1517093157656-b9ec91b3ba71?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Classic Sea Salt Kettle Potato Chips",
        "description": "Crunchy thick-cut kettle-cooked chips sprinkled with natural sea salt.",
        "category": "Snacks",
        "price": 2.49,
        "is_organic": False,
        "stock": 95,
        "image_url": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Crispy Baked Kale Chips",
        "description": "Dehydrated organic curly kale seasoned with nutritional yeast and garlic.",
        "category": "Snacks",
        "price": 6.29,
        "is_organic": True,
        "stock": 30,
        "image_url": "https://images.unsplash.com/photo-1524179091875-bf99a9a6fa57?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Antioxidant Trail Mix with Goji & Pecans",
        "description": "Raw walnuts, pecans, pumpkin seeds, dried blueberries, and tart goji berries.",
        "category": "Snacks",
        "price": 7.99,
        "is_organic": False,
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1508746829417-e6f548d8d6ed?auto=format&fit=crop&w=600&q=80",
    },

    # Beverages & Coffee / Tea
    {
        "name": "Organic Ethiopian Yirgacheffe Whole Bean Coffee",
        "description": "Single-origin light roast coffee featuring vibrant jasmine floral and bergamot citrus notes.",
        "category": "Beverages",
        "price": 16.99,
        "is_organic": True,
        "stock": 35,
        "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Standard Medium Roast Ground Coffee 12oz",
        "description": "Balanced everyday Colombian Arabica ground coffee blend.",
        "category": "Beverages",
        "price": 8.49,
        "is_organic": False,
        "stock": 65,
        "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Ceremonial Grade Japanese Matcha 30g",
        "description": "First harvest stone-ground shade-grown green tea leaves from Uji, Kyoto.",
        "category": "Beverages",
        "price": 18.99,
        "is_organic": True,
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1536256263959-770b48d82b0a?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Chamomile Blossom Herbal Tea 20 Bags",
        "description": "Calming caffeine-free whole Egyptian chamomile flowers for peaceful evening relaxation.",
        "category": "Beverages",
        "price": 4.29,
        "is_organic": True,
        "stock": 70,
        "image_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Lime Sparkling Mineral Water 12-Pack",
        "description": "Zero-calorie crisp sparkling water infused with real lime zest essence.",
        "category": "Beverages",
        "price": 5.99,
        "is_organic": False,
        "stock": 55,
        "image_url": "https://images.unsplash.com/photo-1556881286-fc6915169721?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Cold Brew Coffee Concentrate 32oz",
        "description": "Slow steep 18-hour concentrated organic dark brew with ultra-low acidity.",
        "category": "Beverages",
        "price": 9.99,
        "is_organic": True,
        "stock": 30,
        "image_url": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&w=600&q=80",
    },

    # Fresh Produce
    {
        "name": "Organic Hass Avocados 4-Pack Bag",
        "description": "Creamy rich organic avocados harvested at peak ripeness.",
        "category": "Produce",
        "price": 5.99,
        "is_organic": True,
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Fresh Conventional Yellow Bananas 3lb",
        "description": "Naturally sweet energy boost bananas.",
        "category": "Produce",
        "price": 1.49,
        "is_organic": False,
        "stock": 150,
        "image_url": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Crisp Honeycrisp Apples 3lb Bag",
        "description": "Extra juicy and sweet organic autumn harvest apples.",
        "category": "Produce",
        "price": 6.99,
        "is_organic": True,
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Baby Spinach Clamshell 16oz",
        "description": "Triple washed tender organic baby spinach leaves ready to eat.",
        "category": "Produce",
        "price": 4.99,
        "is_organic": True,
        "stock": 45,
        "image_url": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Fresh Blueberries 6oz",
        "description": "Plump and antioxidant-rich organic sweet blueberries.",
        "category": "Produce",
        "price": 4.50,
        "is_organic": True,
        "stock": 35,
        "image_url": "https://images.unsplash.com/photo-1498557850523-fd3d118b962e?auto=format&fit=crop&w=600&q=80",
    },

    # Oils & Condiments
    {
        "name": "Organic Extra Virgin Olive Oil Cold Pressed 500ml",
        "description": "First cold pressed unrefined Mediterranean organic extra virgin olive oil with peppery finish.",
        "category": "Oils & Condiments",
        "price": 13.99,
        "is_organic": True,
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Artisanal Black Truffle Extra Virgin Olive Oil 250ml",
        "description": "Infused with genuine Italian black summer truffles for decadent culinary finishing.",
        "category": "Oils & Condiments",
        "price": 28.00,
        "is_organic": False,
        "stock": 20,
        "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Pure Avocado Oil Spray",
        "description": "High smoke point (500F) propellant-free expeller-pressed avocado cooking oil spray.",
        "category": "Oils & Condiments",
        "price": 7.49,
        "is_organic": False,
        "stock": 60,
        "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Raw Apple Cider Vinegar with Mother",
        "description": "Unfiltered unpasteurized organic apple cider vinegar naturally fermented.",
        "category": "Oils & Condiments",
        "price": 4.99,
        "is_organic": True,
        "stock": 70,
        "image_url": "https://images.unsplash.com/photo-1509722747041-616f39b57569?auto=format&fit=crop&w=600&q=80",
    },
    {
        "name": "Organic Whole Grain Dijon Mustard",
        "description": "Traditional stone-ground tangy Dijon mustard with whole mustard seeds.",
        "category": "Oils & Condiments",
        "price": 3.49,
        "is_organic": True,
        "stock": 65,
        "image_url": "https://images.unsplash.com/photo-1528751014936-863e6e7a319c?auto=format&fit=crop&w=600&q=80",
    },
]


async def seed_database() -> None:
    print("[*] Initializing Database Schema...")
    async with engine.begin() as conn:
        # Create all tables if not existing
        await conn.run_sync(Base.metadata.create_all)
    print("[+] Database tables verified/created successfully.")

    async with AsyncSessionLocal() as session:
        # 1. Seed Products
        product_count_stmt = select(Product)
        existing_products = (await session.execute(product_count_stmt)).scalars().all()

        if not existing_products:
            print(f"[*] Seeding {len(PRODUCTS_DATA)} curated products...")
            for p_data in PRODUCTS_DATA:
                product = Product(**p_data)
                session.add(product)
            await session.commit()
            print(f"[+] Successfully seeded {len(PRODUCTS_DATA)} products.")
        else:
            print(f"[i] Products table already contains {len(existing_products)} items. Skipping product seeding.")

        # 2. Seed User Preferences
        # Alex (user_id = 1): Prefers organic, budget limit $20
        # Bob (user_id = 2): Budget limit $10, no organic requirement
        pref_1 = await session.execute(select(UserPreference).where(UserPreference.user_id == 1))
        if not pref_1.scalar_one_or_none():
            print("[*] Seeding default UserPreference for User 1 (Alex)...")
            user_pref = UserPreference(
                user_id=1,
                prefers_organic=True,
                max_price_limit=20.00,
                notes="User Alex prefers organic items and has a $20 max price limit per item.",
            )
            session.add(user_pref)

        pref_2 = await session.execute(select(UserPreference).where(UserPreference.user_id == 2))
        if not pref_2.scalar_one_or_none():
            print("[*] Seeding default UserPreference for User 2 (Bob)...")
            user_pref_2 = UserPreference(
                user_id=2,
                prefers_organic=False,
                max_price_limit=10.00,
                notes="User Bob prioritizes budget under $10.",
            )
            session.add(user_pref_2)
        await session.commit()

        # 3. Seed Past Orders for User 1
        orders_stmt = select(Order).where(Order.user_id == 1)
        existing_orders = (await session.execute(orders_stmt)).scalars().all()

        if not existing_orders:
            print("[*] Seeding mock order history for User 1...")
            # Query some product ids
            honey_res = await session.execute(
                select(Product).where(Product.name == "Organic Raw Wildflower Honey")
            )
            honey = honey_res.scalar_one_or_none()
            honey_id = honey.id if honey else 1

            oats_res = await session.execute(
                select(Product).where(Product.name == "Organic Rolled Oats")
            )
            oats = oats_res.scalar_one_or_none()
            oats_id = oats.id if oats else 6

            milk_res = await session.execute(
                select(Product).where(Product.name == "Organic Oat Milk Barista Edition")
            )
            milk = milk_res.scalar_one_or_none()
            milk_id = milk.id if milk else 14

            crackers_res = await session.execute(
                select(Product).where(Product.name == "Gluten-Free Sea Salt Almond Flour Crackers")
            )
            crackers = crackers_res.scalar_one_or_none()
            crackers_id = crackers.id if crackers else 20

            order_1 = Order(
                user_id=1,
                items=[
                    {"product_id": honey_id, "name": "Organic Raw Wildflower Honey", "price": 14.99, "quantity": 1},
                    {"product_id": oats_id, "name": "Organic Rolled Oats", "price": 4.50, "quantity": 1},
                ],
                total_amount=19.49,
                status="completed",
                created_at=datetime.now(timezone.utc) - timedelta(days=10),
            )

            order_2 = Order(
                user_id=1,
                items=[
                    {"product_id": milk_id, "name": "Organic Oat Milk Barista Edition", "price": 4.29, "quantity": 2},
                    {"product_id": crackers_id, "name": "Gluten-Free Sea Salt Almond Flour Crackers", "price": 4.79, "quantity": 1},
                ],
                total_amount=13.37,
                status="completed",
                created_at=datetime.now(timezone.utc) - timedelta(days=25),
            )

            session.add_all([order_1, order_2])
            await session.commit()
            print("[+] Successfully seeded 2 past orders for User 1.")
        else:
            print(f"[i] Orders table already contains {len(existing_orders)} orders for User 1.")

    print("\n=======================================================")
    print("Database seeding completed successfully!")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(seed_database())
