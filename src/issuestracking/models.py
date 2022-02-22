from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Project(models.Model):
    """
    Project model that allow to save project under development.

    Only author is allowed to modify the project.
    """
    title = models.CharField(_('title'), max_length=128, unique=True)
    description = models.CharField(_('description'), max_length=256)
    type = models.CharField(_('type'), max_length=128)

    def __str__(self):
        return f"{self.title}"


class Contributor(models.Model):
    """
    Contributors are users and added by the author of the project.

    They are allowed to add issues and comments.
    """
    CREATOR, CONTRIBUTOR = 'CREA', 'CONT'
    PERMISSIONS = [
        (CREATOR, 'Créateur'),
        (CONTRIBUTOR, 'Contributeur'),
    ]

    PROJECT_MANAGER, PROJECT_STAFF = 'PM', 'PS'
    ROLE_CHOICES = [
        (PROJECT_MANAGER, 'Project manager'),
        (PROJECT_STAFF, 'Project staff'),
    ]

    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             related_name='users')
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE,
                                related_name='projects')
    permission = models.CharField(max_length=128, choices=PERMISSIONS,
                                  default=CONTRIBUTOR)
    role = models.CharField(max_length=128, choices=ROLE_CHOICES,
                            default=PROJECT_STAFF)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'project'],
                                    name=('no_double_contributor')),
        ]


class Issue(models.Model):
    """
    Issue object, to track problems on a given project.
    """
    LOW, MEDIUM, HIGH = 'LOW', 'MED', 'SUP'
    PRIORITY_CHOICES = [
        (LOW, 'FAIBLE'),
        (MEDIUM, 'MOYENNE'),
        (HIGH, 'ÉLEVÉE'),
    ]
    BUG, IMPROVE, TASK = 'BUG', 'IMP', 'TSK'
    TAG_CHOICES = [
        (BUG, 'BUG'),
        (IMPROVE, 'AMÉLIORATION'),
        (TASK, 'TÂCHE'),
    ]
    TODO, DOING, DONE = 'TOD', 'DOI', 'DON'
    STATUS_CHOICES = [
        (TODO, 'À faire'),
        (DOING, 'En cours'),
        (DONE, 'Terminé'),
    ]

    title = models.CharField(_('title'), max_length=128, unique=True)
    description = models.CharField(_('description'), max_length=256)
    tag = models.CharField(_('tag'), max_length=3,
                           choices=TAG_CHOICES, default=BUG)
    priority = models.CharField(_('priority'), max_length=3,
                                choices=PRIORITY_CHOICES, default=LOW)
    status = models.CharField(_('status'), max_length=3,
                              choices=STATUS_CHOICES, default=TODO)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE)
    assignee_user = models.ForeignKey(to=User, on_delete=models.SET_NULL,
                                      blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    description = models.CharField(_('description'), max_length=256)
    author = models.ForeignKey(to=User, on_delete=models.SET_NULL,
                               blank=True, null=True)
    issue = models.ForeignKey(to=Issue, on_delete=models.SET_NULL,
                              blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
