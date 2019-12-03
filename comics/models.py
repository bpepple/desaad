from django.contrib.postgres.fields import ArrayField
from django.db import models
from sorl.thumbnail import ImageField


class Arc(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=255, blank=True)
    desc = models.TextField("Description", blank=True)
    image = ImageField(upload_to="arc/%Y/%m/%d/", blank=True)

    @property
    def issue_count(self):
        return self.issue_set.all().count()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Creator(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=255, blank=True)
    desc = models.TextField("Description", blank=True)
    wikipedia = models.CharField("Wikipedia Slug", max_length=255, blank=True)
    birth = models.DateField("Date of Birth", null=True, blank=True)
    death = models.DateField("Date of Death", null=True, blank=True)
    image = ImageField(upload_to="creator/%Y/%m/%d/", blank=True)
    alias = ArrayField(models.CharField(max_length=100), null=True, blank=True)

    @property
    def issue_count(self):
        return self.credits_set.all().count()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Team(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True)
    desc = models.TextField("Description", blank=True)
    wikipedia = models.CharField("Wikipedia Slug", max_length=255, blank=True)
    image = ImageField(upload_to="team/%Y/%m/%d/", blank=True)
    creators = models.ManyToManyField(Creator, blank=True)

    @property
    def issue_count(self):
        return self.issue_set.all().count()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Character(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True)
    desc = models.TextField("Description", blank=True)
    wikipedia = models.CharField("Wikipedia Slug", max_length=255, blank=True)
    image = ImageField(upload_to="character/%Y/%m/%d/", blank=True)
    alias = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    creators = models.ManyToManyField(Creator, blank=True)
    teams = models.ManyToManyField(Team, blank=True)

    @property
    def issue_count(self):
        return self.issue_set.all().count()

    @property
    def first_appearance(self):
        return self.issue_set.order_by("cover_date").all().first

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Publisher(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, blank=True)
    founded = models.PositiveSmallIntegerField("Year Founded", null=True, blank=True)
    desc = models.TextField("Description", blank=True)
    wikipedia = models.CharField("Wikipedia Slug", max_length=255, blank=True)
    image = ImageField("Logo", upload_to="publisher/%Y/%m/%d/", blank=True)

    @property
    def series_count(self):
        return self.series_set.all().count()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Role(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=25)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class SeriesType(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Series(models.Model):
    mid = models.PositiveIntegerField("Metron ID", unique=True)
    name = models.CharField(max_length=255, blank=True)
    sort_name = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, blank=True)
    volume = models.PositiveSmallIntegerField("Volume Number", null=True, blank=True)
    year_began = models.PositiveSmallIntegerField("Year Began", null=True, blank=True)
    year_end = models.PositiveSmallIntegerField("Year Ended", null=True, blank=True)
    series_type = models.ForeignKey(
        SeriesType, on_delete=models.CASCADE, null=True, blank=True
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.CASCADE, null=True, blank=True
    )
    desc = models.TextField("Description", blank=True)

    def __str__(self):
        return f"{self.name} ({self.year_began})"

    @property
    def issue_count(self):
        return self.issue_set.all().count()

    def first_issue_cover(self):
        try:
            return self.issue_set.all().first().image
        except AttributeError:
            return None

    class Meta:
        verbose_name_plural = "Series"
        ordering = ["sort_name", "year_began"]


class Issue(models.Model):
    STATUS_CHOICES = ((0, "Unread"), (1, "Partially Read"), (2, "Read"))

    mid = models.PositiveIntegerField("Metron ID", unique=True)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    name = ArrayField(
        models.CharField("Story Title", max_length=150), null=True, blank=True
    )
    number = models.CharField("Issue Number", max_length=25)
    slug = models.SlugField(max_length=255, unique=True)
    arcs = models.ManyToManyField(Arc, blank=True)
    cover_date = models.DateField("Cover Date")
    store_date = models.DateField("In Store Date", null=True, blank=True)
    desc = models.TextField("Description", blank=True)
    image = ImageField("Cover", upload_to="issue/%Y/%m/%d/", blank=True)
    creators = models.ManyToManyField(Creator, through="Credits", blank=True)
    characters = models.ManyToManyField(Character, blank=True)
    teams = models.ManyToManyField(Team, blank=True)
    file = models.CharField("File Path", max_length=300)
    status = models.PositiveSmallIntegerField(
        "Status", choices=STATUS_CHOICES, default=0, blank=True
    )
    leaf = models.PositiveSmallIntegerField(editable=False, default=0, blank=True)
    page_count = models.PositiveSmallIntegerField(editable=False, default=1, blank=True)
    mod_ts = models.DateTimeField()

    @property
    def percent_read(self):
        # If status is marked as read return 100%
        if self.status == 2:
            return 100
        if self.leaf > 0:
            # We need to increase the leaf by one to calculate
            # the correct percent (due to index starting with 0)
            read = self.leaf + 1
        else:
            read = self.leaf

        try:
            percent = round((read / self.page_count) * 100)
        except ZeroDivisionError:
            percent = 0
        return percent

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
