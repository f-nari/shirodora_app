#試合数、勝敗数をカウントする関数
 
def match_count_function(match_data_query_results):
    match_result_dict = {
        'sum_point': 0,
        'win_count': 0,
        'lose_count': 0,
        'draw_count': 0,
        'match_count': 0,
    }
    for match in match_data_query_results:
        match_result_dict['sum_point'] = match_result_dict['sum_point'] + match.match_point
        if match.match_result == '完全勝利' or match.match_result == '点差勝利':
            match_result_dict['win_count'] += 1
        elif match.match_result == '完全敗北' or match.match_result == '点差敗北':
            match_result_dict['lose_count'] += 1
        else:
            match_result_dict['draw_count'] += 1
        match_result_dict['match_count'] += 1
    return match_result_dict 

#試合数、勝敗数をカウントする関数。match_dataがリストVer
def match_count_function_match_data_list_ver(match_data_list):
    match_result_dict = {
        "match_count": 0, 
        "win_count": 0, 
        "lose_count": 0, 
        "draw_count": 0, 
        "sum_point":0
    }
    for match in match_data_list:
        match_result_dict['sum_point']      = match_result_dict['sum_point'] + match["match_point"]
        match["date"]                       = match["date"].strftime('%Y-%m-%d')
        if match["match_result"]            == '完全勝利' or match["match_result"] == '点差勝利':
            match_result_dict['win_count']  += 1
        elif match["match_result"]          == '完全敗北' or match["match_result"] == '点差敗北':
            match_result_dict['lose_count'] += 1
        else:
            match_result_dict['draw_count'] += 1
        match_result_dict['match_count']    += 1
    
    return match_result_dict