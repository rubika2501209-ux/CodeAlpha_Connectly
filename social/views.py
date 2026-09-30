from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Profile, Post, Comment, Like, Follow


def home(request):
    posts = Post.objects.select_related("author").prefetch_related(
        "comments__author",
        "likes"
    )

    users = User.objects.exclude(id=request.user.id) if request.user.is_authenticated else User.objects.all()

    return render(
        request,
        "home.html",
        {
            "posts": posts,
            "users": users[:10],
        }
    )


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        Profile.objects.get_or_create(user=user)

        login(request, user)

        messages.success(request, "Account created successfully!")
        return redirect("home")

    return render(request, "register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, "Welcome back!")
            return redirect("home")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        image_url = request.POST.get("image_url", "").strip()

        if not content:
            messages.error(request, "Post cannot be empty.")
            return redirect("home")

        Post.objects.create(
            author=request.user,
            content=content,
            image_url=image_url
        )

        messages.success(request, "Post created successfully!")

    return redirect("home")


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    like = Like.objects.filter(
        user=request.user,
        post=post
    ).first()

    if like:
        like.delete()
    else:
        Like.objects.create(
            user=request.user,
            post=post
        )

    return redirect(request.META.get("HTTP_REFERER", "home"))


@login_required
def comment_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        text = request.POST.get("text", "").strip()

        if text:
            Comment.objects.create(
                post=post,
                author=request.user,
                text=text
            )

    return redirect(request.META.get("HTTP_REFERER", "home"))


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author == request.user:
        post.delete()
        messages.success(request, "Post deleted.")

    return redirect("home")


def profile(request, username):
    user = get_object_or_404(User, username=username)

    posts = Post.objects.filter(
        author=user
    ).prefetch_related("likes", "comments")

    followers_count = Follow.objects.filter(
        following=user
    ).count()

    following_count = Follow.objects.filter(
        follower=user
    ).count()

    is_following = False

    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=user
        ).exists()

    profile_obj, created = Profile.objects.get_or_create(
        user=user
    )

    return render(
        request,
        "profile.html",
        {
            "profile_user": user,
            "profile": profile_obj,
            "posts": posts,
            "followers_count": followers_count,
            "following_count": following_count,
            "is_following": is_following,
        }
    )


@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(
        User,
        username=username
    )

    if user_to_follow == request.user:
        messages.error(request, "You cannot follow yourself.")
        return redirect("profile", username=username)

    follow = Follow.objects.filter(
        follower=request.user,
        following=user_to_follow
    ).first()

    if follow:
        follow.delete()
    else:
        Follow.objects.create(
            follower=request.user,
            following=user_to_follow
        )

    return redirect(
        "profile",
        username=username
    )


@login_required
def edit_profile(request):
    profile_obj, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        bio = request.POST.get("bio", "").strip()
        avatar = request.POST.get("avatar", "").strip()

        profile_obj.bio = bio
        profile_obj.avatar = avatar
        profile_obj.save()

        messages.success(
            request,
            "Profile updated successfully!"
        )

        return redirect(
            "profile",
            username=request.user.username
        )

    return render(
        request,
        "edit_profile.html",
        {
            "profile": profile_obj
        }
    )