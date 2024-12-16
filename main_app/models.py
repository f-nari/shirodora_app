from django.db import models

class Match_Data(models.Model):
    MATCH_RESULT = (
        ('完全勝利','完全勝利'),
        ('点差勝利','点差勝利'),
        ('引き分け','引き分け'),
        ('点差敗北','点差敗北'),
        ('完全敗北','完全敗北'),
    ) # 選択肢の変数は定義より先にしなければならない
    
    user = models.CharField(max_length = 255,)
    date = models.DateField()
    match_result = models.CharField(max_length = 15,choices =MATCH_RESULT)
    match_point = models.IntegerField()
    match_leader = models.CharField(max_length = 255)
    memo = models.TextField(blank=True)
    

