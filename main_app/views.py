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
from .utils import match_count_function,match_count_function_match_data_list_ver

class Login(LoginView):
    form_class    = AuthenticationForm #ログインするためのform
    template_name = '../templates/login.html'
    next_page     = 'main'

class Logout(LogoutView):
    next_page = 'login'
    
#ユーザー登録のビュー
class Sign_up_View(View):  
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

class MainView(LoginRequiredMixin,View): #LoginRequiredMixinを追加することでログインしていないと見ることができないページとなる
    login_url           = '/login'
    redirect_field_name = 'login'

    #メイン画面を表示するためのクラス
    #セッションが登録されていた場合（検索フィルターのPOSTがされていたとき）、セッションに登録されているデータを表示。
    #セッションが登録されていない場合（検索フィルターのPOSTがされていないとき）、モデルからユーザー名でフィルターをかけて持ってくる

    def get(self,request):
        match_date_filter_form = DataFilterForm(request.POST or None)
        user_name              = request.user.username
        match_input_form       = Match_Data_Form(request.POST or None,initial={'date':date.today()})
        if 'processed_data' in request.session:
            processed_data    = request.session.get('processed_data', {})
            match_data        = processed_data.get('match_data')
            match_result_dict = processed_data.get('match_result_dict')
            filter_start_date = processed_data.get('filter_start_date')
            filter_end_date   = processed_data.get('filter_end_date')
            del request.session['processed_data']
            return render(request,'../templates/main.html',{
                'user_name'              : user_name,
                'match_input_form'       : match_input_form,
                'match_date_filter_form' : match_date_filter_form,
                'match_data'             : match_data,
                'match_result_dict'      : match_result_dict,
                'filter_start_date'      : filter_start_date,
                'filter_end_date'        : filter_end_date,
                'form_type'              : 'form_on',
            })
            
        else:
            match_data_query_results = Match_Data.objects.filter(user = user_name).order_by('-id') 
            if not match_data_query_results.exists():
                match_data = Match_Data.objects.none()
                match_result_dict = None
            else:
                match_data        = match_data_query_results
                match_result_dict = match_count_function(match_data_query_results)
            return render(request,'../templates/main.html',{
                'user_name'              : user_name,
                'match_input_form'       : match_input_form,
                'match_date_filter_form' : match_date_filter_form,
                'match_data'             : match_data,
                'match_result_dict'      : match_result_dict,
                'form_type'              : 'form_on',
            })

    def post(self,request):
        match_date_filter_form   = DataFilterForm(request.POST or None)
        match_input_form         = Match_Data_Form(request.POST or None)
        user_name                = request.user.username
        match_data_query_results = Match_Data.objects.filter(user = user_name).order_by('-id') 
        if not match_data_query_results.exists():
            match_data = Match_Data.objects.none()

        #「データをフィルターするform」が押された場合はセッションに登録
        #「試合を結果登録するform」が押されたときはformをモデルに保存する

        if 'date_filter_submit' in request.POST:
            if match_date_filter_form.is_valid():
                filter_start_date        = match_date_filter_form.cleaned_data['filter_start_date']
                filter_end_date          = match_date_filter_form.cleaned_data['filter_end_date']
                match_data_query_results = match_data_query_results.filter(date__range=[filter_start_date, filter_end_date])
                match_data_list          = list(match_data_query_results.values())
                match_result_dict        = match_count_function_match_data_list_ver(match_data_list)
                processed_data  = {
                    'match_result_dict': match_result_dict,
                    'match_data'       : match_data_list,
                    'filter_start_date': filter_start_date.strftime('%Y-%m-%d'),
                    'filter_end_date'  : filter_end_date.strftime('%Y-%m-%d')
                }
                request.session['processed_data'] = processed_data
                return redirect('main')
        elif 'match_data_submit' in request.POST:
            if match_input_form.is_valid():
                #commit=False は、モデルの保存を後で行うために一時的にフォームの保存を保留するためのもの
                match_data = match_input_form.save(commit=False) 
                #userを現在のログインユーザーに設定
                match_data.user = request.user  
                match_data.save() 
                return redirect('main')


class DeleteView(View):
    def get(self,request):
        match_data_query_results = Match_Data.objects.all()
        match_data_query_results.delete()
        return redirect('main')

class EditView(View):
    def get(self,request,*args,**kwargs):
        match_data_query_results = Match_Data.objects.get(id = self.kwargs['pk'])
        match_data_form = Match_Data_Form(request.POST or None,
                initial = {
                    'date'        : match_data_query_results.date,
                    'match_result': match_data_query_results.match_result,
                    'match_point' : match_data_query_results.match_point,
                    'match_leader': match_data_query_results.match_leader,
                    'memo'        : match_data_query_results.memo
                })
        return render(request,'edit.html',{
            'match_data_form' : match_data_form
        })

    def post(self,request,*args,**kwargs):
        match_data_query_results = Match_Data.objects.get(id =self.kwargs['pk'])
        match_data_form          = Match_Data_Form(request.POST, instance=match_data_query_results)
        if match_data_form.is_valid():
            match_data_form.save()
            return redirect('main')

class DetailView(View):
    def get(self,request,*args,**kwargs):
        user_name                = request.user.username
        match_date_filter_form   = DataFilterForm(request.POST or None)
        match_data_query_results = Match_Data.objects.filter(user = user_name).order_by('-id') 
        if not match_data_query_results.exists():
            match_data = Match_Data.objects.none()
        else:
            match_data = match_data_query_results
        #セッションに登録されているものあり
        if 'processed_data' in request.session:
            processed_data    = request.session.get('processed_data', {})
            match_result_dict = processed_data.get('match_result_dict')
            match_data        = processed_data.get('match_data')
            match_count       = processed_data.get('match_count')
            leader_counts     = processed_data.get('leader_counts')
            filter_start_date = processed_data.get('filter_start_date')
            filter_end_date   = processed_data.get('filter_end_date')
            del request.session['processed_data']
            return render(request,'../templates/detail.html',{
                'match_date_filter_form' : match_date_filter_form,
                'match_data'             : match_data,
                'match_result_dict'      : match_result_dict,
                'leader_counts'          : leader_counts,
                'match_count'            : match_count,
                'filter_start_date'      : filter_start_date,
                'filter_end_date'        : filter_end_date,
                'form_type'              : 'form_on',
            })
        #セッションに登録されているものなし。
        else:
            #対戦相手を集計するため
            leaders_list      = [leader.match_leader for leader in match_data] 
            #本来は、countで渡せるんだけど、辞書として認識しないので、dictで囲って辞書として渡してあげている
            leader_counts     = dict(Counter(leaders_list)) 
            match_result_dict = match_count_function(match_data)
            return render(request,'../templates/detail.html',{
                'match_date_filter_form' : match_date_filter_form,
                'match_data'             : match_data,
                'match_result_dict'      : match_result_dict,
                'leader_counts'          : leader_counts,
                'form_type'              : 'form_on',
            })
    
    def post(self,request,*args,**kwargs):
        match_date_filter_form   = DataFilterForm(request.POST or None)
        user_name                = request.user.username
        match_data_query_results = Match_Data.objects.filter(user = user_name).order_by('-id')
        if not match_data_query_results.exists():
            match_data = Match_Data.objects.none()
        #データをフィルターするformが押された場合はセッションに登録
        if 'date_filter_submit' in request.POST:
            if match_date_filter_form.is_valid():
                filter_start_date        = match_date_filter_form.cleaned_data['filter_start_date']
                filter_end_date          = match_date_filter_form.cleaned_data['filter_end_date']
                match_data_query_results = match_data_query_results.filter(date__range=[filter_start_date, filter_end_date])
                match_data_list          = list(match_data_query_results.values())
                leaders_list             = [leader.match_leader for leader in match_data_query_results] 
                #本来は、countで渡せるんだけど、辞書として認識しないので、dictで囲って辞書として渡してあげている
                leader_counts            = dict(Counter(leaders_list)) 
                match_result_dict        = match_count_function_match_data_list_ver(match_data_list)
                processed_data = { 
                    'match_result_dict' : match_result_dict,
                    'match_data'        : match_data_list,
                    'leader_counts'     : leader_counts,
                    'filter_start_date' : filter_start_date.strftime('%Y-%m-%d'),  # start_date も文字列に変換
                    'filter_end_date'   : filter_end_date.strftime('%Y-%m-%d')
                }
                request.session['processed_data'] = processed_data
                return redirect('detail')