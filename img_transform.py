
from sklearn.cluster import KMeans
from pdf2image import convert_from_path
import io
from io import BytesIO
import cv2
import numpy as np


# For the manual writing, we will convert it to image
def pdf_to_images(pdf_file):
    images = convert_from_path(pdf_file)

    images_as_bytes = []
    multiple_rectangles = []

    for image in images:
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        
        cropped_image_path = "./test/10_temp_cropped_image.jpeg"
        with open("./test/01_temp_image.jpeg", "wb") as f:
            f.write(img_bytes.getvalue())
        
        # Check if there are multiple rectangles
        are_multiple_rectangles = crop_central_line("./test/01_temp_image.jpeg", cropped_image_path)
        multiple_rectangles.append(are_multiple_rectangles)

        # os.remove("temp_image.jpeg")

        with open(cropped_image_path, "rb") as f:
            cropped_img_bytes = f.read()
        # os.remove(cropped_image_path)

        images_as_bytes.append(cropped_img_bytes)

    return images_as_bytes, multiple_rectangles


# For the manual writing, we will crop it  
def crop_central_line(image_path, output_path, padding=10):
    # Load the image using OpenCV
    img = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to create a mask
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours in the binary image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Calculate the bounding boxes of the contours
    bounding_boxes = [cv2.boundingRect(cnt) for cnt in contours]

    # Calculate the y-coordinate of the center of each bounding box
    centers_y = [y + h//2 for _, y, _, h in bounding_boxes]

    # Apply k-means clustering to group the elements based on their y-coordinate centers
    kmeans = KMeans(n_clusters=3, n_init=10, random_state=0).fit(np.array(centers_y).reshape(-1, 1))

    # Find the cluster labels and sort them based on the cluster centers
    sorted_labels = sorted(range(3), key=lambda i: kmeans.cluster_centers_[i])

    if len(sorted_labels) == 2:
        # If there are only 2 clusters, assume the central line is the one with the highest y-coordinate (i.e., the second line)
        median_label = sorted_labels[1]
    else:
        # Otherwise, find the cluster label corresponding to the median y-coordinate
        median_label = sorted_labels[1]

    # Get the bounding boxes belonging to the central line
    central_line_bboxes = [bbox for bbox, label in zip(bounding_boxes, kmeans.labels_) if label == median_label]

    # Save an image with bounding boxes drawn for debugging
    img_with_bboxes = img.copy()
    for x, y, w, h in central_line_bboxes:
        cv2.rectangle(img_with_bboxes, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imwrite('./test/02_debug_image_with_bboxes.jpeg', img_with_bboxes)
    
    # Check if there are multiple rectangles
    unique_rectangles = []
    for rect1 in central_line_bboxes:
        is_inside = False
        for rect2 in central_line_bboxes:
            if (rect1 != rect2) and (rect1[0] > rect2[0]) and (rect1[1] > rect2[1]) and (rect1[0] + rect1[2] < rect2[0] + rect2[2]) and (rect1[1] + rect1[3] < rect2[1] + rect2[3]):
                is_inside = True
                break
        if not is_inside:
            unique_rectangles.append(rect1)


    # Find the minimum and maximum x-coordinates and y-coordinates of the elements in the central line
    min_x = min([x for x, _, _, _ in central_line_bboxes])
    max_x = max([x + w for x, _, w, _ in central_line_bboxes])
    min_y = min([y for _, y, _, _ in central_line_bboxes])
    max_y = max([y + h for _, y, _, h in central_line_bboxes])

    # Extract the corresponding region with optional padding
    cropped_img = img[min_y - padding:max_y + padding, min_x - padding:max_x + padding]

    img_with_mask = detect_border_touching_objects(cropped_img)

    # Save the cropped image
    cv2.imwrite(output_path, img_with_mask)

    # Return the number of central_line_bboxes
    return len(unique_rectangles) > 1

def detect_border_touching_objects(image):
    # Method 3: Use distance transform to find objects touching the border
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('./test/03_gray.jpeg', gray)
    
    # Thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite('./test/04_thresh.jpeg', thresh)
    
    # Find contours of objects
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create a mask covering objects touching the image boundaries
    mask = np.zeros_like(gray)
    for cnt in contours:
        _, _, w, h = cv2.boundingRect(cnt)
        if w == image.shape[1] or h == image.shape[0]:
            cv2.drawContours(mask, [cnt], -1, 255, cv2.FILLED)
    cv2.imwrite('./test/05_mask.jpeg', mask)
    
    # Inverse the colors of the mask
    mask_inv = cv2.bitwise_not(mask)
    cv2.imwrite('./test/06_mask_inv.jpeg', mask_inv)
    
    # Get the black white
    bw = cv2.cvtColor(mask_inv, cv2.COLOR_GRAY2BGR)
    cv2.imwrite('./test/07_bw.jpeg', bw)
    
    # Get the white opaque
    alpha = mask_inv.copy()
    alpha[alpha > 0] = 255
    alpha = cv2.cvtColor(alpha, cv2.COLOR_GRAY2BGR)
    cv2.imwrite('./test/08_alpha.jpeg', alpha)
    
    # Add the opaque image to the original image
    img_with_mask = cv2.addWeighted(image, 1, alpha, 1, 0)
    cv2.imwrite('./test/09_img_with_mask.jpeg', img_with_mask)
    
    # Return the image with mask
    return img_with_mask