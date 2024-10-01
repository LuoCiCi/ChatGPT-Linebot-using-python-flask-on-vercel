import requests
import os

# 獲取地震資料的主函數
def get_earthquake_data(start_time, end_time):
    try:
        result = fetch_earthquake_data(start_time, end_time)
        return result
    except Exception as err:
        print(err)
        raise ValueError(f"Error occurred: {err}")

# 用來請求地震資料的函數
def fetch_earthquake_data(start_time, end_time):
    url = (
        'https://opendata.cwb.gov.tw/api/v1/rest/datastore/E-A0016-001?'
        'Authorization=' + os.getenv('AUTHORIZATION') +
        '&limit=3' +
        '&timeFrom=' + start_time +
        '&timeTo=' + end_time
    )
    
    headers = {
        'accept': 'application/json'
    }

    # 發送 HTTP GET 請求
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")
    
    # 解析返回的 JSON 資料
    earthquake_all_data = response.json()

    if earthquake_all_data.get('success') != 'true':
        raise Exception('Failed to get earthquake data')

    earthquake_record = earthquake_all_data['records']['earthquake']
    
    # 取得每筆地震紀錄中的圖片 URI
    earthquake_result = [record['reportImageURI'] for record in earthquake_record]
    
    return earthquake_result

# 範例調用方式
if __name__ == '__main__':
    start_time = '2024-01-01T00:00:00'
    end_time = '2024-01-01T23:59:59'
    
    try:
        earthquake_images = get_earthquake_data(start_time, end_time)
        print(earthquake_images)
    except ValueError as e:
        print(f"An error occurred: {e}")
