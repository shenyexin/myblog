from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import threading


class SendMail(threading.Thread):
    def __init__(self, subject, text, sender, email):
        self.subject = subject
        self.text = text
        self.sender = sender
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject, self.text, self.sender, [self.email], fail_silently=False, html_message=self.text)


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)

    root = models.ForeignKey('self', related_name='root_comment', null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='parent_comment', null=True, on_delete=models.CASCADE)
    reply_to = models.ForeignKey(User, related_name='replies', null=True, on_delete=models.CASCADE)

    def send_mail(self):
        if self.parent is None:
            # 评论博客
            subject = '有人评论你的博客'
            email = self.content_object.get_email()
        else:
            # 回复评论
            subject = '有人回复你的评论'
            email = self.reply_to.email
        if email != '':
            context = {
                'comment_text':self.text,
                'url':self.content_object.get_url(),
            }
            text = render_to_string('comment/send_mail.html', context)
            sender = settings.EMAIL_HOST_USER
            send_mail = SendMail(subject, text, sender, email)
            send_mail.start()

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['comment_time']
