from django.contrib import admin

from .models import User, Listing, Review, Category, Cart, Like, Invoice


class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "user")


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("listing", "date", "username")


class CartAdmin(admin.ModelAdmin):
    display = ("user"), ("quantity")


class CategoryAdmin(admin.ModelAdmin):
    display = ("name")


class LikeAdmin(admin.ModelAdmin):
    display = ("user", "review")


class InvoiceAdmin(admin.ModelAdmin):
    display = ("user", "body", "time")


admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Invoice, InvoiceAdmin)
