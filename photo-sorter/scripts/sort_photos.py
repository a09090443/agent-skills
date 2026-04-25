import os
import shutil
import time
import argparse
import datetime
import json
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

def get_exif_data(image_path):
    exif_data = {}
    try:
        image = Image.open(image_path)
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]
                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value
    except Exception:
        pass
    return exif_data

def convert_to_degrees(value):
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data):
    lat = None
    lon = None
    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]
        gps_latitude = gps_info.get("GPSLatitude")
        gps_latitude_ref = gps_info.get("GPSLatitudeRef")
        gps_longitude = gps_info.get("GPSLongitude")
        gps_longitude_ref = gps_info.get("GPSLongitudeRef")

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = convert_to_degrees(gps_latitude)
            if gps_latitude_ref != "N":                     
                lat = 0 - lat
            lon = convert_to_degrees(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon
    return lat, lon

def get_photo_date(exif_data, file_path):
    date_str = None
    if "DateTimeOriginal" in exif_data:
        date_str = exif_data["DateTimeOriginal"]
    elif "DateTime" in exif_data:
        date_str = exif_data["DateTime"]
        
    if date_str and isinstance(date_str, str):
        try:
            # 嘗試解析 EXIF 預設時間格式
            dt = datetime.datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            return dt
        except Exception:
            pass
            
    # 如果沒有正確的時間，使用檔案系統的修改時間
    mtime = os.path.getmtime(file_path)
    return datetime.datetime.fromtimestamp(mtime)

def get_json_date(file_path):
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    name_no_ext, ext = os.path.splitext(base_name)
    
    candidates = [
        f"{base_name}.json",
        f"{base_name}.supplemental-metadata.json",
        f"{name_no_ext}.json",
        f"{name_no_ext}.json.supplemental-metadata.json"
    ]
    
    for candidate in candidates:
        json_path = os.path.join(dir_name, candidate)
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'photoTakenTime' in data and 'timestamp' in data['photoTakenTime']:
                        ts = int(data['photoTakenTime']['timestamp'])
                        return datetime.datetime.fromtimestamp(ts)
            except Exception:
                pass
    return None

def get_location_name(lat, lon, geolocator):
    try:
        time.sleep(1)
        location = geolocator.reverse(f"{lat}, {lon}", language="zh-TW")
        if location and location.raw.get('address'):
            address = location.raw['address']
            country = address.get('country', '')
            city = address.get('city', address.get('county', address.get('state', '')))
            town = address.get('town', address.get('city_district', address.get('district', address.get('suburb', ''))))
            poi = address.get('tourism', address.get('leisure', address.get('historic', address.get('amenity', address.get('shop', address.get('natural', address.get('village', address.get('hamlet', address.get('neighbourhood', '')))))))))
            
            parts = []
            for p in [country, city, town, poi]:
                if p and p not in parts:
                    parts.append(p)
            result = "_".join(parts)
            has_poi = bool(poi and poi != '')
            if not result:
                result = "未知地點"
            return result, has_poi
    except Exception as e:
        print(f"  [警告] 地理解析失敗 ({lat}, {lon}): {e}")
    return "未知地點", False

def get_unique_filename(target_dir, base_name, ext):
    counter = 1
    new_name = f"{base_name}{ext}"
    while os.path.exists(os.path.join(target_dir, new_name)):
        new_name = f"{base_name}_{counter}{ext}"
        counter += 1
    return new_name

def organize_photos(input_dir, output_dir):
    geolocator = Nominatim(user_agent="antigravity_skill_photo_sorter")
    cluster_centers = [] # 儲存 (lat, lon, folder_name)
    api_cache = {} # 儲存 (round_lat, round_lon) -> (folder_name, has_poi)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith('.json'):
                continue
                
            file_path = os.path.join(root, filename)
            exif_data = get_exif_data(file_path)
            
            # 取得相片時間
            dt = get_photo_date(exif_data, file_path)
            date_folder_str = dt.strftime('%Y-%m-%d')
            file_time_str = dt.strftime('%Y-%m-%d_%H-%M-%S')
            ext = os.path.splitext(filename)[1].lower()
            
            video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp'}
            if ext in video_extensions:
                print(f"處理中: {filename} - 影片檔案")
                json_dt = get_json_date(file_path)
                if json_dt:
                    dt = json_dt
                date_folder_str = dt.strftime('%Y-%m-%d')
                file_time_str = dt.strftime('%Y-%m-%d_%H-%M-%S')
                target_dir = os.path.join(output_dir, "影片", date_folder_str)
                target_base_name = file_time_str
            else:
                lat, lon = get_lat_lon(exif_data)
                
                if lat is not None and lon is not None:
                    print(f"處理中: {filename} - 座標: ({lat:.4f}, {lon:.4f})")
                    folder_name = None
                    
                    rounded_coord = (round(lat, 4), round(lon, 4))
                    if rounded_coord in api_cache:
                        raw_folder_name, has_poi = api_cache[rounded_coord]
                    else:
                        raw_folder_name, has_poi = get_location_name(lat, lon, geolocator)
                        api_cache[rounded_coord] = (raw_folder_name, has_poi)
                        
                    if has_poi:
                        folder_name = raw_folder_name
                        cluster_centers.append((lat, lon, folder_name))
                    else:
                        for c_lat, c_lon, c_name in cluster_centers:
                            dist = geodesic((lat, lon), (c_lat, c_lon)).km
                            if dist <= 0.2:
                                folder_name = c_name
                                print(f"  -> 無明確景點，但距離 [{c_name}] 小於 200 公尺 ({dist:.2f}km)，合併至同目錄")
                                break
                                
                        if folder_name is None:
                            folder_name = raw_folder_name
                            cluster_centers.append((lat, lon, folder_name))
                            print(f"  -> 建立新地點目錄: {folder_name}")
                    
                    target_dir = os.path.join(output_dir, folder_name)
                    target_base_name = file_time_str
                else:
                    print(f"處理中: {filename} - 無 GPS 資訊")
                    
                    json_dt = get_json_date(file_path)
                    if json_dt:
                        dt = json_dt
                    
                    date_folder_str = dt.strftime('%Y-%m-%d')
                    file_time_str = dt.strftime('%Y-%m-%d_%H-%M-%S')
                    
                    # 無座標：放到 [其他]/[日期]/ 目錄下
                    target_dir = os.path.join(output_dir, "其他", date_folder_str)
                    target_base_name = file_time_str
                
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            new_filename = get_unique_filename(target_dir, target_base_name, ext)
            target_path = os.path.join(target_dir, new_filename)
            
            try:
                shutil.copy2(file_path, target_path)
                print(f"  -> 已歸檔: {target_dir}\\{new_filename}")
            except Exception as e:
                print(f"  -> 複製失敗: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="依照 EXIF GPS 座標將照片自動分類到資料夾")
    parser.add_argument("-i", "--input", required=True, help="包含照片的輸入資料夾路徑")
    parser.add_argument("-o", "--output", required=True, help="分類後照片要輸出的資料夾路徑")
    args = parser.parse_args()
    
    print(f"開始整理照片...\n輸入目錄: {args.input}\n輸出目錄: {args.output}\n")
    print("-" * 30)
    organize_photos(args.input, args.output)
    print("-" * 30)
    print("處理完成！")
