from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.views.generic import ListView, DetailView, CreateView,\
    UpdateView, DeleteView, FormView

from webapp.forms import ArticleForm, ArticleCommentForm, SimpleSearchForm, FullSearchForm
from webapp.models import Article, Tag
from django.core.paginator import Paginator


class IndexView(ListView):
    template_name = 'article/index.html'
    context_object_name = 'articles'
    model = Article
    ordering = ['-created_at']
    paginate_by = 5
    paginate_orphans = 1

    def get(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.search_value = self.get_search_value()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.search_value:
            queryset = queryset.filter(
                Q(tags__name__iexact=self.search_value)
            )
        return queryset.distinct()


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'] = self.form
        if self.search_value:
            context['query'] = urlencode({'tag': self.search_value})

        print(self.request.GET.get('tag'))
        return context


    def get_search_form(self):
        return SimpleSearchForm(data=self.request.GET)

    def get_search_value(self):
        if self.form.is_valid():
            return self.form.cleaned_data['tag']
        return None


class ArticleView(DetailView):
    template_name = 'article/article.html'
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        context['form'] = ArticleCommentForm()
        comments = article.comments.order_by('-created_at')
        self.paginate_comments_to_context(comments, context)
        return context


    def paginate_comments_to_context(self, comments, context):
        paginator = Paginator(comments, 3, 0)
        page_number = self.request.GET.get('page', 1)
        page = paginator.get_page(page_number)
        context['paginator'] = paginator
        context['page_obj'] = page
        context['comments'] = page.object_list
        context['is_paginated'] = page.has_other_pages()


class ArticleCreateView(CreateView):
    form_class = ArticleForm
    model = Article
    template_name = 'article/create.html'

    def get_success_url(self):
        return reverse('article_view', kwargs={'pk': self.object.pk})


    def form_valid(self, form):
        tags = self.get_tags(form.cleaned_data['tag'])
        self.object = form.save()
        self.object.tags.clear()
        self.object.tags.add(*tags)
        self.object.save()
        return super().form_valid(form)


    def get_tags(self, cur_tags):
        new_tags = cur_tags.split(',')
        tags = []
        for i in new_tags:
            if i != "":
                Tag.objects.get_or_create(name=i)
                tags.append(Tag.objects.get(name=i))
        return tags

class ArticleUpdateView(UpdateView):
    model = Article
    template_name = 'article/update.html'
    form_class = ArticleForm
    context_object_name = 'article'

    def get_success_url(self):
        return reverse('article_view', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        tags_list = ''
        tags = list(self.object.tags.all())
        for tag in tags:
            tags_list += tag.name + ','
        tags_list = tags_list[:-1]
        form.fields['tag'].initial = tags_list
        return form

    def form_valid(self, form):
        tags = self.get_tags(form.cleaned_data['tag'])
        self.object = form.save()
        self.object.tags.clear()
        self.object.tags.add(*tags)
        self.object.save()
        return super().form_valid(form)


    def get_tags(self, cur_tags):
        new_tags = cur_tags.split(',')
        tags = []
        for i in new_tags:
            if i != "":
                Tag.objects.get_or_create(name=i)
                tags.append(Tag.objects.get(name=i))
        return tags

class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'article/delete.html'
    context_object_name = 'article'
    success_url = reverse_lazy('index')


class ArticleSearchView(FormView):
    template_name = 'article/search.html'
    form_class = FullSearchForm

    def form_valid(self, form):
        text = form.cleaned_data.get('text')
        author = form.cleaned_data.get('author')
        query = self.get_text_search_query(form, text, author)
        context = self.get_context_data(form=form)
        context['articles'] = Article.objects.filter(query).distinct()
        return self.render_to_response(context=context)

    def get_text_search_query(self, form, text, author):
        query = Q()
        if text:
            in_title = form.cleaned_data.get('in_title')
            if in_title:
                query = query | Q(title__icontains=text)
            in_text = form.cleaned_data.get('in_text')
            if in_text:
                query = query | Q(text__icontains=text)
            in_tags = form.cleaned_data.get('in_tags')
            if in_tags:
                query = query | Q(tags__name__iexact=text)
            in_comment_text = form.cleaned_data.get('in_comment_text')
            if in_comment_text:
                query = query | Q(comments__text__icontains=text)
        if author:
            in_articles = form.cleaned_data.get('in_articles')
            if in_articles:
                query = query | Q(author__iexact=author)
            in_comments = form.cleaned_data.get('in_comments')
            if in_comments:
                query = query | Q(comments__author__iexact=author)
        return query