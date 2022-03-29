import argparse
import os
import sys
from logging import Logger
from typing import Optional

import python_lib_for_me as pyl
import tweepy

from twitter_app.logic import twitter_api_auth, twitter_tweet_stream


def main() -> int:
    
    '''
    メイン
    
    Summary:
        コマンドラインから実行する。
        
        引数を検証して問題ない場合、指定したキーワードのツイートを配信する。
    
    Args:
        -
    
    Args on cmd line:
        user_id_for_followees (str)     : [グループB][1つのみ必須] ユーザID(フォロイー用)
        list_id (str)                   : [グループB][1つのみ必須] リストID
        list_name (str)                 : [グループB][1つのみ必須] リスト名
        following_user_file_path (str)  : [グループB][1つのみ必須] フォローユーザファイルパス
        keyword_of_csv_format (str)     : [グループC][任意] キーワード(csv形式)
        header_line_num (int)           : [グループC][任意] ヘッダ行番号
    
    Returns:
        int: 終了コード(0：正常、1：異常)
    '''
    
    lg: Optional[Logger] = None
    
    try:
        # ロガーの取得
        lg = pyl.get_logger(__name__)
        
        # 実行コマンドの表示
        sys.argv[0] = os.path.basename(sys.argv[0])
        pyl.log_inf(lg, f'実行コマンド：{sys.argv}')
        
        # 引数の取得・検証
        args: argparse.Namespace = __get_args()
        if __validate_args(args) == False:
            return 1
        
        # ロジック(TwitterAPI認証)の実行
        api: tweepy.API = twitter_api_auth.do_logic_that_generate_api_by_oauth_1_user()
        
        # ロジック(Twitterツイート配信)の実行
        if args.user_id_for_followees is not None:
            twitter_tweet_stream.do_logic(
                    api,
                    twitter_tweet_stream.EnumOfItemProcTarget.USER_ID,
                    args.user_id_for_followees,
                    args.keyword_of_csv_format,
                    int(args.header_line_num)
                )
        elif args.list_id is not None:
            twitter_tweet_stream.do_logic(
                    api,
                    twitter_tweet_stream.EnumOfItemProcTarget.LIST_ID,
                    args.list_id,
                    args.keyword_of_csv_format,
                    int(args.header_line_num)
                )
        elif args.list_name is not None:
            twitter_tweet_stream.do_logic(
                    api,
                    twitter_tweet_stream.EnumOfItemProcTarget.LIST_NAME,
                    args.list_name,
                    args.keyword_of_csv_format,
                    int(args.header_line_num)
                )
        elif args.following_user_file_path is not None:
            twitter_tweet_stream.do_logic(
                    api,
                    twitter_tweet_stream.EnumOfItemProcTarget.FILE_PATH,
                    args.following_user_file_path,
                    args.keyword_of_csv_format,
                    int(args.header_line_num)
                )
    except KeyboardInterrupt as e:
        if lg is not None:
            pyl.log_inf(lg, f'処理を中断しました。')
    except Exception as e:
        if lg is not None:
            pyl.log_exc(lg, '')
        return 1
    
    return 0


def __get_args() -> argparse.Namespace:
    '''引数取得'''
    
    try:
        parser: pyl.CustomArgumentParser = pyl.CustomArgumentParser(
                description='Twitterツイート配信\n' +
                            '指定したキーワードのツイートを配信します',
                formatter_class=argparse.RawTextHelpFormatter,
                exit_on_error=True
            )
        
        help_: str = ''
        
        # グループBの引数(1つのみ必須な引数)
        arg_group_b: argparse._ArgumentGroup = parser.add_argument_group(
            'Group B - only one required arguments',
            '1つのみ必須な引数\n処理対象の項目を指定します')
        mutually_exclusive_group_a: argparse._MutuallyExclusiveGroup = \
            arg_group_b.add_mutually_exclusive_group(required=True)
        help_ = '{0}\n{1}'
        mutually_exclusive_group_a.add_argument(
            '-ui', '--user_id_for_followees',
            type=str,
            help=help_.format(
                'ユーザID(フォロイー用)', '指定したユーザIDのフォロイーのツイートを配信する'))
        mutually_exclusive_group_a.add_argument(
            '-li', '--list_id',
            type=str,
            help=help_.format(
                'リストID', '指定したリストIDのツイートを配信する'))
        mutually_exclusive_group_a.add_argument(
            '-ln', '--list_name',
            type=str,
            help=help_.format(
                'リスト名', '指定したリスト名のツイートを配信する'))
        mutually_exclusive_group_a.add_argument(
            '-fp', '--following_user_file_path',
            type=str,
            help=help_.format(
                'フォローユーザファイルパス (csvファイル)',
                '指定したファイルに記載されているユーザのツイートを配信する'))
        
        # グループCの引数(任意の引数)
        arg_group_c: argparse._ArgumentGroup = parser.add_argument_group(
            'Group C - optional arguments', '任意の引数')
        help_ = 'キーワード(csv形式)\n' + \
                '例："Google Docs, Google Drive"\n' + \
                'スペースはAND検索(Google AND Docs)\n' + \
                'カンマはOR検索(Google Docs OR Google Drive)'
        arg_group_c.add_argument('-k', '--keyword_of_csv_format', type=str, default='', help=help_)
        help_ = 'ヘッダ行番号 (デフォルト：%(default)s)\n' + \
                'フォローユーザファイルパスのヘッダ行番号\n' + \
                '0：ヘッダなし、1~：ヘッダとなるファイルの行番号'
        arg_group_c.add_argument('-hd', '--header_line_num', type=int, default='1', help=help_)
        
        args: argparse.Namespace = parser.parse_args()
    except Exception as e:
        raise(e)
    
    return args


def __validate_args(args: argparse.Namespace) -> bool:
    '''引数検証'''
    
    lg: Optional[Logger] = None
    
    try:
        # ロガーの取得
        lg = pyl.get_logger(__name__)
        
        # 検証：グループAの引数が指定された場合は1文字以上であること
        if args.user_id_for_followees is not None \
            and not (len(args.user_id_for_followees) >= 1):
            pyl.log_war(lg, f'ユーザID(フォロイー用)が1文字以上ではありません。' +
                            f'(user_id_for_followees:{args.user_id_for_followees})')
            return False
        elif args.list_id is not None \
            and not (len(args.list_id) >= 1):
            pyl.log_war(lg, f'リストIDが1文字以上ではありません。' +
                            f'(list_id:{args.list_id})')
            return False
        elif args.list_name is not None \
            and not (len(args.list_name) >= 1):
            pyl.log_war(lg, f'リスト名が1文字以上ではありません。' +
                            f'(list_name:{args.list_name})')
            return False
        elif args.following_user_file_path is not None \
            and not (len(args.following_user_file_path) >= 1):
            pyl.log_war(lg, f'フォローユーザファイルパスが1文字以上ではありません。' +
                            f'(following_user_file_path:{args.following_user_file_path})')
            return False
        
        # 検証：フォローユーザファイルパスがcsvファイルのパスであること
        if args.following_user_file_path is not None \
            and not (os.path.splitext(args.following_user_file_path)[1] == '.csv'):
            pyl.log_war(lg, f'フォローユーザファイルパスがcsvファイルのパスではありません。' +
                            f'(following_user_file_path:{args.following_user_file_path})')
            return False
        
        # 検証：フォローユーザファイルパスのファイルが存在すること
        if args.following_user_file_path is not None \
            and not (os.path.isfile(args.following_user_file_path) == True):
            pyl.log_war(lg, f'フォローユーザファイルパスのファイルが存在しません。' +
                            f'(following_user_file_path:{args.following_user_file_path})')
            return False
        
        # 検証：ヘッダ行番号が0以上であること
        if not (int(args.header_line_num) >= 0):
            pyl.log_war(lg, f'ヘッダ行番号が0以上ではありません。' +
                            f'(header_line_num:{args.header_line_num})')
            return False
    except Exception as e:
        raise(e)
    
    return True


if __name__ == '__main__':
    sys.exit(main())
