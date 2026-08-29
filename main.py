import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

IMAGE_PAIRS = [
    ("left0.png", "right0.png"),
    ("left1.png", "right1.png"),
    ("left2.png", "right2.png")
]

OUTPUT_DIR = "output"


CALIBRATION = {

     #intrinsic camera matrix K that has fy fx cx cy
    0: {
        "K_left": np.array([
            [5299.313, 0, 1263.818],
            [0, 5299.313, 977.763],
            [0, 0, 1]
        ], dtype=np.float64),

        "K_right": np.array([
            [5299.313, 0, 1438.004],
            [0, 5299.313, 977.763],
            [0, 0, 1]
        ], dtype=np.float64),

        "doffs": 174.186,       #calibration offset 
        "baseline_mm": 177.288, #distance between the two cameras in millimeters
        "width": 2988,          #image width in pixels
        "height": 2008,
        "ndisp": 180,              #disparity search range as SGBM needs to know how far it should reach
        "vmin": 54,                #calibration metadata from the data set but not rlly used in the code
        "vmax": 147
    },


    1: {
        "K_left": np.array([
            [4396.869, 0, 1353.072],
            [0, 4396.869, 989.702],
            [0, 0, 1]
        ], dtype=np.float64),

        "K_right": np.array([
            [4396.869, 0, 1538.860],
            [0, 4396.869, 989.702],
            [0, 0, 1]
        ], dtype=np.float64),

        "doffs": 185.788,
        "baseline_mm": 144.049,
        "width": 2880,
        "height": 1980,
        "ndisp": 640,
        "vmin": 17,
        "vmax": 619
    },

    2: {
        "K_left": np.array([
            [5806.559, 0, 1429.219],
            [0, 5806.559, 993.403],
            [0, 0, 1]
        ], dtype=np.float64),

        "K_right": np.array([
            [5806.559, 0, 1543.510],
            [0, 5806.559, 993.403],
            [0, 0, 1]
        ], dtype=np.float64),

        "doffs": 114.291,
        "baseline_mm": 174.019,
        "width": 2960,
        "height": 2016,
        "ndisp": 250,
        "vmin": 38,
        "vmax": 222
    }
}



if os.path.exists(OUTPUT_DIR):

    if not os.path.isdir(OUTPUT_DIR):

        print(
            "ERROR: output exists as a FILE."
        )

        print(
            "Delete it and create an output folder."
        )

        exit()

else:

    os.makedirs(OUTPUT_DIR)  #creates the output folder if it doesn't exist


def normalize_image(image):  #disparity and depth array contain floating point values and we need to convert them to 8-bit grayscale for visualization as normal png expects that

    valid = image[np.isfinite(image)] #removes any NaN or infinite values from the image array

    if len(valid) == 0: #if no valid pixels are found, return a black image

        return np.zeros(
            image.shape,
            dtype=np.uint8
        )

    minimum = np.min(valid) #find the minimum and maximum values of the valid pixels to normalize the image to 0-255 range
    maximum = np.max(valid)

    if maximum - minimum < 1e-6: #IF the range is too small, return a black image to avoid division by zero

        return np.zeros(
            image.shape,
            dtype=np.uint8
        )

    normalized = (     #Normalize the image to 0-255 range using the formula: (image - min) / (max - min) * 255
        (image - minimum)
        /
        (maximum - minimum)
        * 255
    )

    return np.clip(
        normalized,  #Ensures that the values are clipped to the range [0, 255] and converted to uint8 type for proper visualization
        0,
        255
    ).astype(np.uint8) #CONVERTS THE FLOATING POINT VALUES TO 8-BIT UNSIGNED INTEGERS



def get_sift_matches(left, right): #GOAL: To find corresponding points and match SIFT features between the left and right images, returning the matched image, keypoints, and descriptors.

    gray_left = cv2.cvtColor(
        left,
        cv2.COLOR_BGR2GRAY   #converts the left image to grayscale for SIFT feature detection, as SIFT works on single-channel images  
    )                        #bec im interesed in intensity patterns and edges and corners rather than color information

    gray_right = cv2.cvtColor(
        right,
        cv2.COLOR_BGR2GRAY
    )

    sift = cv2.SIFT_create(
        nfeatures=3000         #detects up to 3000 distinctive keypoints in each image, which are points of interest that are invariant to scale and rotation   
    )                           #detects distinctive keypoints in the left and right images, and computes their corresponding descriptors, which are unique representations of the local image patches around each keypoint

    kp_left, des_left = (
        sift.detectAndCompute(
            gray_left,           #DETECTS AND COMPUTES SIFT KEYPOINTS AND DESCRIPTORS AND FEATURES FOR THE LEFT IMAGE
            None                 #returns a list of keypoints (kp_left) and a corresponding array of descriptors (des_left) that describe the local image patches around each keypoint
        )                        #keypoint WHERE , decriptor WHAT IT LOOKS LIKE
    )

    kp_right, des_right = (
        sift.detectAndCompute(
            gray_right,
            None
        )
    )

    print(
        "Left SIFT features:",
        len(kp_left)
    )

    print(
        "Right SIFT features:",
        len(kp_right)
    )

    matcher = cv2.BFMatcher()  #compares the descriptors of the left and right images to find potential matches between keypoints. It uses a brute-force approach to compute distances between descriptors and find the best matches.

    matches = matcher.knnMatch( #finds the k nearest neighbors for each descriptor in the left image from the right image
        des_left,
        des_right,
        k=2
    )

    good_matches = []

    for pair in matches:

        if len(pair) != 2:
            continue

        m, n = pair

        if m.distance < 0.75 * n.distance:

            good_matches.append(m)

    print(
        "Good matches:",
        len(good_matches)
    )

    # Draw matching lines

    match_image = cv2.drawMatches( #draws lines connecting the matched keypoints between the left and right images, creating a visual representation of the feature matching results. It returns an image that shows the two input images side by side with lines connecting the matched keypoints.
        left,
        kp_left,
        right,
        kp_right,
        good_matches,
        None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )

    pts_left = np.float32([
        kp_left[m.queryIdx].pt
        for m in good_matches #extracts the coordinates of the matched keypoints in the left image based on the good matches, creating an array of 2D points that correspond to the matched features in the left image
    ])

    pts_right = np.float32([
        kp_right[m.trainIdx].pt
        for m in good_matches
    ])

    return (
        match_image,
        pts_left,
        pts_right,
        good_matches
    )


# FUNDAMENTAL MATRIX
#it satisfies the epipolar constraint: x2^T * F * x1 = 0, where x1 and x2 are corresponding points in the left and right images, respectively. The fundamental matrix encodes the geometric relationship between the two camera views and is used to establish correspondences between points in stereo vision.
#we us ransac bec SIFT matches can contain outliers, and RANSAC helps to robustly estimate the fundamental matrix by iteratively selecting random subsets of matches and fitting a model while discarding outliers. This ensures that the estimated fundamental matrix is less affected by incorrect matches and provides a more accurate representation of the epipolar geometry between the two images.
def calculate_fundamental(
    pts_left,
    pts_right
):

    if len(pts_left) < 8:

        raise ValueError(
            "At least 8 matches are required."
        )

    F, mask = cv2.findFundamentalMat(
        pts_left,
        pts_right,
        cv2.FM_RANSAC,
        1.0, #error threshold for RANSAC, which determines how far a point can be from the epipolar line to be considered an inlier. A smaller value makes the estimation more strict, while a larger value allows for more tolerance to noise and outliers.
        0.99 #confidence level for RANSAC, which specifies the probability that the estimated fundamental matrix is correct. A higher value increases the number of iterations and improves the robustness of the estimation, but also increases computation time.
    )

    if F is None:

        raise ValueError(
            "Could not calculate Fundamental Matrix."
        )

    mask = mask.ravel().astype(bool) #returns 1 for inliers and 0 for outliers, allowing us to filter the matched points and keep only the inliers that are consistent with the estimated fundamental matrix.

    inlier_left = pts_left[mask]
    inlier_right = pts_right[mask]

    return (
        F,
        inlier_left,
        inlier_right
    )


# EPIPOLAR LINES
#you dont need to search for corresponding points in the entire image, but only along the epipolar lines, which reduces the search space and improves the efficiency of stereo matching algorithms. By drawing epipolar lines on the images, you can visualize the geometric relationship between corresponding points and verify the accuracy of feature matching and fundamental matrix estimation.


def create_epipolar_image(
    left,
    right,
    pts_left,
    pts_right,
    F
):

    left_img = left.copy()
    right_img = right.copy()

    number = min(
        20,
        len(pts_left)
    )

    left_points = pts_left[:number]
    right_points = pts_right[:number]

    # Epipolar lines in right image

    lines_right = cv2.computeCorrespondEpilines( #computes the epipolar lines in the right image corresponding to the points in the left image using the fundamental matrix F. The function takes the points from the left image, reshapes them to a suitable format, and returns the coefficients of the epipolar lines in the right image.
        left_points.reshape(-1, 1, 2),#-1 means let numpy figure out the appropriate size for that dimension based on the other dimensions and the total number of elements in the array. In this case, it reshapes the left_points array to have a shape of (N, 1, 2), where N is the number of points. The second dimension is set to 1 to indicate that each point is represented as a single row, and the third dimension is set to 2 to represent the x and y coordinates of each point.
        1,
        F
    )

    lines_right = lines_right.reshape(
        -1,
        3
    )

    # Epipolar lines in left image

    lines_left = cv2.computeCorrespondEpilines(
        right_points.reshape(-1, 1, 2),
        2,
        F
    )

    lines_left = lines_left.reshape(
        -1,
        3
    )

    h, w = left.shape[:2]

    # Left

    for line, point in zip(
        lines_left,
        left_points
    ):

        a, b, c = line

        if abs(b) < 1e-8:
            continue

        x0 = 0
        y0 = int(-c / b)

        x1 = w
        y1 = int(
            -(c + a * x1) / b
        )

        cv2.line( #draws the epipolar line on the left image using the calculated endpoints (x0, y0) and (x1, y1). The line is drawn in green color with a thickness of 2 pixels.
            left_img,
            (x0, y0),
            (x1, y1),
            (0, 255, 0),
            2
        )

        cv2.circle(
            left_img,
            tuple(np.int32(point)),
            6,
            (0, 0, 255),
            -1
        )

    # Right

    for line, point in zip(
        lines_right,
        right_points
    ):

        a, b, c = line

        if abs(b) < 1e-8:
            continue

        x0 = 0
        y0 = int(-c / b)

        x1 = w
        y1 = int(
            -(c + a * x1) / b
        )

        cv2.line(
            right_img,
            (x0, y0),
            (x1, y1),
            (0, 255, 0),
            2
        )

        cv2.circle(
            right_img,
            tuple(np.int32(point)),
            6,
            (0, 0, 255),
            -1
        )

    left_rgb = cv2.cvtColor(
        left_img,
        cv2.COLOR_BGR2RGB
    )

    right_rgb = cv2.cvtColor(
        right_img,
        cv2.COLOR_BGR2RGB
    )

    return np.hstack(
        (
            left_rgb,
            right_rgb
        )
    )


# ESSENTIAL MATRIX

def calculate_pose(
    F,
    K_left,
    K_right,
    pts_left,
    pts_right
):

    # Essential matrix 
    #Essential matrix is a 3x3 matrix that relates corresponding points in two calibrated camera views. It encodes the relative rotation and translation between the two cameras, allowing us to recover the 3D structure of the scene from stereo images. The essential matrix is derived from the fundamental matrix and the intrinsic camera parameters, and it is used in stereo vision to estimate the camera pose and reconstruct the 3D geometry of the scene.

    E = (
        K_right.T
        @ F
        @ K_left
    )
    

    # Normalize points

    left_norm = cv2.undistortPoints(
        pts_left.reshape(-1, 1, 2),
        K_left,
        None
    )

    right_norm = cv2.undistortPoints(
        pts_right.reshape(-1, 1, 2),
        K_right,
        None
    )

    # Recover rotation and translation

    _, R, t, _ = cv2.recoverPose(
        E,
        left_norm,
        right_norm
    )

    return E, R, t


# RECTIFICATION

#makes the images lie on the samehorizontal scaleline

def rectify_images(
    left,
    right,
    K_left,
    K_right,
    R,
    t
):

    h, w = left.shape[:2]

    distortion_left = np.zeros( # Initialize distortion coefficients for the left camera
        5,
        dtype=np.float64
    )

    distortion_right = np.zeros(
        5,
        dtype=np.float64
    )

    # Stereo rectification

    (
        R1,
        R2,
        P1,
        P2,
        Q,
        roi1,
        roi2
    ) = cv2.stereoRectify(
        K_left,
        distortion_left,
        K_right,
        distortion_right,
        (w, h),
        R,
        t,
        flags=cv2.CALIB_ZERO_DISPARITY,
        alpha=0 #minimal black regions in the rectified images
    )

    # Left map

    map1x, map1y = (
        cv2.initUndistortRectifyMap( #wherre should i sample the pixels from the original image to create the rectified image. It takes the camera matrix, distortion coefficients, rectification transformation, and projection matrix as inputs and returns two maps (map1x and map1y) that specify the pixel coordinates in the original image for each pixel in the rectified image.
            K_left,
            distortion_left,
            R1,
            P1,
            (w, h),
            cv2.CV_32FC1
        )
    )

    # Right map

    map2x, map2y = (
        cv2.initUndistortRectifyMap(
            K_right,
            distortion_right,
            R2,
            P2,
            (w, h),
            cv2.CV_32FC1
        )
    )

    rect_left = cv2.remap(
        left,
        map1x,
        map1y,
        cv2.INTER_LINEAR
    )

    rect_right = cv2.remap(
        right,
        map2x,
        map2y,
        cv2.INTER_LINEAR
    )

    # Homography matrices

    H1 = (
        P1[:, :3]
        @ np.linalg.inv(K_left)
    )

    H2 = (
        P2[:, :3]
        @ np.linalg.inv(K_right)
    )

    return (
        rect_left,
        rect_right,
        H1,
        H2,
        Q,
        P1,
        P2
    )


# DISPARITY


def calculate_disparity(
    left,
    right,
    ndisp
):
    #compares the rectified left and right images to compute the disparity map, which represents the pixel-wise differences between corresponding points in the two images. The disparity map is used to estimate depth information in stereo vision.

    gray_left = cv2.cvtColor(
        left,
        cv2.COLOR_BGR2GRAY
    )

    gray_right = cv2.cvtColor(
        right,
        cv2.COLOR_BGR2GRAY
    )

    # SGBM requires num disparities
    # to be divisible by 16

    num_disparities = (
        int(ndisp / 16) * 16
    )

    if num_disparities < 16:
        num_disparities = 16

    print(
        "Disparity range:",
        num_disparities
    )

    stereo = cv2.StereoSGBM_create( #finds corresponding points between the left and right images using the Semi-Global Block Matching (SGBM) algorithm. It takes the rectified grayscale images as input and computes the disparity map, which represents the pixel-wise differences between corresponding points in the two images. The disparity map is used to estimate depth information in stereo vision.

        minDisparity=0,

        numDisparities=num_disparities,

        blockSize=7,#instead of comparing individual pixels, SGBM compares small blocks of pixels (7x7 in this case) between the left and right images to find the best match. A larger block size can provide more robust matching but may reduce accuracy in areas with fine details.

        P1=8 * 1 * 7 * 7, #penalty for small disparity changes between neighboring pixels. It encourages smoothness in the disparity map by penalizing abrupt changes in disparity values. A higher value of P1 results in a smoother disparity map but may reduce accuracy in areas with fine details.

        P2=32 * 1 * 7 * 7, #penalty for larger disparity changes between neighboring pixels. It allows for more flexibility in the disparity map by permitting larger changes in disparity values. A higher value of P2 can improve accuracy in areas with fine details but may introduce noise in the disparity map.

        disp12MaxDiff=1,

        uniquenessRatio=10,

        speckleWindowSize=100,

        speckleRange=2,

        preFilterCap=63,

        mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
    )

    disparity = (
        stereo.compute(
            gray_left,
            gray_right
        ).astype(np.float32)
        / 16.0 #opencv returns disparity values multiplied by 16 to preserve sub-pixel accuracy. Dividing by 16.0 converts the disparity values back to their original scale, allowing for accurate depth estimation and visualization.
    )

    disparity[
        disparity <= 0
    ] = 0

    return disparity


# DEPTH


def calculate_depth(
    disparity,
    focal_length,
    baseline_mm,
    doffs
):

    depth_mm = np.zeros_like(
        disparity,
        dtype=np.float32
    )

    valid = disparity > 0

    # Stereo depth equation:
    #
    # Z = f * B / (d + doffs)

    denominator = (
        disparity[valid]
        + doffs
    )

    valid_denominator = (
        denominator > 0
    )

    valid_indices = np.where(
        valid
    )

    y = valid_indices[0][
        valid_denominator
    ]

    x = valid_indices[1][
        valid_denominator
    ]

    depth_mm[
        y,
        x
    ] = (
        focal_length
        * baseline_mm
        /
        denominator[
            valid_denominator
        ]
    )

    return depth_mm


# SAVE DISPARITY + DEPTH

def save_results(
    disparity,
    depth,
    pair_number
):

    
    # Disparity grayscale
  
    disparity_gray = normalize_image(
        disparity
    )

    cv2.imwrite(
        f"{OUTPUT_DIR}/"
        f"disparity_{pair_number}_gray.png",
        disparity_gray
    )

    
    # Disparity heatmap
   

    disparity_heatmap = (
        cv2.applyColorMap(
            disparity_gray,
            cv2.COLORMAP_JET
        )
    )

    cv2.imwrite(
        f"{OUTPUT_DIR}/"
        f"disparity_{pair_number}_heatmap.png",
        disparity_heatmap
    )

    
    # Depth grayscale
    

    depth_gray = normalize_image(
        depth
    )

    cv2.imwrite(
        f"{OUTPUT_DIR}/"
        f"depth_{pair_number}_gray.png",
        depth_gray
    )

  
    # Depth heatmap
   

    depth_heatmap = (
        cv2.applyColorMap(
            depth_gray,
            cv2.COLORMAP_JET
        )
    )

    cv2.imwrite(
        f"{OUTPUT_DIR}/"
        f"depth_{pair_number}_heatmap.png",
        depth_heatmap
    )

    return (
        cv2.cvtColor(
            disparity_heatmap,
            cv2.COLOR_BGR2RGB
        ),
        cv2.cvtColor(
            depth_heatmap,
            cv2.COLOR_BGR2RGB
        )
    )



# DASHBOARD


def show_dashboard(
    pair_number,
    match_image,
    epipolar_image,
    rect_left,
    rect_right,
    disparity_image,
    depth_image,
    good_matches,
    inliers
):

    fig, axes = plt.subplots(
        3,
        2,
        figsize=(18, 13)
    )

    fig.suptitle(
        f"ROV STEREO VISION — PAIR {pair_number}",
        fontsize=22,
        fontweight="bold"
    )

  
    # SIFT
    

    axes[0, 0].imshow(
        cv2.cvtColor(
            match_image,
            cv2.COLOR_BGR2RGB
        )
    )

    axes[0, 0].set_title(
        f"SIFT FEATURE MATCHING\n"
        f"{len(good_matches)} good matches"
    )

    axes[0, 0].axis("off")

    
    

    axes[0, 1].imshow(
        epipolar_image
    )

    axes[0, 1].set_title(
        "EPIPOLAR LINES + FEATURE POINTS"
    )

    axes[0, 1].axis("off")

  
    # RECTIFIED
    

    left_rgb = cv2.cvtColor(
        rect_left,
        cv2.COLOR_BGR2RGB
    )

    right_rgb = cv2.cvtColor(
        rect_right,
        cv2.COLOR_BGR2RGB
    )

    rectified = np.hstack(
        (
            left_rgb,
            right_rgb
        )
    )

    axes[1, 0].imshow(
        rectified
    )

    axes[1, 0].set_title(
        "RECTIFIED LEFT + RIGHT"
    )

    axes[1, 0].axis("off")

   
    # DISPARITY
   

    axes[1, 1].imshow(
        disparity_image
    )

    axes[1, 1].set_title(
        "DISPARITY HEATMAP"
    )

    axes[1, 1].axis("off")

    # DEPTH
   

    axes[2, 0].imshow(
        depth_image
    )

    axes[2, 0].set_title(
        "DEPTH HEATMAP"
    )

    axes[2, 0].axis("off")

   
    # INFORMATION
  

    axes[2, 1].axis("off")

    info = (
        "STEREO VISION PIPELINE\n\n"

        f"SIFT matches: {len(good_matches)}\n"
        f"RANSAC inliers: {len(inliers)}\n\n"

    )

    axes[2, 1].text(
        0.5,
        0.5,
        info,
        ha="center",
        va="center",
        fontsize=15
    )

    plt.tight_layout(
        rect=[
            0,
            0,
            1,
            0.95
        ]
    )

    plt.show()



# OBJECT MEASUREMENT


def measure_object(
    image,
    disparity,
    K,
    baseline_mm,
    doffs
):

    print("\n")
    print(
        "======================================"
    )

    print(
        "OBJECT LENGTH MEASUREMENT"
    )

    print(
        "======================================"
    )

    print(
        "Click TWO points on the object."
    )

    points = []

    display = image.copy()

    def mouse_callback(
        event,
        x,
        y,
        flags,
        param
    ):

        if event != cv2.EVENT_LBUTTONDOWN:
            return

        if len(points) >= 2:
            return

        points.append(
            (x, y)
        )

        cv2.circle(
            display,
            (x, y),
            8,
            (0, 0, 255),
            -1
        )

        cv2.imshow(
            "Object Measurement",
            display
        )

    cv2.namedWindow(
        "Object Measurement",
        cv2.WINDOW_NORMAL
    )

    cv2.resizeWindow(
        "Object Measurement",
        1280,
        800
    )

    cv2.setMouseCallback(
        "Object Measurement",
        mouse_callback
    )

    cv2.imshow(
        "Object Measurement",
        display
    )

    cv2.waitKey(0)

    cv2.destroyAllWindows()

    if len(points) != 2:

        print(
            "Two points were not selected."
        )

        return

    fx = K[0, 0]
    fy = K[1, 1]

    cx = K[0, 2]
    cy = K[1, 2]

    points_3d = []

    for u, v in points:

        radius = 3

        y1 = max(
            0,
            v - radius
        )

        y2 = min(
            disparity.shape[0],
            v + radius + 1
        )

        x1 = max(
            0,
            u - radius
        )

        x2 = min(
            disparity.shape[1],
            u + radius + 1
        )

        local_disparity = (
            disparity[
                y1:y2,
                x1:x2
            ]
        )

        valid = (
            local_disparity[
                local_disparity > 0
            ]
        )

        if len(valid) == 0:

            print(
                f"No valid disparity at "
                f"({u},{v})"
            )

            return

        d = np.median(
            valid
        )

        # Depth in millimeters

        Z = (
            fx
            * baseline_mm
            /
            (d + doffs)
        )

        X = (
            (u - cx)
            * Z
            / fx
        )

        Y = (
            (v - cy)
            * Z
            / fy
        )

        point = np.array([
            X,
            Y,
            Z
        ])

        points_3d.append(
            point
        )

        print(
            f"\nPixel: ({u}, {v})"
        )

        print(
            f"Disparity: {d:.3f}"
        )

        print(
            "3D point:"
        )

        print(
            f"X = {X:.2f} mm"
        )

        print(
            f"Y = {Y:.2f} mm"
        )

        print(
            f"Z = {Z:.2f} mm"
        )

    # Euclidean distance

    length_mm = np.linalg.norm(
        points_3d[0]
        -
        points_3d[1]
    )

    print("\n")
    print(
        "======================================"
    )

    print(
        "OBJECT LENGTH RESULT"
    )

    print(
        "======================================"
    )

    print(
        f"Length = {length_mm:.2f} mm"
    )

    print(
        f"Length = "
        f"{length_mm / 10:.2f} cm"
    )

    print(
        f"Length = "
        f"{length_mm / 1000:.4f} m"
    )



# MAIN


def main():

    print("\n")
    print(
        "================================================"
    )

    print(
        "          ROV STEREO VISION SYSTEM"
    )

    print(
        "================================================"
    )

    for pair_number, (
        left_path,
        right_path
    ) in enumerate(IMAGE_PAIRS):

        print("\n")
        print(
            "================================================"
        )

        print(
            f"PROCESSING IMAGE PAIR {pair_number}"
        )

        print(
            "================================================"
        )

       
        # Calibration

        calibration = (
            CALIBRATION[pair_number]
        )

        K_left = (
            calibration["K_left"]
        )

        K_right = (
            calibration["K_right"]
        )

        doffs = (
            calibration["doffs"]
        )

        baseline_mm = (
            calibration["baseline_mm"]
        )

        ndisp = (
            calibration["ndisp"]
        )

      
        # Load images
        

        left = cv2.imread(
            left_path
        )

        right = cv2.imread(
            right_path
        )

        if left is None:

            print(
                f"ERROR: Cannot load {left_path}"
            )

            continue

        if right is None:

            print(
                f"ERROR: Cannot load {right_path}"
            )

            continue

        print(
            "Images loaded successfully."
        )

       
        # Print calibration
        

        print(
            "\nLEFT CAMERA MATRIX:"
        )

        print(K_left)

        print(
            "\nRIGHT CAMERA MATRIX:"
        )

        print(K_right)

        print(
            f"\nBaseline = "
            f"{baseline_mm} mm"
        )

        print(
            f"Disparity offset = "
            f"{doffs}"
        )

        print(
            f"Maximum disparity = "
            f"{ndisp}"
        )

        
        # STEP 1 — SIFT
        

        print(
            "\n FEATURE MATCHING"
        )

        (
            match_image,
            pts_left,
            pts_right,
            good_matches
        ) = get_sift_matches(
            left,
            right
        )

        if len(good_matches) < 8:

            print(
                "Not enough matches."
            )

            continue

        
        # STEP 2 — FUNDAMENTAL
       

        print(
            "\n FUNDAMENTAL MATRIX"
        )

        (
            F,
            inlier_left,
            inlier_right
        ) = calculate_fundamental(
            pts_left,
            pts_right
        )

        print(
            "\nFundamental Matrix F:"
        )

        print(F)

        print(
            "\nRANSAC inliers:",
            len(inlier_left)
        )

        
        # STEP 3 — EPIPOLAR LINES
      
        print(
            "\n EPIPOLAR LINES"
        )

        epipolar_image = (
            create_epipolar_image(
                left,
                right,
                inlier_left,
                inlier_right,
                F
            )
        )

        cv2.imwrite(
            f"{OUTPUT_DIR}/"
            f"epipolar_{pair_number}.png",
            cv2.cvtColor(
                epipolar_image,
                cv2.COLOR_RGB2BGR
            )
        )

        # STEP 4 — ESSENTIAL
     
        print(
            "\n ESSENTIAL MATRIX"
        )

        (
            E,
            R,
            t
        ) = calculate_pose(
            F,
            K_left,
            K_right,
            inlier_left,
            inlier_right
        )
        t = t / np.linalg.norm(t) * baseline_mm

        print(
            "\nEssential Matrix E:"
        )

        print(E)

        print(
            "\nRotation Matrix R:"
        )

        print(R)

        print(
            "\nTranslation Vector t:"
        )

        print(t)

        # STEP 5 — RECTIFICATION
        

        print(
            "\n RECTIFICATION"
        )

        (
            rect_left,
            rect_right,
            H1,
            H2,
            Q,
            P1,
            P2
        ) = rectify_images(
            left,
            right,
            K_left,
            K_right,
            R,
            t
        )

        print(
            "\nHomography H1:"
        )

        print(H1)

        print(
            "\nHomography H2:"
        )

        print(H2)

        cv2.imwrite(
            f"{OUTPUT_DIR}/"
            f"rectified_left_{pair_number}.png",
            rect_left
        )

        cv2.imwrite(
            f"{OUTPUT_DIR}/"
            f"rectified_right_{pair_number}.png",
            rect_right
        )

    
        # STEP 6 — DISPARITY
       

        print(
            "\n CORRESPONDENCE / DISPARITY"
        )

        disparity = (
            calculate_disparity(
                rect_left,
                rect_right,
                ndisp
            )
        )

        print("Valid disparity pixels:",np.sum(disparity > 0),"OUT OF",disparity.size)
        print("Disparity min/max:",disparity.min(), disparity.max())

 
        # STEP 7 — DEPTH
      

        print(
            "\n DEPTH IMAGE"
        )

        focal_length = P1[0, 0]
        rectified_baseline = -P2[0, 3]  / P2[0, 0]
        rectified_doffs = P2[0, 2] - P1[0, 2]

        depth = (
            calculate_depth(
                disparity,
                focal_length,
                rectified_baseline,
                rectified_doffs
            )
        )

        
        # SAVE
        

        (
            disparity_image,
            depth_image
        ) = save_results(
            disparity,
            depth,
            pair_number
        )

        print(
            "\nAll images saved."
        )

       
        # DASHBOARD
       

        show_dashboard(
            pair_number,
            match_image,
            epipolar_image,
            rect_left,
            rect_right,
            disparity_image,
            depth_image,
            good_matches,
            inlier_left
        )

        # OBJECT MEASUREMENT
        

        K_rect = P1[:, :3]

        measure_object(
                rect_left,
                disparity,
                K_rect,
                rectified_baseline,
                rectified_doffs
            )

    print("\n")
    print(
        "================================================"
    )

    print(
        "          STEREO VISION COMPLETE!"
    )

    print(
        "================================================"
    )

    print(
        "Check the output folder."
    )


if __name__ == "__main__":

    main()