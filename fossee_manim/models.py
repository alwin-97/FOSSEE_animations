from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.conf import settings
from django.utils import timezone
from django.core.files import File
from taggit.managers import TaggableManager
from simple_history.models import HistoricalRecords
from os import path, sep
import tempfile
import subprocess

position_choices = (
    ("contributor", "Contributor"),
    ("reviewer", "Reviewer")
    )

department_choices = (
    ("computer", "Computers"),
    ("mathematics", "Mathematics"),
    ("physics", "Physics"),
    ("information technology", "Information Technology"),
    ("civil", "Civil"),
    ("electrical", "Electrical"),
    ("mechanical", "Mechanical"),
    ("chemical", "Chemical"),
    ("aerospace", "Aerospace"),
    ("biosciences and bioengineering", "Biosciences and  BioEngineering"),
    ("electronics", "Electronics"),
    ("energy science and engineering", "Energy Science and Engineering"),
    ("others", "Others")
    )

title = (
    ("Professor", "Prof."),
    ("Doctor", "Dr."),
    ("Shriman", "Shri"),
    ("Shrimati", "Smt"),
    ("Kumari", "Ku"),
    ("Mr", "Mr."),
    ("Mrs", "Mrs."),
    ("Miss", "Ms."),
    )

source = (
    ("FOSSEE website", "FOSSEE website"),
    ("Google", "Google"),
    ("Social Media", "Social Media"),
    ("From other College", "From other College"),
    ("others", "Others")
    )

states = (
    ("IN-AP",	"Andhra Pradesh"),
    ("IN-AR",	"Arunachal Pradesh"),
    ("IN-AS",	"Assam"),
    ("IN-BR",	"Bihar"),
    ("IN-CT",	"Chhattisgarh"),
    ("IN-GA",	"Goa"),
    ("IN-GJ",	"Gujarat"),
    ("IN-HR",	"Haryana"),
    ("IN-HP",	"Himachal Pradesh"),
    ("IN-JK",	"Jammu and Kashmir"),
    ("IN-JH",	"Jharkhand"),
    ("IN-KA",	"Karnataka"),
    ("IN-KL",	"Kerala"),
    ("IN-MP",	"Madhya Pradesh"),
    ("IN-MH",	"Maharashtra"),
    ("IN-MN",	"Manipur"),
    ("IN-ML",	"Meghalaya"),
    ("IN-MZ",	"Mizoram"),
    ("IN-NL",	"Nagaland"),
    ("IN-OR",	"Odisha"),
    ("IN-PB",	"Punjab"),
    ("IN-RJ",	"Rajasthan"),
    ("IN-SK",	"Sikkim"),
    ("IN-TN",	"Tamil Nadu"),
    ("IN-TG",	"Telangana"),
    ("IN-TR",	"Tripura"),
    ("IN-UT",	"Uttarakhand"),
    ("IN-UP",	"Uttar Pradesh"),
    ("IN-WB",	"West Bengal"),
    ("IN-AN",	"Andaman and Nicobar Islands"),
    ("IN-CH",	"Chandigarh"),
    ("IN-DN",	"Dadra and Nagar Haveli"),
    ("IN-DD",	"Daman and Diu"),
    ("IN-DL",	"Delhi"),
    ("IN-LD",	"Lakshadweep"),
    ("IN-PY",	"Puducherry")
    )

status = (
    ("pending", "Pending Acceptance"),
    ("rejected", "Rejected"),
    ("changes", "Changes Required"),
    ("released", "Released")
)


def has_profile(user):
    """ check if user has profile """
    return True if hasattr(user, 'profile') else False


def attachments(instance, filename):
    return path.join(instance.animation.category.name,
                     instance.animation.title,
                     str(instance.animation.id), filename)

def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.mp4']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


class Profile(models.Model):
    """Profile for users(instructors and coordinators)"""

    user = models.OneToOneField(User)
    title = models.CharField(max_length=32, blank=True, choices=title)
    institute = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=150, choices=department_choices)
    phone_number = models.CharField(
                max_length=10,
                validators=[RegexValidator(
                                regex=r'^.{10}$', message=(
                                    "Phone number must be entered \
                                in the format: '9999999999'.\
                                Up to 10 digits allowed.")
                            )], null=False)
    position = models.CharField(max_length=32, choices=position_choices,
                                default='contributor')
    how_did_you_hear_about_us = models.CharField(max_length=255, blank=True,
                                                 choices=source)
    location = models.CharField(max_length=255, blank=True,
                                help_text="Place/City")
    state = models.CharField(max_length=255, choices=states, default="IN-MH")
    pincode = models.CharField(max_length=6, blank=True,
                               validators=[RegexValidator(
                                 regex=r'^.{6}$', message=(
                                    "Please enter valid PINCODE"
                                 )
                                )])
    is_email_verified = models.BooleanField(default=False)
    activation_key = models.CharField(max_length=255, blank=True, null=True)
    key_expiry_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return u"id: {0}| {1} {2} | {3} ".format(
                                            self.user.id,
                                            self.user.first_name,
                                            self.user.last_name,
                                            self.user.email
                                            )


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(default=timezone.now)
    description = models.TextField()

    def __str__(self):
        return u"{0}".format(self.name)


class Animation(models.Model):
    title = models.CharField(max_length=255)
    contributor = models.ForeignKey(User, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                                 related_name="%(app_label)s_%(class)s_related")
    outline = models.TextField()
    # concepts = models.TextField()
    # audience=models.TextField()
    status = models.CharField(max_length=255, choices=status)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(default=timezone.now)
    tags = TaggableManager()
    history = HistoricalRecords()

    def __str__(self):
        return u"{0} | {1}".format(self.title, self.status)


class Comment(models.Model):
    comment = models.TextField()
    commentor = models.ForeignKey(User, on_delete=models.CASCADE)
    animation = models.ForeignKey(Animation, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    animation_status = models.CharField(max_length=255)

    def __str__(self):
        return u"{1} | {0}".format(
            self.created_date,
            self.commentor
        )


class AnimationStats(models.Model):
    animation = models.ForeignKey(Animation, on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)
    like = models.PositiveIntegerField(default=0)
    dislike = models.PositiveIntegerField(default=0)
    thumbnail = models.ImageField(null=True, blank=True, upload_to=attachments)
    video_path = models.FileField(null=True, blank=True, upload_to=attachments, validators=[validate_file_extension])

    def _create_thumbnail(self):
        video_path = self.video_path.path
        img_output = path.join(
            tempfile.mkdtemp(),  "{0}.jpg".format(self.animation.title)
            )
        file_name = "{0}.jpg".format(self.animation.title)
        subprocess.call(['ffmpeg', '-i', video_path, '-ss', '00:00:02.000',
                        '-vframes', '1', img_output])
        if path.exists(img_output):
            que_file = open(img_output, 'rb')
            # Converting to Python file object with
            # some Django-specific additions
            django_file = File(que_file)
            self.thumbnail.save(file_name, django_file, save=True)

    def _create_ogv(self):
        video_input = self.video_path.path
        vid_output = path.join(
            tempfile.mkdtemp(),  "{0}.ogv".format(self.animation.title)
            )
        file_name = "{0}.ogv".format(self.animation.title)
        subprocess.call(['ffmpeg', '-i', video_input, '-r', '24', vid_output])
        if path.exists(vid_output):
            que_file = open(vid_output, 'rb')
            # Converting to Python file object with
            # some Django-specific additions
            django_file = File(que_file)
            self.video_path.save(file_name, django_file, save=True)
