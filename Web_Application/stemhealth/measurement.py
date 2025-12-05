import cv2
import numpy as np

# Methods to get the sponge mask and reference object mask
def get_sponge_mask(image_path):
    image = cv2.imread(image_path)
    
    # Convert the image from BGR to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define the range for the green color in HSV
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    
    # Create a mask for the green color
    mask = cv2.inRange(hsv_image, lower_green, upper_green)
    
    # Apply morphological opening to remove small noises
    kernel = np.ones((2, 2), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find the largest contour by area
    largest_contour = max(contours, key=cv2.contourArea)
        
    # Calculate the convex hull of the largest contour
    hull = cv2.convexHull(largest_contour)
    
    # Simplify the convex hull to 4 points
    # If there are more than 4 points, approximate to 4 points
    if len(hull) > 4:
        epsilon = 0.01 * cv2.arcLength(hull, True)  # Approximation accuracy
        approx = cv2.approxPolyDP(hull, epsilon, True)
        
        if len(approx) > 4:
            # Use only the first 4 points
            approx = approx[:4]
    
    # Create a new blank mask
    simplified_mask = np.zeros_like(mask)
    
    # Draw the 4-point polygon on the new mask
    pts = approx.reshape((-1, 1, 2))
    cv2.fillPoly(simplified_mask, [pts], 255)

    return mask, simplified_mask, approx

# Function to get the reference object mask
def get_reference_object_mask(image_path):
    image = cv2.imread(image_path)
    
    # Convert the image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # # Redefine the red color range in HSV to include both possible ranges for red hues
    lower_red_1 = np.array([0, 100, 100])
    upper_red_1 = np.array([10, 255, 255])
    
    # Create masks for the red color ranges
    reference_mask = cv2.inRange(hsv, lower_red_1, upper_red_1)
    # Apply morphological opening to remove small noises
    kernel = np.ones((3, 3), np.uint8)
    reference_mask = cv2.morphologyEx(reference_mask, cv2.MORPH_CLOSE, kernel)
    trimmed_mask = reference_mask.copy()
    trimmed_mask[:, :420] = trimmed_mask[:, 565:] = 0
    
    contours, _ = cv2.findContours(trimmed_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Assuming the largest contour is the reference object
    contour = max(contours, key=cv2.contourArea)
    
    # Calculate the convex hull of the largest contour
    hull = cv2.convexHull(contour)
    
    # Simplify the convex hull to 4 points
    # If there are more than 4 points, approximate to 4 points
    if len(hull) > 4:
        epsilon = 0.01 * cv2.arcLength(hull, True)  # Approximation accuracy
        approx = cv2.approxPolyDP(hull, epsilon, True)
        
        if len(approx) > 4:
            # Use only the first 4 points
            approx = approx[:4]
    
    # Draw the convex hull
    for i in range(len(approx)):
        cv2.line(image, tuple(approx[i][0]), tuple(approx[(i + 1) % len(approx)][0]), (0, 255, 0), 1)
    
    # Create a new blank mask
    simplified_reference_mask = np.zeros_like(reference_mask)
    simplified_reference_mask_points = approx.reshape((-1, 1, 2))
    cv2.fillPoly(simplified_reference_mask, [simplified_reference_mask_points.astype(np.int32)], 255, lineType=cv2.LINE_AA)
    
    return reference_mask, simplified_reference_mask, approx

# Find the most right point of the mask
def extend_line_to_right_boundary(mask, coord):
    y = coord[1]
    x = coord[0]

    # Initialize the end points
    right_end = None
    
    # Variables to track the current and previous states of the mask value
    previous_value = 0  # Start outside the object
    inside_boundary = False

    # Scan to the right to find the right boundary
    for i in range(x, mask.shape[1]):
        current_value = mask[y, i]

        if current_value > 0:
            if not inside_boundary:
                # Entered the object from background
                inside_boundary = True
                previous_value = current_value
        elif inside_boundary:
            # Exited the object to background
            right_end = (i, y)
            break
    
    return right_end

# Find the area where the seedling will be considered for measurement
def find_eligible_seedling_position(simplified_reference_mask, simplified_sponge_mask, simplified_reference_mask_points, simplified_sponge_mask_points):
    simplified_reference_mask_points = [tuple(point[0]) for point in simplified_reference_mask_points]  # Convert approx to a list of (x, y) tuples
    # Bottom points have the highest y value
    reference_bottom_points = sorted(simplified_reference_mask_points, key=lambda p: p[1], reverse=True)[:2]
    # Among the bottom points, select the leftmost and rightmost
    reference_bottom_left = min(reference_bottom_points, key=lambda p: p[0])
    reference_bottom_right = max(reference_bottom_points, key=lambda p: p[0])

    # Find the corresponding points in the sponge mask
    sponge_top_right = extend_line_to_right_boundary(simplified_sponge_mask, reference_bottom_right)
    sponge_bottom_right = extend_line_to_right_boundary(simplified_sponge_mask, reference_bottom_left)

    # Create a mask for the eligible area
    eligible_area_mask = np.zeros_like(simplified_reference_mask)
    points = np.array([reference_bottom_left, reference_bottom_right, sponge_top_right, sponge_bottom_right])
    cv2.fillPoly(eligible_area_mask, [points], 255)
    return eligible_area_mask

# Function to check if a coordinate is within the eligibile seedling position mask
def is_within_mask(mask, coord):
    # Convert the mask to grayscale if it is in BGR
    if len(mask.shape) == 3:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    x, y = coord
    # Check if the coordinate is within the mask
    if x >= 0 and x < mask.shape[1] and y >= 0 and y < mask.shape[0]:
        return mask[y, x] > 0
    return False


# Measurement methods
# Function to extend the line from a point to the boundary of the mask
def extend_line_to_boundary(mask, coord):
    y = coord[1]
    x = coord[0]

    # Initialize the end points
    left_end = None

    # Extend line to the left
    for i in range(x, -1, -1):
        if mask[y, i] > 0:  # Boundary found
            left_end = (i, y)
            break

    return left_end

# Function to find the top edge of the mask at the same x-coordinate
def find_top_edge(mask, x):
    for y in range(mask.shape[0]):
        if mask[y, x] > 0:
            return (x, y)
    return None

# Function to calculate the real-world seedling height
def calculate_seedling_height(left_end, top_edge_point, height):
    # Calculate the scale factor (5 is the actual height of the reference object)
    scale = 5 / (left_end[1] - top_edge_point[1])
    measurement = "{:.2f}".format(height * scale)
    return float(measurement)

# Process the image to calculate the seedling height.
def process_image(reference_mask, x1, y1, x2, y2):
    height = y2 - y1
    coordinate = (x2, y2)
    left_end = extend_line_to_boundary(reference_mask, coordinate)
    top_edge_point = find_top_edge(reference_mask, left_end[0])
    measurement = calculate_seedling_height(left_end, top_edge_point, height)
    return measurement
