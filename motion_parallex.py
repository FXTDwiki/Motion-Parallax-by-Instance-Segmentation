import cv2
import imageio.v2 as imageio
import numpy as np
from scipy.spatial.distance import cdist
from PIL import Image

import feature_matcher


def raw_motion_parallex(img1_path, img2_path):
    img1 = imageio.imread(img1_path)
    img2 = imageio.imread(img2_path)
    return [img1, img2]


def saliency_sift_motion_parallex(img1_path, img2_path, model='homography', thres=100, fix_saliency_thres=256):
    img1 = imageio.imread(img1_path)
    img2 = imageio.imread(img2_path)
    saliency1 = imageio.imread(img1_path[:-4] + '_saliency.png')
    saliency2 = imageio.imread(img2_path[:-4] + '_saliency.png')

    # Detect features
    method = feature_matcher.CreateMethod.sift_bf_crosscheck()
    kp1, des1, kp2, des2, matches = method(img1, img2)

    # Filter by saliency
    p1 = [[int(kp1[m.queryIdx].pt[0]), int(kp1[m.queryIdx].pt[1])] for m in matches]
    p2 = [[int(kp2[m.trainIdx].pt[0]), int(kp2[m.trainIdx].pt[1])] for m in matches]
    matches = [
        matches[i] for i in range(len(matches))
        if saliency1[p1[i][1], p1[i][0]] > thres and saliency2[p2[i][1], p2[i][0]] > thres
    ]

    # Drawing matched result
    match_img = cv2.drawMatches(
        img1, kp1, img2, kp2, matches,
        None, flags=2)
    imageio.imsave('_tmp.jpg', match_img)

    # Model image plane movement
    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    if model == 'homography':
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC)
    elif model == 'translation':
        src_m = np.median(src_pts, 0)[0]
        dst_m = np.median(dst_pts, 0)[0]
        M = np.eye(3).astype(np.float32)
        M[0, 2] = dst_m[0] - src_m[0]
        M[1, 2] = dst_m[1] - src_m[1]
    elif model == 'affine':
        M, _ = cv2.estimateAffinePartial2D(src_pts, dst_pts)
        if M is not None:
            M = np.vstack([M, [0, 0, 1]])
        else:
            print("Failed to estimate affine transformation. Using identity matrix.")
            M = np.eye(3)
    else:
        raise Exception()

    # Warp according to homography
    height, width = img1.shape[:2]
    img1_warp = cv2.warpPerspective(img1, M, (width, height))

    # Only move non saliency part
    mask = saliency2 > fix_saliency_thres
    img1_warp[mask] = img2[mask]

    # Finding maximum bbox
    bbox = np.array([
        [0, 0, 1], [img1.shape[1], 0, 1],
        [img1.shape[1], img1.shape[0], 1], [0, img1.shape[0], 1]
    ], np.float32)
    bbox = M.dot(bbox.T).T
    bbox = bbox[:, :2] / bbox[:, [2]]
    xmin = int(max(0, bbox[0, 0], bbox[3, 0]))
    xmax = int(min(img1.shape[1], img2.shape[1], bbox[1, 0], bbox[2, 0]))
    ymin = int(max(0, bbox[0, 1], bbox[1, 1]))
    ymax = int(min(img1.shape[0], img2.shape[0], bbox[2, 1], bbox[3, 1]))

    img1_warp = img1_warp[ymin:ymax, xmin:xmax]
    img2 = img2[ymin:ymax, xmin:xmax]

    return [img1_warp, img2], match_img


if __name__ == '__main__':

    import tkinter as tk
    from tkinter import filedialog, messagebox
    import os
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--fix_saliency_thres', default=256, type=float)
    parser.add_argument('--mode', choices=['raw', 'saliency_sift'], default='saliency_sift')
    parser.add_argument('--model', choices=['homography', 'translation', 'affine'], default='homography')
    args = parser.parse_args()

    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Select input images
    while True:
        image_paths = filedialog.askopenfilenames(
            title="Select two images",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg")],
            multiple=True
        )
        
        if len(image_paths) == 2:
            break
        else:
            retry = messagebox.askretrycancel(
                "Invalid Selection",
                "Please select exactly two images.\nDo you want to try again?"
            )
            if not retry:
                print("Selection cancelled. Exiting.")
                exit()

    img1_path, img2_path = image_paths

    # Select output directory
    out_dir = filedialog.askdirectory(title="Select output directory")
    
    if not out_dir:
        print("Output directory must be selected. Exiting.")
        exit()

    # Generate motion parallax
    if args.mode == 'raw':
        images = raw_motion_parallex(img1_path, img2_path)
    elif args.mode == 'saliency_sift':
        images, match_img = saliency_sift_motion_parallex(
            img1_path, img2_path, args.model, fix_saliency_thres=args.fix_saliency_thres)
    else:
        raise NotImplementedError()

    # Save result as gif
    out_gif = os.path.join(out_dir, "motion_parallax.gif")
    imageio.mimsave(out_gif, images, 'GIF')
    print(f"Motion parallax GIF saved to: {out_gif}")

    # Save match image if available
    if 'match_img' in locals():
        out_match = os.path.join(out_dir, "match_image.jpg")
        imageio.imsave(out_match, match_img)
        print(f"Match image saved to: {out_match}")

    print("Processing complete.")
    messagebox.showinfo("Processing Complete", "Motion parallax processing is complete.")