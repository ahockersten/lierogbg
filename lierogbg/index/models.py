from django.db import models

class Player(models.Model):
    name = models.CharField(max_length = 100)
    real_name = models.CharField(max_length = 100, blank = True)
    ranking_points = models.IntegerField(default = 1000)
    pool_points = models.IntegerField(default = 0)

    def __unicode__(self):
        return u'%s %i %i' % (self.name, self.ranking_points, self.pool_points)

    def clean(self):
        pass

    class Meta:
        pass
