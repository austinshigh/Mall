from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django import forms
from django.db import IntegrityError
from django.db.models import Max, Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
import smtplib
import ssl
import json
from email.message import EmailMessage
import datetime

from .models import User, Listing, Review, Cart, Category, Like, Invoice


class product_review(forms.Form):
    text = forms.CharField(max_length=250, label=False, widget=forms.TextInput(
        attrs={'class': 'Review'}))


def index(request):
    # Set page header
    header = "All Products"

    # Query Listings
    listings = Listing.objects.all()
    listings = listings.order_by('title')

    return render(request, "shopping/index.html", {
        "listings": listings,
        "header": header
    })


@csrf_protect
def listing(request, listing_id):
    # Retrieve listing passed to function
    current_listing = Listing.objects.get(pk=listing_id)
    # Query for reviews on current listing
    reviews = reversed(Review.objects.filter(listing=current_listing))
    # Create review form
    review_form = product_review()
    # Render listing page, pass in necessary info
    return render(request, "shopping/listing.html", {
        "listing": current_listing,
        "reviews": reviews,
        "reviewForm": review_form
        })


@login_required
@csrf_protect
def review(request, listing_id):
    # Request method must be POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Retrieve data from review form
    form = product_review(request.POST)
    if form.is_valid():
        text = form.cleaned_data['text']
        # Get current user object
        user = request.user
        # Get current listing object
        current_listing = Listing.objects.get(pk=listing_id)

        # Create new instance of review, set values to form values
        review = Review(
            text=text,
            username=user,
            listing=current_listing
        )
        review.save()
        # Redirect user to listing page
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


@login_required
@csrf_protect
def cart(request):
    # GET request for viewing cart
    if request.method == "GET":
        # Render cart page for the current user
        current_user = request.user
        cart = Cart.objects.filter(user=current_user)

        # Add item prices to get Cart total
        total = 0
        for item in cart:
            total = total + (item.quantity * item.listing.price)

        return render(request, "shopping/cart.html", {
            "cart": cart,
            "total": total})

    # POST request used for adding items to cart
    if request.method == "POST":
        # Retrieve data from form
        id_add = request.POST.get("add-cart", False)
        # Get current user object
        user = request.user
        # See if current listing is in the users cart
        current_listing = Listing.objects.get(pk=id_add)
        contained = Cart.objects.filter(
            user=user,
            listing=current_listing
            )
        if not contained:
            # Add new listing instance to the user's cart
            cart = Cart(
                user=user,
                listing=current_listing
            )
            cart.save()
        else:
            # If already contained, increase item quantity in cart by 1
            current_cart_item = contained[0]
            current_cart_item.quantity = current_cart_item.quantity + 1
            current_cart_item.save()
        return HttpResponseRedirect(reverse("cart"))


@csrf_protect
def change_quant(request, listing_id):
    # Editing a post must be via PUT
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Get current user object
    user = request.user

    # Retrieve instance of selected cart item
    cart = Cart.objects.filter(user=user)

    # Get listing object intended to be modified
    modified_item = Listing.objects.get(pk=listing_id)

    # Look for listing in cart, set modified_item to reference listing in cart
    for item in cart:
        if (item.listing == modified_item):
            modified_item = item

    # Load data from json fetch request
    data = json.loads(request.body)
    quantity = data.get("quantity")

    # If fetch request sends post content, update database
    if quantity == "0":
        # Remove listing from cart if quantity is zero
        modified_item.delete()
    else:
        # Else set new specified quantity in cart
        modified_item.quantity = quantity
        modified_item.save()

    # Get reference to current cart object
    cart = Cart.objects.filter(user=user)

    # Return cart total via JSON Response
    total = 0
    for item in cart:
        total = total + (item.quantity * item.listing.price)

    # If the cart is completely empty, delete the cart
    if (total == 0):
        cart.delete()

    return JsonResponse(total, status=201, safe=False)


@csrf_protect
@login_required
def checkout(request):

    # Get current user object
    current_user = request.user
    # Get current user id
    user_id = request.user.id
    # Get all objects in current user's cart
    cart = Cart.objects.filter(user=user_id)

    # Verify empty cart is not being sent to customer
    if cart:
        # Send page superuser(s) an invoice email
        invoice = send_admin_invoice(request, cart)
        # Send customer a receipt via email
        send_user_receipt(request, cart, invoice)

        # Delete all items in current user's cart
        for item in cart:
            item.delete()

        # Return invoice Id as JSON response
        invoice_id = invoice.id
        return JsonResponse(invoice_id, status=201, safe=False)


@login_required
def send_admin_invoice(request, cart):

    # Get current user object
    current_user = request.user

    # Place customer username and email address in email body
    message_body = f"Ordered By: {current_user.username}\n"
    message_body = message_body + f"Address: {current_user.email} \n"

    # Add all relevant listing info into email body
    total = 0
    for item in cart:
        if (item.quantity > 0):
            total = total + (item.quantity * item.listing.price)
            message_body = message_body + f"Item: {item.listing.title} | "
            message_body = message_body + f"Quantity: {item.quantity} | "
            message_body = message_body + f"Price: ${item.listing.price}\n"

    message_body = message_body + f"Total Order Amount: ${total}"

    # Add packing codes, for efficient processing of order
    message_body = message_body + " \nPacking Codes:\n"
    for item in cart:
        if (item.quantity > 0):
            message_body = message_body + f"ID: {item.listing.id} "
            message_body = message_body + f"Qty: {item.quantity} \n"

    # Create and save invoice object for record-keeping purposes
    invoice = Invoice(
        user=current_user,
        body=message_body
    )
    invoice.save()

    # Add invoice creation time and invoice ID to email
    message_body = message_body + f"{invoice.time.strftime('%x %X')}\n"
    message_body = message_body + f"Invoice Number: {invoice.id}"

    # Query superusers who will all be recipients of invoice emails
    superusers = User.objects.filter(is_superuser=True)

    # Create and send email to all superusers using django email protocol
    for superuser in superusers:
        msg = EmailMessage()
        msg.set_content(f"{message_body}")
        msg["Subject"] = "New Order Invoice: Mall App"
        msg["From"] = "ashcustombuilders@gmail.com"
        msg["To"] = f"{superuser.email}"

        context = ssl.create_default_context()

        with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
            smtp.starttls(context=context)
            smtp.login('ashcustombuilders@gmail.com', 'kxjfyyyoscoqtikr')
            smtp.send_message(msg)

    # Return invoice instance
    return invoice


@login_required
def send_user_receipt(request, cart, invoice):
    # Get current user object
    current_user = request.user

    # Add recipient username to message body
    message_body = f"Order From Mall placed by: {current_user.username}\n"

    # Add total cost, additional listing info to receipt
    total = 0
    for item in cart:
        if (item.quantity > 0):
            total = total + (item.quantity * item.listing.price)
            message_body = message_body + f"Item: {item.listing.title} | "
            message_body = message_body + f"Quantity: {item.quantity} | "
            message_body = message_body + f"Price: ${item.listing.price}\n"

    message_body = message_body + f"Total Order Amount: ${total}\n"

    # Add receipt creation time, as well as invoice/receipt ID number
    message_body = message_body + f"{invoice.time.strftime('%x %X')}\n"
    message_body = message_body + f"Receipt Number: {invoice.id}"

    # Create and send receipt via email to current user
    msg = EmailMessage()
    msg.set_content(f"{message_body}")
    msg["Subject"] = "Your Receipt! Thank you for Shopping with us!"
    msg["From"] = "ashcustombuilders@gmail.com"
    msg["To"] = f"{current_user.email}"

    context = ssl.create_default_context()

    with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
        smtp.starttls(context=context)
        smtp.login('ashcustombuilders@gmail.com', 'kxjfyyyoscoqtikr')
        smtp.send_message(msg)


@login_required
@csrf_protect
def feedback(request):
    # Adding a like to a review must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get contents of review
    data = json.loads(request.body)
    review_id = data.get("review", "")
    review = Review.objects.get(id=review_id)

    # Get User object for current user
    user = request.user

    # Determine if current user has already liked this review
    like_on_review = Like.objects.filter(review=review)
    current_like = like_on_review.filter(user=user)

    # If user has liked this review, remove the like. Else, add one.
    if current_like:
        current_like.delete()
    else:
        like = Like(
            review=review,
            user=user
        )
        like.save()

    # Count number of total like on review
    new_like_count = like_on_review.count()

    # Pass new number of total likes as JsonResponse
    data = {
        "newCount": new_like_count
    }
    return JsonResponse(data, status=201)


def categories(request):
    # Render categories page with all categories
    categories = Category.objects.all()
    # Set page header
    categories = categories.order_by('name')
    return render(request, "shopping/categories.html", {
        "categories": categories
    })


def category(request, category_id):
    # Render page with listings within requested category
    category = Category.objects.get(pk=category_id)
    # Set page header
    header = category.name

    # Filter for listings within requested category
    listings = Listing.objects.filter(category=category)
    listings = listings.order_by('title')

    return render(request, "shopping/index.html", {
        "listings": listings,
        "header": header
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "shopping/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "shopping/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "shopping/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "shopping/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "shopping/register.html")
