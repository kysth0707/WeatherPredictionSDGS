import cv2
import numpy as np

def extract_clouds(image_path):
    image = cv2.imread(image_path)
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 하늘 색상의 HSV 범위 설정 (푸른색, 노란색, 빨간색 포함)
    lower_sky_blue = np.array([90, 50, 50], dtype=np.uint8)
    upper_sky_blue = np.array([130, 255, 255], dtype=np.uint8)
    sky_mask_blue = cv2.inRange(hsv_image, lower_sky_blue, upper_sky_blue)
    
    lower_sky_yellow = np.array([15, 50, 50], dtype=np.uint8)
    upper_sky_yellow = np.array([35, 255, 255], dtype=np.uint8)
    sky_mask_yellow = cv2.inRange(hsv_image, lower_sky_yellow, upper_sky_yellow)
    
    lower_sky_red1 = np.array([0, 50, 50], dtype=np.uint8)
    upper_sky_red1 = np.array([10, 255, 255], dtype=np.uint8)
    sky_mask_red1 = cv2.inRange(hsv_image, lower_sky_red1, upper_sky_red1)
    
    lower_sky_red2 = np.array([160, 50, 50], dtype=np.uint8)
    upper_sky_red2 = np.array([180, 255, 255], dtype=np.uint8)
    sky_mask_red2 = cv2.inRange(hsv_image, lower_sky_red2, upper_sky_red2)
    
    # 모든 하늘 마스크를 합침
    sky_mask = cv2.bitwise_or(sky_mask_blue, sky_mask_yellow)
    sky_mask = cv2.bitwise_or(sky_mask, sky_mask_red1)
    sky_mask = cv2.bitwise_or(sky_mask, sky_mask_red2)
    
    # 구름 마스크는 하늘 마스크의 반전으로 정의
    cloud_mask = cv2.bitwise_not(sky_mask)
    
    return image, cloud_mask

def measure_brightness(image, mask):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.mean(gray_image[mask > 0])

def calculate_cloud_coverage(cloud_mask):
    cloud_pixels = np.sum(cloud_mask > 0)
    total_pixels = cloud_mask.size
    cloud_coverage = cloud_pixels / total_pixels
    return cloud_coverage

def get_absolute_brightness_threshold(timeOfPicture):
    if 6 <= timeOfPicture < 12:  # 오전
        return 150
    elif 12 <= timeOfPicture < 18:  # 오후
        return 200
    else:  # 저녁
        return 80

def color_correct(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    lab = cv2.merge((l, a, b))
    corrected_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return corrected_image

def brightness_correct(image, target_brightness=128):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    current_brightness = np.mean(gray_image)
    correction_factor = target_brightness / current_brightness
    corrected_image = cv2.convertScaleAbs(image, alpha=correction_factor, beta=0)
    return corrected_image

def extract_cloud_bottom(image, cloud_mask, bottom_fraction=0.33):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cloud_pixels = gray_image[cloud_mask > 0]
    
    # 구름 부분의 밝기 분포 계산
    sorted_indices = np.argsort(cloud_pixels)
    bottom_pixels_count = int(bottom_fraction * len(cloud_pixels))
    
    # 가장 어두운 부분 마스크 생성
    threshold_value = int(cloud_pixels[sorted_indices[bottom_pixels_count]])
    cloud_bottom_mask = cv2.inRange(gray_image, 0, threshold_value)
    cloud_bottom_mask = cv2.bitwise_and(cloud_bottom_mask, cloud_mask)
    
    return cloud_bottom_mask

def analyze_cloud_brightness(cloud_pixels):
    sorted_indices = np.argsort(cloud_pixels)
    lower_10_percent_idx = int(len(cloud_pixels) * 0.1)
    upper_10_percent_idx = int(len(cloud_pixels) * 0.9)
    
    lower_10_percent_brightness = np.mean(cloud_pixels[sorted_indices[:lower_10_percent_idx]])
    upper_10_percent_brightness = np.mean(cloud_pixels[sorted_indices[upper_10_percent_idx:]])
    
    return lower_10_percent_brightness, upper_10_percent_brightness

def is_cloud_bottom_bright(image_path, timeOfPicture, rel_brightness_threshold=1.2, cloud_coverage_threshold=0.9):
    image = cv2.imread(image_path)
    
    # 컬러 보정 및 밝기 보정 적용
    image = color_correct(image)
    image = brightness_correct(image)
    
    image, cloud_mask = extract_clouds(image_path)
    height, width, _ = image.shape
    
    # 구름 비율 계산
    cloud_coverage = calculate_cloud_coverage(cloud_mask)
    
    if cloud_coverage > cloud_coverage_threshold:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cloud_pixels = gray_image[cloud_mask > 0]
        lower_10_percent_brightness, upper_10_percent_brightness = analyze_cloud_brightness(cloud_pixels)
        
        if upper_10_percent_brightness > lower_10_percent_brightness:
            return "구름 가득 & 밝음"
        else:
            return "구름 가득 & 어두움"
    else:
        # 상대적 밝기 분석을 위해 구름의 밑 부분 추출
        cloud_bottom_mask = extract_cloud_bottom(image, cloud_mask)
        
        # 하늘 부분 추출
        sky_mask = cv2.bitwise_not(cloud_mask)
        
        # 구름의 밑 부분 밝기 측정
        avg_cloud_brightness = measure_brightness(image, cloud_bottom_mask)
        
        # 하늘 부분 밝기 측정
        avg_sky_brightness = measure_brightness(image, sky_mask)
        
        # 상대 밝기 계산
        relative_brightness = avg_cloud_brightness / (avg_sky_brightness + 1e-5)

        # 시간대에 따른 절대 밝기 임계값 설정
        abs_brightness_threshold = get_absolute_brightness_threshold(timeOfPicture)

        # 구름 비율에 따라 다른 기준 적용
        if cloud_coverage > cloud_coverage_threshold:
            # 구름이 대부분을 차지할 경우 절대 밝기 기준 사용
            if avg_cloud_brightness > abs_brightness_threshold:
                return "구름의 밑 부분이 밝습니다."
            else:
                return "구름의 밑 부분이 어둡습니다."
        else:
            # 구름이 부분적으로 있을 경우 상대 밝기 기준 사용
            if relative_brightness > rel_brightness_threshold:
                return "구름의 밑 부분이 밝습니다."
            else:
                return "구름의 밑 부분이 어둡습니다."

# 이미지 경로
image_path = 'testclouds/5.jpg'

# 시간대 정보 (예: 14시는 오후 2시)
timeOfPicture = 14

# 밝기 판단
result = is_cloud_bottom_bright(image_path, timeOfPicture)
print(result)
