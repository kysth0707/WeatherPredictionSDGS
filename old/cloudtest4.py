import cv2
import numpy as np

def extract_clouds(image_path, k=2):
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    
    image_2d = image.reshape((-1, 3))
    _, labels, centers = cv2.kmeans(image_2d.astype(np.float32), k, None,
                                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2),
                                    10, cv2.KMEANS_RANDOM_CENTERS)
    
    segmented_image = labels.reshape((height, width))
    cloud_cluster = np.argmax([np.mean(image[segmented_image == i]) for i in range(k)])
    cloud_mask = (segmented_image == cloud_cluster).astype(np.uint8) * 255
    
    return image, cloud_mask

def measure_brightness(image, mask):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.mean(gray_image[mask > 0])

def calculate_cloud_coverage(cloud_mask):
    return np.mean(cloud_mask > 0)

def is_cloud_bottom_bright(image_path, abs_brightness_threshold=100, rel_brightness_threshold=1.2, cloud_coverage_threshold=0.7):
    image, cloud_mask = extract_clouds(image_path)
    height, width, _ = image.shape
    
    # 구름 비율 계산
    cloud_coverage = calculate_cloud_coverage(cloud_mask)
    
    # 구름의 밑 부분 추출
    cloud_bottom_mask = np.zeros_like(cloud_mask)
    cloud_bottom_mask[int(2*height/3):height, :] = cloud_mask[int(2*height/3):height, :]
    
    # 하늘 부분 추출
    sky_mask = cv2.bitwise_not(cloud_mask)
    
    # 구름의 밑 부분 밝기 측정
    avg_cloud_brightness = measure_brightness(image, cloud_bottom_mask)
    
    # 하늘 부분 밝기 측정
    avg_sky_brightness = measure_brightness(image, sky_mask)
    
    # 상대 밝기 계산
    relative_brightness = avg_cloud_brightness / (avg_sky_brightness + 1e-5)

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
image_path = 'testclouds/2.jpg'

# 밝기 판단
result = is_cloud_bottom_bright(image_path)
print(result)
