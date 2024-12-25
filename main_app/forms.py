from django import forms
from django.forms import DateInput
from .models import Match_Data


class Match_Data_Form(forms.ModelForm): #モデルのデータをそのまま使う
    class Meta:
        model = Match_Data
        #fields = '__all__'
        fields = ['date', 'match_result', 'match_point', 'match_leader', 'memo']
        # HTMLでCSSをいじりたい。クラスをつけたいのだけど、このwidgetでクラスを追加する方法が簡単だった
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class':'form-date',
                'placeholder': '日付を選択' #これは表示されなかった。仕様のためしょうがない
                }),
            'match_result':forms.Select(attrs={
                'class': 'form-match-result',
                'placeholder':'試合結果を選択'
            }),
            'match_point':forms.NumberInput(attrs={
                'class': 'form-match-point',
                'placeholder':'増減つよPを入力。※半角英数字'
            }),
            'match_leader':forms.TextInput(attrs={
                'class': 'form-match-leader',
                'placeholder':'相手リーダーを入力'
            }),
            'memo':forms.Textarea(attrs={
                'class': 'form-memo',
                'placeholder':'メモを入力',
                'rows':4
            }),
        }
        
        
        
class DataFilterForm(forms.Form):
    filter_start_date = forms.DateField(
        widget = forms.DateInput(attrs = {
            'type': 'date',
            'class':'form-date',#あとでクラス変える
            'placeholder': '開始日を選択'#多分映らない
        }),
        
    )
    filter_end_date = forms.DateField(
        widget = forms.DateInput(attrs = {
            'type': 'date',
            'class':'form-date',#あとでクラス変える
            'placeholder': '開始日を選択'#多分映らない
        }),
        
    )