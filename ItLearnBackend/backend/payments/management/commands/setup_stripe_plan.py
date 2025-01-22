import stripe
from django.core.management.base import BaseCommand
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class Command(BaseCommand):
    help = "Setup Stripe product and plan"

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting Stripe plan setup...')
        
        try:
            product_name = 'Pro Plan'
            products = stripe.Product.list()
            product = next((p for p in products['data'] if p['name'] == product_name), None)

            if not product:
                # Create the product
                product = stripe.Product.create(name=product_name)
                self.stdout.write(f"Created product: {product['id']}")

            # Check if the price (plan) exists for the product
            prices = stripe.Price.list(product=product['id'])
            if not prices['data']:
                # Create the price (plan)
                price = stripe.Price.create(
                    product=product['id'],
                    unit_amount=1000,  # Amount in cents ($10.00)
                    currency="usd",
                    recurring={"interval": "month"},
                )
                self.stdout.write(f"Created price: {price['id']}")
            else:
                self.stdout.write("Price already exists.")

            self.stdout.write(self.style.SUCCESS("Stripe plan setup completed successfully!"))

        except stripe.error.StripeError as e:
            self.stderr.write(f"Stripe error: {e}")
        except Exception as e:
            self.stderr.write(f"Error: {e}")