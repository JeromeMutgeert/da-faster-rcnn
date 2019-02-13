# --------------------------------------------------------
# Fast R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick
# --------------------------------------------------------

"""The data layer used during training to train a DA Fast R-CNN network.

RoIDataLayer implements a Caffe Python layer.
"""

import caffe
from fast_rcnn.config import cfg
from roi_data_da_layer.minibatch import get_minibatch
import numpy as np
import yaml
from multiprocessing import Process, Queue
import time
import os


class RoIDataDALayer(caffe.Layer):
    """Fast R-CNN data layer used for training."""

    def _shuffle_roidb_inds(self):
        """Randomly permute the training roidb."""
        if cfg.TRAIN.ASPECT_GROUPING:
            widths = np.array([r['width'] for r in self._roidb])
            heights = np.array([r['height'] for r in self._roidb])
            horz = (widths >= heights)
            vert = np.logical_not(horz)
            horz_inds = np.where(horz)[0]
            vert_inds = np.where(vert)[0]
            inds = np.hstack((
                np.random.permutation(horz_inds),
                np.random.permutation(vert_inds)))
            inds = np.reshape(inds, (-1, 2))
            row_perm = np.random.permutation(np.arange(inds.shape[0]))
            inds = np.reshape(inds[row_perm, :], (-1,))
            self._perm = inds
        else:
            self._perm = np.random.permutation(np.arange(len(self._roidb)))
        self._cur = 0

    def _get_next_minibatch_inds(self):
        """Return the roidb indices for the next minibatch."""
        if self._cur + cfg.TRAIN.IMS_PER_BATCH >= len(self._roidb):
            self._shuffle_roidb_inds()

        db_inds = self._perm[self._cur:self._cur + cfg.TRAIN.IMS_PER_BATCH]
        self._cur += cfg.TRAIN.IMS_PER_BATCH
        return db_inds

    def _get_next_minibatch(self):
        """Return the blobs to be used for the next minibatch.

        If cfg.TRAIN.USE_PREFETCH is True, then blobs will be computed in a
        separate process and made available through self._blob_queue.
        """
        if cfg.TRAIN.USE_PREFETCH or cfg.FETCH_TARGETS:
            print self._blob_queue.qsize()
            return self._blob_queue.get()
        else:
            db_inds = self._get_next_minibatch_inds()
            minibatch_db = [self._roidb[i] for i in db_inds]
            return get_minibatch(minibatch_db, self._num_classes)

    def set_roidb(self, roidb):
        """Set the roidb to be used by this layer during training."""
        self._roidb = roidb
        self._shuffle_roidb_inds()
        if cfg.TRAIN.USE_PREFETCH or cfg.FETCH_TARGETS:
            self._blob_queue = Queue(10)
            self._prefetch_process = BlobFetcher(self._blob_queue,
                                                 self._roidb,
                                                 self._num_classes)
            self._prefetch_process.start()
            # Terminate the child process when the parent exists
            def cleanup():
                print 'Terminating BlobFetcher'
                self._prefetch_process.terminate()
                self._prefetch_process.join()
            import atexit
            atexit.register(cleanup)

    def setup(self, bottom, top):
        """Setup the RoIDataLayer."""

        # parse the layer parameter string, which must be valid YAML
        layer_params = yaml.load(self.param_str_)

        self._num_classes = layer_params['num_classes']

        self._name_to_top_map = {}

        # data blob: holds a batch of N images, each with 3 channels
        idx = 0
        top[idx].reshape(cfg.TRAIN.IMS_PER_BATCH, 3,
            max(cfg.TRAIN.SCALES), cfg.TRAIN.MAX_SIZE)
        self._name_to_top_map['data'] = idx
        idx += 1

        if cfg.TRAIN.HAS_RPN:
            top[idx].reshape(1, 3)
            self._name_to_top_map['im_info'] = idx
            idx += 1

            top[idx].reshape(1, 4)
            self._name_to_top_map['gt_boxes'] = idx
            idx += 1

            top[idx].reshape(1, 1)
            self._name_to_top_map['need_backprop'] = idx
            idx += 1

            top[idx].reshape(1, 1)
            self._name_to_top_map['dc_label'] = idx
            idx += 1

        else: # not using RPN
            # rois blob: holds R regions of interest, each is a 5-tuple
            # (n, x1, y1, x2, y2) specifying an image batch index n and a
            # rectangle (x1, y1, x2, y2)
            top[idx].reshape(1, 5)
            self._name_to_top_map['rois'] = idx
            idx += 1

            # labels blob: R categorical labels in [0, ..., K] for K foreground
            # classes plus background
            top[idx].reshape(1)
            self._name_to_top_map['labels'] = idx
            idx += 1

            if cfg.TRAIN.BBOX_REG:
                # bbox_targets blob: R bounding-box regression targets with 4
                # targets per class
                top[idx].reshape(1, self._num_classes * 4)
                self._name_to_top_map['bbox_targets'] = idx
                idx += 1

                # bbox_inside_weights blob: At most 4 targets per roi are active;
                # thisbinary vector sepcifies the subset of active targets
                top[idx].reshape(1, self._num_classes * 4)
                self._name_to_top_map['bbox_inside_weights'] = idx
                idx += 1

                top[idx].reshape(1, self._num_classes * 4)
                self._name_to_top_map['bbox_outside_weights'] = idx
                idx += 1

        print 'RoiDataLayer: name_to_top:', self._name_to_top_map
        assert len(top) == len(self._name_to_top_map)

    def forward(self, bottom, top):
        """Get blobs and copy them into this layer's top blob vector."""
        blobs = self._get_next_minibatch()

        for blob_name, blob in blobs.iteritems():
            top_ind = self._name_to_top_map[blob_name]
            # Reshape net's input blobs
            top[top_ind].reshape(*(blob.shape))
            # Copy data into net's input blobs
            top[top_ind].data[...] = blob.astype(np.float32, copy=False)

    def backward(self, top, propagate_down, bottom):
        """This layer does not propagate gradients."""
        pass

    def reshape(self, bottom, top):
        """Reshaping happens during the call to forward."""
        pass

class BlobFetcher(Process):
    """Experimental class for prefetching blobs in a separate process."""
    def __init__(self, queue, roidb, num_classes):
        super(BlobFetcher, self).__init__()
        self._queue = queue
        self._roidb = roidb
        self._num_classes = num_classes
        self._perm = None
        self._cur = 0
        self._shuffle_roidb_inds()
        # fix the random seed for reproducibility
        np.random.seed(cfg.RNG_SEED)
        
        self.daemon = True

    def _shuffle_roidb_inds(self):
        """Randomly permute the training roidb."""
        # TODO(rbg): remove duplicated code
        self._perm = np.random.permutation(np.arange(len(self._roidb)))
        self._cur = 0

    def _get_next_minibatch_inds(self):
        """Return the roidb indices for the next minibatch."""
        # TODO(rbg): remove duplicated code
        if self._cur + cfg.TRAIN.IMS_PER_BATCH >= len(self._roidb):
            self._shuffle_roidb_inds()

        db_inds = self._perm[self._cur:self._cur + cfg.TRAIN.IMS_PER_BATCH]
        self._cur += cfg.TRAIN.IMS_PER_BATCH
        return db_inds

    def run(self):
        print 'BlobFetcher started'
        target_pic = False
        targets = target_roi_gen()
        while True:
            if target_pic:
                target_roi = next(targets)
                minibatch_db = [target_roi]
            else:
                db_inds = self._get_next_minibatch_inds()
                minibatch_db = [self._roidb[i] for i in db_inds]
                
            blobs = get_minibatch(minibatch_db, self._num_classes)
            self._queue.put(blobs)
            
            target_pic = not target_pic


TARGET_DATA_PATH = "./TargetDataLoaderProcess/{}"

# counter txt's interface:
def update_read(read):
    tempfile = TARGET_DATA_PATH.format("read_temp.txt")
    file = TARGET_DATA_PATH.format("read.txt")
    with open(tempfile,'w') as f:
        f.write(str(read))
        f.flush()
        os.fsync(f.fileno())
    # atomic:
    os.rename(tempfile,file)

def get_fetched():
    with open(TARGET_DATA_PATH.format("fetched.txt"),'r') as f:
        numstr = f.read()
    return int(numstr)


def target_roi_gen():
    
    num = 0
    fetched = 0
    read = 0
    
    
    # make sure we do not read an old version of fetched.txt:
    with open(TARGET_DATA_PATH.format("fetched.txt"),'w') as f:
        f.write(str(fetched))
        f.flush()
        os.fsync(f.fileno())
    # As long as read.txt is not increased, fetched.txt will not be overwritten by a newer write of the loader process it is reset.
    
    # triggers resetting of the live db:
    update_read(read)
    
    
    while True:
        
        # Ensure the file 'target_<num>.jpg" is loaded:
        if not fetched > num:
            fetched = get_fetched()
        while not fetched > num:
            time.sleep(.02) #query with 50 Hz untill the file(s) is (are) loaded.
            fetched = get_fetched()
        
        
        filepath = TARGET_DATA_PATH.format("target_{}.jpg".format(num))
        flipped = np.random.randint(2) == 1
        
        roi = {
            'gt_classes': np.array([1], dtype=np.int32),
            'max_classes': np.array([1]),
            'bbox_targets': np.array([[3.,0.,0.,0.,0.]], dtype=np.float32),
            'boxes': np.array([[0,0,0,0]], dtype=np.uint16),
            'max_overlaps': np.array([1.], dtype=np.float32),
            'gt_overlaps': np.array([1.],dtype=np.float32),
            'image' : filepath,
            'width': 0,
            'height': 0,
            'flipped': flipped
        }
        
        yield roi
        
        read += 1
        update_read(read)
        
        num += 1