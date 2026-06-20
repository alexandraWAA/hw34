import stripe
from django.conf import settings
from django.core.exceptions import ValidationError

stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(course):
    try:
        product = stripe.Product.create(
            name=course.name,
            description=course.description or f'Курс "{course.name}"',
            metadata={"course_id": course.id},
        )
        return product.id
    except stripe.error.StripeError as e:
        raise ValidationError(f"Ошибка создания продукта: {str(e)}")


def create_stripe_price(amount, product_id):
    try:
        price = stripe.Price.create(
            unit_amount=int(amount * 100),
            currency="rub",
            product=product_id,
        )
        return price.id
    except stripe.error.StripeError as e:
        raise ValidationError(f"Ошибка создания цены: {str(e)}")


def create_checkout_session(price_id, course_name, success_url, cancel_url):
    try:
        session = stripe.checkout.Session.create(
            success_url=success_url,
            cancel_url=cancel_url,
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            metadata={"course_name": course_name},
        )
        return session
    except stripe.error.StripeError as e:
        raise ValidationError(f"Ошибка создания сессии: {str(e)}")


def sync_course_with_stripe(course):
    if not course.stripe_product_id:
        product_id = create_stripe_product(course)
        course.stripe_product_id = product_id
        course.save(update_fields=["stripe_product_id"])
    if not course.stripe_price_id and course.price > 0:
        price_id = create_stripe_price(course.price, course.stripe_product_id)
        course.stripe_price_id = price_id
        course.save(update_fields=["stripe_price_id"])
    return course
