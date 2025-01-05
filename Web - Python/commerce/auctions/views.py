from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import *
from django import forms

from .models import User


# Shows on watchlist should not i think
def index(request):
    if request.method == "POST":
        listings = filters(request)
    else:
        listings = Listings.objects.filter(closed=False)
    return sorted_index(request, listings, "Listings", filters=True)


def filters(request):
    listings_a = active(request)
    return category(request, listings_a)


def category(request, listings_a):
    cat = request.POST["category"]
    if cat == "All":
        return listings_a
    return listings_a.filter(category=cat)


def active(request):
    form = request.POST
    active_status = form["active_status"]
    if active_status == "active":
        return Listings.objects.filter(closed=False)
    elif active_status == "unactive":
        return Listings.objects.filter(closed=True)
    else:
        return Listings.objects.filter()


# Can be used by different
def sorted_index(request, listings, sorted_name, filters=False):
    return render(
        request,
        "auctions/index.html",
        {
            "listings": listings,
            "sorted_name": sorted_name,
            "categories": all_categories(),
            "filters": filters,
        },
    )


def all_categories():
    listings = Listings.objects.all()
    categories = []
    categories.append("All")

    for e in listings:
        if e.category not in categories:
            categories.append(e.category)
    print("-------------------", categories)
    return categories


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
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
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
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create(request):
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():

            listing = form.save(commit=False)
            listing.user = request.user
            listing.user_bid = None
            listing.category = listing.category.capitalize()
            listing.save()
            form.save()
        return redirect(reverse("index"))

    else:
        return render(request, "auctions/create.html", {"form": CreateForm()})


# Try and split it up
def listing(request, id, only_show=False):
    listing = ret_listing(id)
    comments = return_com(listing)
    error_msg = ""
    watchlist_Exist = False

    if request.method == "POST" and only_show == False:
        error_msg = make_bid(request, listing)

    # Check if it is added to watchlist
    watchlist_Exist = Watchlist.objects.filter(
        listing_id=listing.id, user_id=request.user.id
    ).exists()

    bid_status = bid_won(listing, request.user)
    print(bid_status, '-----------------------------------------------')
    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listing,
            "login_user_id": request.user.id,
            "watchlisted": watchlist_Exist,
            "error_msg": error_msg,
            "comments": comments,
            "bid_won": bid_status,
        },
    )


def bid_won(listing, user):
    if listing.num_bid == 0 or not listing.closed:
        return None
    list_user_id = listing.user_bid.id
    user_id = user.id
    closed = listing.closed
    
    if list_user_id == user_id and closed:
        return True
    return False


def return_com(listing):
    comments = []
    c = Comments.objects.filter(listing__id=listing.id)
    for e in c:
        comments.append({"username": e.user.username, "text": e.comment})
    return comments


def comment(request, list_id):
    form = request.POST
    com = Comments.objects.create(
        listing=ret_listing(list_id),
        comment=form["comment"],
        user=ret_user(form["user_id"]),
    )
    com.save()
    return redirect(reverse("listing", args=[list_id]))


def close(request, list_id):
    form = request.POST
    user_id = form["user_id"]
    listing = ret_listing(list_id)
    print("----- - --  -- - - - -- - - ", listing.id, listing.name)
    # Change to bool in model to closed
    if int(user_id) == int(listing.user.id):
        if listing.user_bid == None:
            msg = f"No bids, listing closed"
        else:
            msg = f"Listing Closed at: {listing.current_bid}$"

        listing.closed = True
        listing.save()
    else:
        msg = "You dont have permisson to close this bid"
    return render(request, "auctions/close.html", {"msg": msg})


def make_bid(request, listing):
    form = request.POST
    bid = form["bid"]
    if listing.closed == True:
        error_msg = "Bid is closed!"
    elif not bid:
        error_msg = "Enter a price to bid"
    elif float(bid) > listing.current_bid or (
        listing.num_bid == 0 and float(bid) == listing.current_bid
    ):
        listing.current_bid = bid
        listing.user_bid = request.user
        listing.num_bid = listing.num_bid + 1
        listing.bidders.add(request.user)

        listing.save()

        error_msg = None
    else:
        error_msg = (
            f"Your bid needs to be higher than the current bid ({listing.current_bid}$)"
        )
    return error_msg


# Watchlist page
def watchlist(request, list_id):
    if request.method == "POST":
        # Check if filtes is aplied
        if request.POST["val"] == "filter":
            print("Get - -- - - - - - - - -- - - ----------")
            listings = filters(request)
            watchlisted = Watchlist.objects.filter(user_id=request.user.id)
            listings = listings.filter(id__in=watchlisted.values("listing_id"))
            return sorted_index(request, listings, "Watchlisted listings")

        elif request.POST["val"] == "add":
            add_watchlist(Listings.objects.get(id=list_id), request.user)
            request.method = "GET"
            return listing(request, list_id, only_show=True)
        else:
            # Remove if it exist
            l = Watchlist.objects.filter(listing_id=list_id)
            if l.exists():
                l.delete()
            return listing(request, list_id, only_show=True)

    listings = Listings.objects.filter(
        id__in=Watchlist.objects.filter(user_id=request.user.id).values("listing_id")
    )

    # Display msg if none is watchlisted
    if listings.exists():
        header = "Watchlisted Listings"
    else:
        header = "You dont have any listings watchlisted"
    return sorted_index(request, listings, header)


def add_watchlist(listing, user):
    w_list = Watchlist()
    w_list.user = user
    w_list.listing = listing
    w_list.save()


# Your listings
def your(request):
    listings = Listings.objects.filter(user_id=request.user.id, closed=False)
    if listings.exists():
        header = "Your Listings"
    else:
        header = "You dont have any listings listed on here"
    return sorted_index(request, listings, header)


def bids(request):
    listings = Listings.objects.filter(bidders=request.user).distinct()
    if listings.exists():
        header = "Your Bids"
    else:
        header = "You have not bid on any items"
    return sorted_index(request, listings, header)


def ret_listing(id):
    return Listings.objects.get(id=int(id))


def ret_user(id):
    return User.objects.get(id=int(id))
