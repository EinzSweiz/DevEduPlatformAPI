import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_plan():
    """
    Create a Stripe product and its associated price plan (if it doesn't already exist).
    """
    try:
        # Check if the product already exists by searching by name
        products = stripe.Product.list()
        product_name = "Pro Plan"
        product = next((p for p in products['data'] if p['name'] == product_name), None)

        if not product:
            # Create the product
            product = stripe.Product.create(name=product_name)
            print(f"Created product: {product['id']}")

        # Check if the price for the product exists
        prices = stripe.Price.list(product=product['id'])
        if not prices['data']:
            # Create the price (plan)
            price = stripe.Price.create(
                product=product['id'],
                unit_amount=1000,  # Amount in cents (e.g., $10.00)
                currency="usd",
                recurring={"interval": "month"},  # Monthly billing
            )
            print(f"Created price: {price['id']}")
        else:
            print("Price already exists.")
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_stripe_plan()
