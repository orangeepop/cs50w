from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import *
from django.contrib.auth.decorators import login_required

from .models import User
from . import forms

@login_required(login_url='login')
def category(request, category):
    category_dict = Listings.category.field.choices
    category_id = None
    for i in category_dict:
        if i[1] == category:
            category_id = i[0]
    list = Listings.objects.filter(category=category_id, closed=False)
    return render(request, "auctions/category.html", {
        "category": category, "listings": list
        })

@login_required(login_url='login')
def categories(request):
    choices= [i[1] for i in Listings.category.field.choices]
    return render(request, "auctions/categories.html", {
        "choices": choices
    })

@login_required(login_url='login')
def watchlist(request):
    username = request.user.username
    watchlist = Watchlist.objects.filter(user=username)
    if request.method == "POST":
        item_to_remove = request.POST["remove"]
        Watchlist.objects.filter(user=username, listing=item_to_remove).delete()
    return render(request, "auctions/watchlist.html", {
        "watchlists": watchlist
    })
    
@login_required(login_url='login')
def listing(request, listing_id):
    current_listing = Listings.objects.get(id=listing_id)
    hb = Bids.objects.filter(listing=current_listing, highest_bid=True).first()
    seller_visiting = False
    winner_visiting = False
    all_comments = Comments.objects.filter(listing=current_listing)
    username = request.user.username

    seller_object = current_listing.seller
    if username == seller_object.username:
        seller_visiting = True  

    if request.method == "POST":
        # add to watchlist
        if request.POST.get("watchlist"):
            try:
                Watchlist.objects.create(user=username, listing=current_listing)
            except IntegrityError:
                return HttpResponse("This auction is already on your watchlist!")

        # bid on item
        if request.POST.get("bid"):
            bid = int(request.POST["bid"])
            if hb == None and bid > current_listing.price:
                Bids.objects.create(user=username, listing=current_listing, bid=bid, highest_bid=True)
            elif hb == None and bid <= current_listing.price:
                return HttpResponse("Your bid must be higher than starting bid!")
            elif bid > hb.bid:
                hb.highest_bid = False
                hb.save()
                hb = Bids.objects.create(user=username, listing=current_listing, bid=bid, highest_bid=True)
            else:
                return HttpResponse("Your bid must be higher than current highest bid!")
        
        # close listing if seller is visiting
        if request.POST.get("close"):
            current_listing.closed = True
            current_listing.winner = hb.user
            current_listing.save()
        
        # add comments
        if request.POST.get("comment"):
            comment = request.POST["comment"]
            Comments.objects.create(listing=current_listing, comment=comment)

    # winning user visits a closed listing page, should see that they won the listing
    if current_listing.winner != None:
        winner_username = current_listing.winner
        if username == winner_username:
            winner_visiting = True

    return render(request, "auctions/listing.html", {
        "listing": current_listing, "highest_bid": hb, "seller_visiting": seller_visiting, "winner_visiting": winner_visiting, "comments": all_comments
    })

@login_required(login_url='login')
def create_listing(request):
    categories_list = forms.CategoriesList()
    if request.method == "POST":

        # user adding the listing
        seller = None
        if request.user.is_authenticated:
            seller = request.user.username
            seller_object = User.objects.get(username=seller)
        
        # title of listing
        title = request.POST["title"]

        # starting bid
        price = request.POST["price"]

        # description
        description = request.POST["description"]

        # category
        category = request.POST["category"]

        # image url
        image = request.POST["image"]

        Listings.objects.create(seller=seller_object, title=title, price=price, description=description, category=category, image=image, closed=False)
        return HttpResponseRedirect(reverse("index"))
    
    else:
        return render(request, "auctions/create_listing.html", {
            'categories_list': categories_list
        })


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.exclude(closed=True)
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
