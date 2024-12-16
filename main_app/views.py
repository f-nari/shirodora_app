from django.shortcuts import render,redirect
from django.contrib.auth.views import LoginView,LogoutView
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from .models import Match_Data
from .forms import Match_Data_Form,DataFilterForm
from datetime import date
from collections import Counter #対戦りーだーの登場回数を計算するため。DetailViewで使用

class Login(LoginView):
    form_class = AuthenticationForm #ログインするためのform
    template_name = '../templates/login.html'
    next_page = 'main'


class Logout(LogoutView):
    next_page = 'login'
    
class Sign_up_View(View):  #ユーザー登録のビュー
    def get(self,request):
        form = UserCreationForm()
        return render(request,'../templates/user_creation.html',{
            'form':form
        })

    def post(self,request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            error_message = form.errors
            return render(request,'../templates/user_creation.html',{
                'form':form
            })

class StrongPointView(LoginRequiredMixin,View): #LoginRequiredMixinを追加することでログインしていないと見ることができないページとなる
    login_url ='/login'  #ログインしていないときのダイレクトのURL
    redirect_field_name = 'login' #上のURLの名前。
    #セッションに登録はできたけど、ここで、見るとセッションに登録されていない
    def get(self,request):
        match_count = {"match_count": 0, "win_count": 0, "lose_count": 0, "draw_count": 0, "sum_point":0}
        date_filter_form = DataFilterForm(request.POST or None) #絞り込みフォームを表示
        user = request.user.username
        form = Match_Data_Form(request.POST or None,initial={'date':date.today()}) #フォームの日付に今日の日付をいれる
        #セッションがあれば、以下の文に移動
        if 'processed_data' in request.session:
            processed_data = request.session.get('processed_data', {})
            match_data = processed_data.get('match_data')
            match_count = processed_data.get('match_count')
            start_date = processed_data.get('start_date')
            end_date  = processed_data.get('end_date')
            del request.session['processed_data'] #セッションを削除
            return render(request,'../templates/main.html',{
                'user':user,
                'form':form,
                'date_filter_form':date_filter_form,
                'match_data':match_data,
                'match_count':match_count,
                'start_date':start_date,
                'end_date':end_date,
                'form_type':'form_on',
            })
        else:
            match_data = Match_Data.objects.filter(user = user).order_by('-id') #これで自分で登録したものが自分だけで見れるし、データだ登録した順で並べることだできる
            if not match_data.exists():
                #match_data = 'None'
                match_data = Match_Data.objects.none()
            else:
                for match in match_data: #勝利数等々を集計する
                    match_count['sum_point'] = match_count['sum_point'] + match.match_point
                    if match.match_result == '完全勝利' or match.match_result == '点差勝利':
                        match_count['win_count'] += 1
                    elif match.match_result == '完全敗北' or match.match_result == '点差敗北':
                        match_count['lose_count'] += 1
                    else:
                        match_count['draw_count'] += 1
                    match_count['match_count'] += 1

            return render(request,'../templates/main.html',{
                'user':user,
                'form':form,
                'date_filter_form':date_filter_form,
                'match_data':match_data,
                'match_count':match_count,
                'form_type':'form_on',
            })

    def post(self,request):
        match_count = {"match_count": 0, "win_count": 0, "lose_count": 0, "draw_count": 0, "sum_point":0} #日付をフィルターするため(セッションに登録するため)に必要
        date_filter_form = DataFilterForm(request.POST or None)
        form = Match_Data_Form(request.POST or None)
        user = request.user.username
        match_data = Match_Data.objects.filter(user = user).order_by('-id') #日付をフィルターするため(セッションに登録するため)に必要
        if not match_data.exists():
            match_data = Match_Data.objects.none()
        if 'date_filter_submit' in request.POST:
            if date_filter_form.is_valid():
                start_date = date_filter_form.cleaned_data['start_date']
                end_date = date_filter_form.cleaned_data['end_date']
                match_data = match_data.filter(date__range=[start_date, end_date])
                match_data_list = list(match_data.values())
                for match in match_data_list: #勝利数等々を集計する
                    match_count['sum_point'] = match_count['sum_point'] + match["match_point"]
                    match["date"] = match["date"].strftime('%Y-%m-%d')
                    if match["match_result"] == '完全勝利' or match["match_result"] == '点差勝利':
                        match_count['win_count'] += 1
                    elif match["match_result"] == '完全敗北' or match["match_result"] == '点差敗北':
                        match_count['lose_count'] += 1
                    else:
                        match_count['draw_count'] += 1
                    match_count['match_count'] += 1
                #セッションに登録
                processed_data = { 
                    'match_count': match_count,
                    'match_data':match_data_list,
                    'start_date': start_date.strftime('%Y-%m-%d'),  # start_date も文字列に変換
                    'end_date': end_date.strftime('%Y-%m-%d')
                }
                request.session['processed_data'] = processed_data
                return redirect('main')

        elif 'match_data_submit' in request.POST:
            if form.is_valid():
                match_data = form.save(commit=False) #commit=False は、モデルの保存を後で行うために一時的にフォームの保存を保留するためのもの
                match_data.user = request.user  # userを現在のログインユーザーに設定
                match_data.save() 
                return redirect('main')


class DeleteView(View):
    def get(self,request):
        match_data = Match_Data.objects.all()
        match_data = Match_Data.objects.all()
        match_data.delete()
        return redirect('main')

class EditView(View):
    def get(self,request,*args,**kwargs):
        match_data = Match_Data.objects.get(id = self.kwargs['pk'])
        match_data_form = Match_Data_Form(request.POST or None,
                            initial = {
                                'date' :match_data.date,
                                'match_result':match_data.match_result,
                                'match_point':match_data.match_point,
                                'match_leader':match_data.match_leader,
                                'memo':match_data.memo
                            })
                
        return render(request,'edit.html',{
            'match_data_form':match_data_form
        })
        
    def post(self,request,*args,**kwargs):
        match_data = Match_Data.objects.get(id =self.kwargs['pk'])
        match_data_form = Match_Data_Form(request.POST, instance=match_data)

        if match_data_form.is_valid():
            match_data_form.save()
            print('上書きされます')
            return redirect('main')
        
        
class DetailView(View):
    def get(self,request,*args,**kwargs):
        match_count = {"match_count": 0, "win_count": 0, "lose_count": 0, "draw_count": 0, "sum_point":0}
        user = request.user.username
        date_filter_form = DataFilterForm(request.POST or None) #絞り込みフォームを表示
        match_data = Match_Data.objects.filter(user = user).order_by('-id') #これで自分で登録したものが自分だけで見れるし、データだ登録した順で並べることだできる
        if not match_data.exists():
            match_data = Match_Data.objects.none()
            #match_data = 'None'
            #return redirect('detail')

        if 'processed_data' in request.session:
            processed_data = request.session.get('processed_data', {})
            match_data = processed_data.get('match_data')
            match_count = processed_data.get('match_count')
            leader_counts = processed_data.get('leader_counts')
            start_date = processed_data.get('start_date')
            end_date  = processed_data.get('end_date')
            del request.session['processed_data'] #セッションを削除
            
            return render(request,'../templates/detail.html',{
                'date_filter_form':date_filter_form,
                'match_data':match_data,
                'leader_counts':leader_counts,
                'match_count':match_count,
                'start_date':start_date,
                'end_date':end_date,
                'form_type':'form_on',
            })
            
        else:
            leaders = [leader.match_leader for leader in match_data] #対戦相手を集計するため
            leader_counts = dict(Counter(leaders)) #本来は、countで渡せるんだけど、辞書として認識しないので、dictで囲って辞書として渡してあげている
            for match in match_data: #勝利数等々を集計する
                match_count['sum_point'] = match_count['sum_point'] + match.match_point
                if match.match_result == '完全勝利' or match.match_result == '点差勝利':
                    match_count['win_count'] += 1
                elif match.match_result == '完全敗北' or match.match_result == '点差敗北':
                    match_count['lose_count'] += 1
                else:
                    match_count['draw_count'] += 1
                match_count['match_count'] += 1
                
            return render(request,'../templates/detail.html',{
                'date_filter_form':date_filter_form,
                'match_data':match_data,
                'match_count':match_count,
                'leader_counts':leader_counts,
                'form_type':'form_on',
            })
    
    def post(self,request,*args,**kwargs):
        match_count = {"match_count": 0, "win_count": 0, "lose_count": 0, "draw_count": 0, "sum_point":0}
        date_filter_form = DataFilterForm(request.POST or None)
        user = request.user.username
        match_data = Match_Data.objects.filter(user = user).order_by('-id')
        if not match_data.exists():
            match_data = Match_Data.objects.none()
            #match_data = 'None'
            #return match_data
        if 'date_filter_submit' in request.POST:
            if date_filter_form.is_valid():
                start_date = date_filter_form.cleaned_data['start_date']
                end_date = date_filter_form.cleaned_data['end_date']
                match_data = match_data.filter(date__range=[start_date, end_date])
                match_data_list = list(match_data.values())
                leaders = [leader.match_leader for leader in match_data] #対戦相手を集計するため
                leader_counts = dict(Counter(leaders)) #本来は、countで渡せるんだけど、辞書として認識しないので、dictで囲って辞書として渡してあげている
                for match in match_data_list: #勝利数等々を集計する
                    match_count['sum_point'] = match_count['sum_point'] + match["match_point"]
                    match["date"] = match["date"].strftime('%Y-%m-%d')
                    if match["match_result"] == '完全勝利' or match["match_result"] == '点差勝利':
                        match_count['win_count'] += 1
                    elif match["match_result"] == '完全敗北' or match["match_result"] == '点差敗北':
                        match_count['lose_count'] += 1
                    else:
                        match_count['draw_count'] += 1
                    match_count['match_count'] += 1
                    
                #セッションに登録
                processed_data = { 
                    'match_count': match_count,
                    'match_data':match_data_list,
                    'leader_counts':leader_counts,
                    'start_date': start_date.strftime('%Y-%m-%d'),  # start_date も文字列に変換
                    'end_date': end_date.strftime('%Y-%m-%d')
                }
                request.session['processed_data'] = processed_data
                return redirect('detail')
            
            
            