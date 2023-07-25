from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import datetime

from .models import *

def paginate(request, posts):
    paginator = Paginator(posts, 10) #show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

@login_required(login_url='login')
def following(request):

    user = User.objects.get(username=request.user.username)

    followed_accounts = Follows.objects.filter(follower=user)

    query = Q()

    for i in followed_accounts:
        query.add(Q(author=i.user), Q.OR)
    
    followed_posts = Posts.objects.filter(query).order_by("-timestamp")
    page_obj = paginate(request, followed_posts)
    return render(request, "network/following.html", {
        "page_obj": page_obj
    })


def profile(request, username):
    user = User.objects.get(username=username)
    posts = Posts.objects.filter(author=user).order_by("-timestamp")

    page_obj = paginate(request, posts)

    follows = Follows.objects.filter(follower=user).count()
    followers = Follows.objects.filter(user=user).count()
    logged_in = False
    show_button = False
    followed = False

    # follow/unfollow
    if request.user.is_authenticated:
        logged_in = True
        visitor = User.objects.get(username=request.user.username)
        follow_object = Follows.objects.filter(user=user, follower=visitor)
        
        if not follow_object:
            # not already following, show follow button
            show_button = logged_in and (visitor.username != username)
        else:
            # already following
            followed = True
        if request.method == "POST":
            if request.POST.get("follow"):
                Follows.objects.create(user=user, follower=visitor)
                return redirect(reverse("profile", kwargs={'username': username}))
            elif request.POST.get("unfollow"):
                follow_object.delete()
                return redirect(reverse("profile", kwargs={'username': username}))
                
    return render(request, "network/profile.html", {
        "user": user, "page_obj": page_obj, "follows": follows, "followers": followers, "show_button": show_button, "followed": followed
    })

@login_required(login_url='login')
def index(request):
    if request.method == "POST":
        # create new post
        if request.POST.get("new-post"):
            post = request.POST["new-post"]
            user = request.user
            Posts.objects.create(author=user, post=post)
        elif request.POST.get('edit-post'):
            post = request.POST['edit-post']
            Posts.objects.filter(id=request.POST['id']).update(post=post, timestamp=datetime.now())


    # display posts
    posts = Posts.objects.all().order_by("-timestamp")
    page_obj = paginate(request, posts)
    return render(request, "network/index.html", {
        'page_obj': page_obj
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
