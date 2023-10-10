---
layout: default

title: Blog

lang: es
ref: blog

published: True
order: 6
---

<ul>
  {% for post in site.posts %}
      <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
      {{ post.excerpt }}
  {% endfor %}
</ul>
