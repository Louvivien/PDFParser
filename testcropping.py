import cv2
import numpy as np
from sklearn.cluster import KMeans

def crop_central_line(image_path, output_path, padding=0, debug=True):
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
    if debug:
        img_with_bboxes = img.copy()
        for x, y, w, h in central_line_bboxes:
            cv2.rectangle(img_with_bboxes, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imwrite('./test/debug_image_with_bboxes.jpeg', img_with_bboxes)

    # Find the minimum and maximum x-coordinates and y-coordinates of the elements in the central line
    min_x = min([x for x, _, _, _ in central_line_bboxes])
    max_x = max([x + w for x, _, w, _ in central_line_bboxes])
    min_y = min([y for _, y, _, _ in central_line_bboxes])
    max_y = max([y + h for _, y, _, h in central_line_bboxes])

    # Extract the corresponding region with optional padding
    cropped_img = img[min_y - padding:max_y + padding, min_x - padding:max_x + padding]

    # Save the cropped image
    cv2.imwrite(output_path, cropped_img)

# Set the input and output paths
image_path = './test/temp_image.jpeg'
output_path = './test/output.jpeg'

# Set optional padding (in pixels)
padding = 10

# Set debug flag
debug = True

# Crop the entire central line of the image
crop_central_line(image_path, output_path, padding, debug)
