from logging import Logger
from typing import Any, Optional

import python_lib_for_me
import tweepy


def has_twitter_list(api: tweepy.API, list_name: str) -> bool:
    '''Twitterリスト存在確認'''
    
    lg: Optional[Logger] = None
    
    try:
        lg = python_lib_for_me.get_logger(__name__)
        
        twitter_lists: Any = api.get_lists()
        
        if isinstance(twitter_lists, tweepy.List):
            for twitter_list in twitter_lists:
                if twitter_list.name == list_name:
                    lg.info(f'Twitterリストが既に存在します。(リスト名：{twitter_list.name})')
                    return True
    except Exception as e:
        raise(e)
    
    return False


def generate_twitter_list(api: tweepy.API, twitter_list_name: str) -> tweepy.List:
    '''Twitterリスト作成'''
    
    lg: Optional[Logger] = None
    
    try:
        lg = python_lib_for_me.get_logger(__name__)
        
        twitter_list: Any = api.create_list(twitter_list_name, mode='private', description='')
        lg.info(f'Twitterリスト作成に成功しました。(リスト名：{twitter_list.name})')
    except Exception as e:
        if lg is not None:
            lg.info(f'Twitterリスト作成に失敗しました。')
        raise(e)
    
    return twitter_list


def add_user(api: tweepy.API, twitter_list: tweepy.List, user_id: str, user_name: str) -> None:
    '''ユーザ追加'''
    
    lg: Optional[Logger] = None
    
    try:
        lg = python_lib_for_me.get_logger(__name__)
        
        api.add_list_member(list_id=twitter_list.id, screen_name=user_id)
        lg.info(f'ユーザ追加に成功しました。(ユーザID：{user_id: <20}、ユーザ名：{user_name})')
    except Exception as e:
        # ユーザが鍵付きや削除済みなどの場合
        if lg is not None:
            lg.info(f'ユーザ追加に失敗しました。(ユーザID：{user_id: <20}、ユーザ名：{user_name})')
    
    return None
