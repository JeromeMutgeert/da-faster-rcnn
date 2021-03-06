#!/usr/bin/env python

# --------------------------------------------------------
# Faster R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""

import _init_paths
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from utils.timer import Timer
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import caffe, os, sys, cv2
import argparse

from roi_data_da_layer.live_dataset import target_file_streamer

CLASSES = ('__background__',
    'person',
    'bicycle',
    'car',
    'motorcycle',
    'airplane',
    'bus',
    'train',
    'truck',
    'boat',
    'traffic light',
    'fire hydrant',
    'stop sign',
    'parking meter',
    'bench',
    'bird',
    'cat',
    'dog',
    'horse',
    'sheep',
    'cow',
    'elephant',
    'bear',
    'zebra',
    'giraffe',
    'backpack',
    'umbrella',
    'handbag',
    'tie',
    'suitcase',
    'frisbee',
    'skis',
    'snowboard',
    'sports ball',
    'kite',
    'baseball bat',
    'baseball glove',
    'skateboard',
    'surfboard',
    'tennis racket',
    'bottle',
    'wine glass',
    'cup',
    'fork',
    'knife',
    'spoon',
    'bowl',
    'banana',
    'apple',
    'sandwich',
    'orange',
    'broccoli',
    'carrot',
    'hot dog',
    'pizza',
    'donut',
    'cake',
    'chair',
    'couch',
    'potted plant',
    'bed',
    'dining table',
    'toilet',
    'tv',
    'laptop',
    'mouse',
    'remote',
    'keyboard',
    'cell phone',
    'microwave',
    'oven',
    'toaster',
    'sink',
    'refrigerator',
    'book',
    'clock',
    'vase',
    'scissors',
    'teddy bear',
    'hair drier',
    'toothbrush')

NETS = {'vgg16': ('VGG16',
                  'coco_vgg16_faster_rcnn_final.caffemodel')}


def vis_detections(im, class_name, dets, inds,thres=0.5):
    """Draw detected bounding boxes."""

    im = im[:, :, (2, 1, 0)]
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(im, aspect='equal')
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]

        ax.add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
                          bbox[2] - bbox[0],
                          bbox[3] - bbox[1], fill=False,
                          edgecolor='red', linewidth=3.5)
            )
        ax.text(bbox[0], bbox[1] - 2,
                '{:s} {:.3f}'.format(class_name, score),
                bbox=dict(facecolor='blue', alpha=0.5),
                fontsize=14, color='white')

    ax.set_title(('{} detections with '
                  'p({} | box) >= {:.1f}').format(class_name, class_name,
                                                  thresh),
                  fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.draw()

def demo(net, image_name):
    """Detect object classes in an image using pre-computed object proposals."""

    # Load the demo image
    # im_file = os.path.join(cfg.DATA_DIR, 'demo', image_name)
    im = cv2.imread(im_name)

    # Detect all object classes and regress object bounds
    # timer = Timer()
    # timer.tic()
    scores, boxes = im_detect(net, im)
    
    scores = np.array(scores)
    boxes = np.array(boxes)
    
    # scores:: N x   81
    # boxes :: N x 324 (= 4*81)
    
    N,_ = boxes.shape
    boxes = boxes.reshape(N,4,81)
    
    # Pseudo-labelling: Only keep the most confident prediction for each bounding box:
    classes = scores.argmax(1)
    scores = scores[np.arange(N),classes]
    boxes = boxes[np.arange(N),:,classes]
    
    
    # scores:: N
    # boxes :: N x 4
    
    # remove detections with background labels:
    boxes = boxes[classes != 0,:]
    scores = scores[classes != 0]
    classes = classes[classes != 0]
    
    # scores:: M
    # boxes :: M x 4
    # where M <= N
    print(scores.shape,boxes.shape)
    
    detections = {}
    
    
    for cls_ind, cls in enumerate(CLASSES[1:]):
        sel = classes == cls_ind
        if sel.any():
            detections[cls] = list((s,list(boxes)) for s,boxes in zip(scores[sel],boxes[sel,:]))
    
    
    with open("coco_detections.txt",'a') as f:
        f.write(str(detections) + "\n")
        f.flush()
    
    # timer.toc()
    # print ('Detection took {:.3f}s for '
    #        '{:d} object proposals').format(timer.total_time, boxes.shape[0])

    # Visualize detections for each class
    # CONF_THRESH = 0.8
    # NMS_THRESH = 0.3
    # for cls_ind, cls in enumerate(CLASSES[1:]):
    #     cls_ind += 1 # because we skipped background
    #     cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
    #     cls_scores = scores[:, cls_ind]
    #     dets = np.hstack((cls_boxes,
    #                       cls_scores[:, np.newaxis])).astype(np.float32)
    #     keep = nms(dets, NMS_THRESH)
    #     dets = dets[keep, :]
    #     inds = np.where(dets[:, -1] >= CONF_THRESH)[0]
    #     if len(inds) > 0:
    #         # vis_detections(im, cls, dets, CONF_THRESH)
    #         # detects[cls_ind] = [cls_boxes]
    #         pass

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Faster R-CNN demo')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--cpu', dest='cpu_mode',
                        help='Use CPU mode (overrides --gpu)',
                        action='store_true')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]',
                        choices=NETS.keys(), default='vgg16')

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    cfg.TEST.HAS_RPN = True  # Use RPN for proposals

    args = parse_args()

    prototxt = os.path.join('.','models','coco', NETS[args.demo_net][0],
                            'faster_rcnn_end2end', 'test.prototxt')
    caffemodel = os.path.join(cfg.DATA_DIR, 'faster_rcnn_models',
                              NETS[args.demo_net][1])

    if not os.path.isfile(caffemodel):
        raise IOError(('{:s} not found.\nDid you run ./data/script/'
                       'fetch_faster_rcnn_models.sh?').format(caffemodel))

    if args.cpu_mode:
        caffe.set_mode_cpu()
    else:
        caffe.set_mode_gpu()
        caffe.set_device(args.gpu_id)
        cfg.GPU_ID = args.gpu_id
    net = caffe.Net(prototxt, caffemodel, caffe.TEST)

    print '\n\nLoaded network {:s}'.format(caffemodel)

    # Warmup on a dummy image
    im = 128 * np.ones((300, 500, 3), dtype=np.uint8)
    for i in xrange(2):
        _, _= im_detect(net, im)

    # im_names = ['000456.jpg', '000542.jpg', '001150.jpg',
    #             '001763.jpg', '004545.jpg']
    i = 0
    os.remove("coco_detections.txt")
    for im_name in target_file_streamer():
        # print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        # print 'Demo for data/demo/{}'.format(im_name)
        print(i)
        demo(net, im_name)
        i += 1
        if i == 20000:
            break

    plt.show()
