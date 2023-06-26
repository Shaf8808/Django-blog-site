from django.shortcuts import render, get_object_or_404, reverse  # Looks up a URL by the name in the urls.py file
from django.views import generic, View
from django.http import HttpResponseRedirect
from .models import Post
from .forms import CommentForm


class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'index.html'
    paginate_by = 6


class PostDetail(View):

    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by('created_on')
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )

    def post(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by('created_on')
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True
        # Gets all of the data requested from the comments form
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            # Sets email and username automatically based on 
            # the details of the logged in user by adding request
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            # Assign a post to the comment before committing
            # and saving
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
        else:
            # If the form is not valid, return an empty
            # form instance
            comment_form = CommentForm()

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )


class PostLike(View):
    def post(self, request, slug):
        # Gets the post
        post = get_object_or_404(Post, slug=slug)
        # Checks if post is already liked before removing it
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        # If it hasn't been liked before, add it
        else:
            post.likes.add(request.user)
        # Reload post_detail template to see likes
        return HttpResponseRedirect(reverse('post_detail', args=[slug]))