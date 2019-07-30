from django.contrib.postgres.fields import ArrayField
from django.db import models
from sorl.thumbnail import ImageField


class Arc(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True)
    desc = models.TextField("Description", blank=True)
    image = ImageField(upload_to="arc/%Y/%m/%d/", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Creator(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True)
    desc = models.TextField("Description", blank=True)
    wikipedia = models.CharField("Wikipedia Slug", max_length=255, blank=True)
    birth = models.DateField("Date of Birth", null=True, blank=True)
    death = models.DateField("Date of Death", null=True, blank=True)
    image = ImageField(upload_to="creator/%Y/%m/%d/", blank=True)
    alias = ArrayField(models.CharField(max_length=100), null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Publisher(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    founded = models.PositiveSmallIntegerField("Year Founded", null=True, blank=True)
    desc = models.TextField("Description", blank=True)
    wikipedia = models.CharField("Wikipedia Slug", max_length=255, blank=True)
    image = ImageField("Logo", upload_to="publisher/%Y/%m/%d/", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Role(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=25)
    order = models.PositiveSmallIntegerField(unique=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order"]


class SeriesType(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Series(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=255)
    sort_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    volume = models.PositiveSmallIntegerField("Volume Number")
    year_began = models.PositiveSmallIntegerField("Year Began")
    year_end = models.PositiveSmallIntegerField("Year Ended", null=True, blank=True)
    series_type = models.ForeignKey(SeriesType, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    desc = models.TextField("Description", blank=True)

    def __str__(self):
        return f"{self.name} ({self.year_began})"

    class Meta:
        verbose_name_plural = "Series"
        unique_together = ["publisher", "name", "volume"]
        ordering = ["sort_name", "year_began"]


class Issue(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    name = ArrayField(
        models.CharField("Story Title", max_length=150), null=True, blank=True
    )
    slug = models.SlugField(max_length=255, unique=True)
    number = models.CharField(max_length=25)
    arcs = models.ManyToManyField(Arc, blank=True)
    cover_date = models.DateField("Cover Date")
    store_date = models.DateField("In Store Date", null=True, blank=True)
    desc = models.TextField("Description", blank=True)
    image = ImageField("Cover", upload_to="issue/%Y/%m/%d/", blank=True)
    creators = models.ManyToManyField(Creator, through="Credits", blank=True)

    def __str__(self):
        return f"{self.series.name} #{self.number}"

    class Meta:
        unique_together = ["series", "number"]
        ordering = ["series__sort_name", "cover_date", "store_date", "number"]


class Credits(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    role = models.ManyToManyField(Role)

    class Meta:
        verbose_name_plural = "Credits"
        unique_together = ["issue", "creator"]
        ordering = ["creator__name"]
