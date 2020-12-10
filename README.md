# Mall

Online store which submits an emailed receipt to customers, as well as an invoice to the website's superuser(s).

**Additional features:**

Users are able to leave reviews for products, and mark existing reviews as helpful.

Products are allowed two images, when the user mouses-over the first product image, the optionally added second image is shown.

Customers can shop by product category.

# Setup Requirements

*When creating a superuser or user, use your personal email (or email that you have access to, superuser email address will be the recipient of invoices, current user email address will be recipient of receipts)*

Email host must be set in settings.py
In this version, the creator has provided a host email. Therefore the settings.py file requires no modification.

# File Contents

Summary of file contents

**HTML files**

*layout.html*
Contains navigation bar, CSS and JS references, all other html pages extend this page.

*index.html*
Displays all products for sale, clicking on a product takes the user to listing.html

*listing.html*
Displays all product data for a given product listing. Users can add product to their cart, review the product, and 'like' reviews.

*cart.html*
Displays the user's shopping cart, alternate views include an order submission processing page, and a confirmed order page.

*categories.html*
Displays a list of product categories. Users can click on a category to be directed to the listing.html page filtered for products in the selected category.

*login.html*
Log-in page for already registered users

*register.html*
Page for new users to create an account for the website

**views.py functions**

*def index*
Queries listings and passes them to index.html

*def listing*
Accepts listing_id as parameter. Passes requested listing, form for new review and existing reviews for listing to listing.html page.

*def review*
POST request required, function adds a new review to the listing taken as a parameter.

*def cart*
If GET request, function returns contents of current user's shopping cart. If POST request, adds the product to the user's cart

*def change_quant*
PUT request required, function modifies the quantity of a given item in the user's cart, and returns a new cart total cost via JSON response.

*def checkout*
Calls send_admin_invoice and send_user_receipt, returning the invoice id number for the newly created invoice object.

*def send_admin_invoice*
Creates an invoice email with sale information, and sends 1 copy via email to each superuser in the database, returns reference to new invoice object.

*def send_user_receipt*
Creates a receipt email with sale information, sends 1 copy to the current user (purchaser).

*def feedback*
POST request required, adds or removes a like from a listing review, each user is allowed to like each review 1 time.

*def categories*
Renders categories.html, passing a query of all existing categories.

*def category*
Takes a parameter category_id, queries for all items within the selected category, passing them to the index.html page.

**shopping.js functions**

*checkOut()*
On click of Check Out button on cart.html, hides Cart view and loads Processing view. Makes fetch call to send emails, once emails are sent, function hides loading view and displays Received view, with new invoice/receipt number.

*photoOn()*
Called by changePhoto, photoOn changes the SRC of a listing's photo, to the SRC of the second photo

*photoAway()*
Called by changePhoto, photoOn changes the SRC of a listing's second photo, to the SRC of the first photo

*changePhoto()*
Calls photoOn() when the user mouses over a photo, and calls photoAway() when the user mouses off of a photo.

*changeQuant()*
On click of a Change Quantity button, function makes a fetch call with the text in the input field. If the text is a positive or 0 value, the function makes a fetch call to /change_quant to update the database and modifies the html to reflect changes to the user's cart.

*reviewCount()*
On click of a like button (thumbsup image) for a review, function makes a fetch call to /feedback. Function then changes the html to reflect the review's new like count.

# Citations

Loading Icon Image: https://i.etsystatic.com/13221305/r/il/dcb12b/1550187633/il_570xN.1550187633_g1ti.jpg
Thumbs-Up Image: https://images.onlinelabels.com/images/clip-art/SavanaPrice/Thumbs%20Up-192852.png 

Django Email Documentation: https://docs.djangoproject.com/en/3.1/topics/email/

# Tree

```bash
├── db.sqlite3
├── mall
│   ├── __init__.py
│   ├── __init__.py:Zone.Identifier
│   ├── __pycache__
│   │   ├── __init__.cpython-38.pyc
│   │   ├── settings.cpython-38.pyc
│   │   ├── urls.cpython-38.pyc
│   │   └── wsgi.cpython-38.pyc
│   ├── asgi.py
│   ├── asgi.py:Zone.Identifier
│   ├── settings.py
│   ├── settings.py:Zone.Identifier
│   ├── urls.py
│   ├── urls.py:Zone.Identifier
│   ├── wsgi.py
│   └── wsgi.py:Zone.Identifier
├── manage.py
├── manage.py:Zone.Identifier
├── requirements.txt
└── shopping
    ├── __init__.py
    ├── __init__.py:Zone.Identifier
    ├── __pycache__
    │   ├── __init__.cpython-38.pyc
    │   ├── admin.cpython-38.pyc
    │   ├── models.cpython-38.pyc
    │   ├── urls.cpython-38.pyc
    │   └── views.cpython-38.pyc
    ├── admin.py
    ├── admin.py:Zone.Identifier
    ├── apps.py
    ├── apps.py:Zone.Identifier
    ├── migrations
    │   ├── 0001_initial.py
    │   ├── 0002_category_invoice_listing_review_thumbsup_watch.py
    │   ├── 0003_remove_listing_highestbidder.py
    │   ├── 0004_auto_20201201_0041.py
    │   ├── 0005_auto_20201201_0043.py
    │   ├── 0006_auto_20201201_0044.py
    │   ├── 0007_remove_listing_isclosed.py
    │   ├── 0008_auto_20201201_0431.py
    │   ├── 0009_auto_20201201_0435.py
    │   ├── 0010_auto_20201201_0525.py
    │   ├── 0011_auto_20201203_0335.py
    │   ├── __init__.py
    │   └── __pycache__
    │       ├── 0001_initial.cpython-38.pyc
    │       ├── 0002_category_invoice_listing_review_thumbsup_watch.cpython-38.pyc
    │       ├── 0003_remove_listing_highestbidder.cpython-38.pyc
    │       ├── 0004_auto_20201201_0041.cpython-38.pyc
    │       ├── 0005_auto_20201201_0043.cpython-38.pyc
    │       ├── 0006_auto_20201201_0044.cpython-38.pyc
    │       ├── 0007_remove_listing_isclosed.cpython-38.pyc
    │       ├── 0008_auto_20201201_0431.cpython-38.pyc
    │       ├── 0009_auto_20201201_0435.cpython-38.pyc
    │       ├── 0010_auto_20201201_0525.cpython-38.pyc
    │       ├── 0011_auto_20201203_0335.cpython-38.pyc
    │       └── __init__.cpython-38.pyc
    ├── models.py
    ├── models.py:Zone.Identifier
    ├── static
    │   └── shopping
    │       ├── shopping.js
    │       ├── styles.css
    │       └── styles.css:Zone.Identifier
    ├── templates
    │   └── shopping
    │       ├── cart.html
    │       ├── categories.html
    │       ├── index.html
    │       ├── index.html:Zone.Identifier
    │       ├── layout.html
    │       ├── layout.html:Zone.Identifier
    │       ├── listing.html
    │       ├── login.html
    │       ├── login.html:Zone.Identifier
    │       ├── register.html
    │       └── register.html:Zone.Identifier
    ├── tests.py
    ├── tests.py:Zone.Identifier
    ├── urls.py
    ├── urls.py:Zone.Identifier
    ├── views.py
    └── views.py:Zone.Identifier
```