from django import forms
from django.core.exceptions import ValidationError

from webapp.models import Article, Comment


class ArticleForm(forms.ModelForm):
    tag = forms.CharField(label='Новый тег', max_length=500, required=False)
    class Meta:
        model = Article
        exclude = ['created_at', 'updated_at', 'tags']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['created_at', 'updated_at']


class ArticleCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'text']


class SimpleSearchForm(forms.Form):
    tag = forms.CharField(max_length=100, required=False, label='Найти')


class FullSearchForm(forms.Form):
    text = forms.CharField(max_length=100, required=False, label='Текст')
    in_title = forms.BooleanField(initial=True, required=False, label='В заголовках')
    in_text = forms.BooleanField(initial=True, required=False, label='В тексте')
    in_tags = forms.BooleanField(initial=True, required=False, label='В тегах')
    in_comment_text = forms.BooleanField(initial=False, required=False, label='В тексте комментариев')
    author = forms.CharField(max_length=100, required=False, label='Автор')
    in_articles = forms.BooleanField(initial=True, required=False, label='Статей')
    in_comments = forms.BooleanField(initial=False, required=False, label='Комментариев')


    def clean(self):
        super().clean()
        text = self.cleaned_data.get('text')
        in_title = self.cleaned_data.get('in_title')
        in_text = self.cleaned_data.get('in_text')
        in_tags = self.cleaned_data.get('in_tags')
        in_comment_text = self.cleaned_data.get('in_comment_text')
        author = self.cleaned_data.get('author')
        in_articles = self.cleaned_data.get('in_articles')
        in_comments = self.cleaned_data.get('in_comments')
        if not(author or text):
            raise ValidationError('One of the fields: Text or Author should be filled.',
                                  code='no_text_search_destination')
        if text:
            if not (in_title or in_text or in_tags or in_comment_text):
                raise ValidationError(
                    'One of the checkboxes: In Title, In Text, In Tags, In Comment text should be checked.',
                    code='no_text_search_destination'
                )
        if author:
            if not(in_articles or in_comments):
                raise ValidationError(
                    'One of the checkboxes: In Articles, In comments should be checked.',
                    code='no_text_search_destionation'
                )
        return self.cleaned_data

class ArticleSearchForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'author']