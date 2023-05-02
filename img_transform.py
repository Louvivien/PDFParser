
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
        
        cropped_image_path = "./test/13_temp_cropped_image.jpeg"
        with open("./test/01_temp_image.jpeg", "wb") as f:
            f.write(img_bytes.getvalue())
        
        # Check if there are multiple rectangles
        are_multiple_rectangles = crop_central_line("./test/01_temp_image.jpeg", cropped_image_path)

        if are_multiple_rectangles is None:
            print("Error: Failed to process the image.")
            continue

        multiple_rectangles.append(are_multiple_rectangles)

        # os.remove("temp_image.jpeg")

        with open(cropped_image_path, "rb") as f:
            cropped_img_bytes = f.read()
        # os.remove(cropped_image_path)

        images_as_bytes.append(cropped_img_bytes)

    return images_as_bytes, multiple_rectangles


# For the manual writing, we will crop it  
def crop_central_line(image_path, output_path):
    # Load the image using OpenCV
    img = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to create a mask
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours in the binary image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Calculate the row sums along the y-axis
    row_sums = np.sum(thresh, axis=1)

    # Find the spaces between rows by looking for runs of white
    row_spaces = np.where(row_sums > 0)[0]

    # Count the number of detected rows by counting the changes in row_spaces
    detected_rows = np.sum(np.diff(row_spaces) > 1) + 1

    
    img_with_rows = img.copy()
    line_y_coordinates = []

    for i in range(len(row_spaces) - 1):
        if row_spaces[i + 1] - row_spaces[i] > 1:
            line_y = row_spaces[i]
            line_y_coordinates.append(line_y)
            cv2.line(img_with_rows, (0, line_y), (img_with_rows.shape[1], line_y), (0, 255, 0), 2)
    
    last_line_y = row_spaces[-1]
    line_y_coordinates.append(last_line_y)
    cv2.line(img_with_rows, (0, last_line_y), (img_with_rows.shape[1], last_line_y), (0, 255, 0), 2)
    cv2.imwrite('./test/02_debug_image_with_rows.jpeg', img_with_rows)

    # Print the y-coordinates of the lines
    print("Y-coordinates of the lines:", line_y_coordinates)




    if detected_rows == 1:
        cropped_img = img.copy()
    elif detected_rows == 2:
        first_line_y = line_y_coordinates[0]
        print(f"y = {first_line_y}")
        # y = 58
        cropped_img = img[:first_line_y, :]
    elif detected_rows == 3:
        first_line_y = line_y_coordinates[0]
        second_line_y = line_y_coordinates[1]
        third_line_y = line_y_coordinates[2]
        cropped_img = img[second_line_y, third_line_y]
    else:
        print(f"Error: Unexpected number of detected rows ({detected_rows}).")
        return None

    if cropped_img is None or cropped_img.size == 0:
        print("Error: Cropped image is empty or not found.")
        return None

    cv2.imwrite('./test/03_cropped_img_debug.jpeg', cropped_img)

    img_with_mask = detect_border_touching_objects(cropped_img)

    # Convert the image to grayscale
    gray2 = cv2.cvtColor(img_with_mask, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to create a mask
    _, thresh2 = cv2.threshold(gray2, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours in the binary image
    contours2, _ = cv2.findContours(thresh2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Calculate the bounding boxes of the contours
    bounding_boxes = [cv2.boundingRect(cnt) for cnt in contours2]

    # Set the minimum width and height threshold for the bounding boxes
    min_width = 20
    min_height = 20

    # Filter the bounding boxes based on the threshold
    filtered_bboxes = [bbox for bbox in bounding_boxes if bbox[2] > min_width and bbox[3] > min_height]


    # Calculate the y-coordinate of the center of each bounding box
    centers_y = [y + h//2 for _, y, _, h in filtered_bboxes]

    if len(filtered_bboxes) == 1:
        cropped_img_with_mask = img_with_mask
    else:
        # Apply k-means clustering to group the elements based on their y-coordinate centers
        kmeans = KMeans(n_clusters=detected_rows, n_init=10, random_state=0).fit(np.array(centers_y).reshape(-1, 1))

        # Find the cluster labels and sort them based on the cluster centers
        sorted_labels = sorted(range(detected_rows), key=lambda i: kmeans.cluster_centers_[i])

        # Determine the median label
        if detected_rows == 1:
            median_label = sorted_labels[0]
        elif detected_rows == 2:
            median_label = sorted_labels[1]
        elif detected_rows == 3:
            median_label = sorted_labels[1]
        else:
            print("Error: Unexpected number of detected rows.")
            return None
        
        # Get the bounding boxes belonging to the target line
        central_line_bboxes = [bbox for bbox, label in zip(filtered_bboxes, kmeans.labels_) if label == median_label]


        # Save an image with bounding boxes drawn for debugging
        img_with_bboxes = img_with_mask.copy()
        for x, y, w, h in central_line_bboxes:
            cv2.rectangle(img_with_bboxes, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imwrite('./test/11_debug_image_with_bboxes.jpeg', img_with_bboxes)

        # Find the minimum and maximum x-coordinates and y-coordinates of the elements in the central line
        min_x = min([x for x, _, _, _ in central_line_bboxes])
        max_x = max([x + w for x, _, w, _ in central_line_bboxes])
        min_y = min([y for _, y, _, _ in central_line_bboxes])
        max_y = max([y + h for _, y, _, h in central_line_bboxes])

        # Extract the corresponding region with optional padding
        padding = 10
        min_y_padded = max(min_y - padding, 0)
        max_y_padded = min(max_y + padding, img_with_mask.shape[0])
        min_x_padded = max(min_x - padding, 0)
        max_x_padded = min(max_x + padding, img_with_mask.shape[1])

        # Extract the corresponding region with optional padding
        cropped_img_with_mask = img_with_mask[min_y_padded:max_y_padded, min_x_padded:max_x_padded]

        if cropped_img_with_mask is None or cropped_img_with_mask.size == 0:
            print("Error: Cropped image is empty or not found.")
            return None
        cv2.imwrite('./test/12_cropped_img_debug.jpeg', cropped_img_with_mask)

    # Save the cropped image
    cv2.imwrite(output_path, cropped_img_with_mask)

    # Check if there are multiple rectangles
    unique_rectangles = []
    for rect1 in bounding_boxes:
        is_inside = False
        if rect1[2] == 1 and rect1[3] == 1:
            continue  
        for rect2 in bounding_boxes:
            if (rect1 != rect2) and (rect1[0] > rect2[0]) and (rect1[1] > rect2[1]) and (rect1[0] + rect1[2] < rect2[0] + rect2[2]) and (rect1[1] + rect1[3] < rect2[1] + rect2[3]):
                is_inside = True
                break
        if not is_inside:
            unique_rectangles.append(rect1)

    # Return the number of central_line_bboxes
    return len(unique_rectangles) > 1

def detect_border_touching_objects(image):
    # Method 3: Use distance transform to find objects touching the border
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('./test/04_gray.jpeg', gray)
    
    # Thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite('./test/05_thresh.jpeg', thresh)
    
    # Find contours of objects
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create a mask covering objects touching the image boundaries
    mask = np.zeros_like(gray)
    for cnt in contours:
        _, _, w, h = cv2.boundingRect(cnt)
        if w == image.shape[1] or h == image.shape[0]:
            cv2.drawContours(mask, [cnt], -1, 255, cv2.FILLED)
    cv2.imwrite('./test/06_mask.jpeg', mask)
    
    # Inverse the colors of the mask
    mask_inv = cv2.bitwise_not(mask)
    cv2.imwrite('./test/07_mask_inv.jpeg', mask_inv)
    
    # Get the black white
    bw = cv2.cvtColor(mask_inv, cv2.COLOR_GRAY2BGR)
    cv2.imwrite('./test/08_bw.jpeg', bw)
    
    # Get the white opaque
    alpha = mask_inv.copy()
    alpha[alpha > 0] = 255
    alpha = cv2.cvtColor(alpha, cv2.COLOR_GRAY2BGR)
    cv2.imwrite('./test/09_alpha.jpeg', alpha)
    
    # Add the opaque image to the original image
    img_with_mask = cv2.addWeighted(image, 1, alpha, 1, 0)
    cv2.imwrite('./test/10_img_with_mask.jpeg', img_with_mask)
    
    # Return the image with mask
    return img_with_mask