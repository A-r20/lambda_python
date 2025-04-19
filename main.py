import os
import json
import boto3
import matplotlib.pyplot as plt
import pandas as pd
import io
#import japanize_matplotlib

os.environ['MPLCONFIGDIR'] = '/tmp'

def lambda_handler(event, context):
    try:
        s3_client = boto3.client('s3')
        bucket_name = event['Records'][0]['s3']['bucket']['name'].strip()
        key_name = event['Records'][0]['s3']['object']['key']
        response = s3_client.get_object(Bucket=bucket_name, Key=key_name)
        
        # CSVファイルの読み込み
        df = pd.read_csv(io.BytesIO(response['Body'].read()), encoding='utf-8-sig')

        
        # 顧客名の取得
        df_category = df['顧客名'].unique().tolist()

        total_amounts = []

        for name in df_category:
            category_name = df[df['顧客名'] == name]
            sum_user = category_name['購入金額'].sum()
            total_amounts.append(sum_user)

        # グラフの作成
        fig, ax = plt.subplots(figsize=(10,6))
        ax.plot(df_category, total_amounts, color='skyblue', marker='^', markersize=10, label='blue')
        ax.set_title('顧客別、商品購入金額', fontsize=16)
        ax.set_xlabel('顧客名', fontsize=12)
        ax.set_ylabel('合計購入額', fontsize=12, rotation='horizontal')
        ax.grid()
        plt.xticks(rotation=45, ha='right')
        print("tight_layout() 実行前")
        plt.tight_layout()

        # 画像として保存
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        print("画像変換完了、seek(0) 実行します")
        buffer.seek(0)
        print("S3 にアップロード開始")

        # 画像のアップロード
        image_key = 'output/test.png'
        s3_client.put_object(Bucket=bucket_name, Key=image_key, Body=buffer, ContentType='image/png')
        print("アップロード完了")
        
        result = f'グラフをS3に保存しました: s3://{bucket_name}/{image_key}'
        print(result)

        return {
            'statusCode': 200,
            'body': result
        }

    except Exception as e:
        # エラーハンドリング
        print(f"エラーが発生しました: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"エラーが発生しました: {str(e)}"
        }
