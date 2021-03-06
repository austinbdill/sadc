import numpy as np
import tensorflow as tf
from data.data_loader import DataLoader
from models.model import *
from trainers.base_trainer import BaseTrainer
import imageio

class SimpleTrainer(BaseTrainer):

    def __init__(self, params):
        super(SimpleTrainer, self).__init__(params)
        
    def build(self):

        images, sparse, maps = self.init_data().next_batch

        self.images = tf.cast(images, tf.float32)

        self.sparse = tf.cast(sparse, tf.float32)

        self.maps = tf.cast(maps, tf.float32)
        
        input_imgs = tf.concat([self.images, tf.expand_dims(self.sparse, axis=3)], axis=3)

        self.net = SimpleNetwork(input_imgs, self.params)

        self.est_maps = tf.reshape(self.net.forward(), [-1, 200, 200])
        
        self.loss = tf.reduce_mean(tf.abs((self.est_maps - self.maps)))
        
        self.saver = tf.train.Saver(max_to_keep=1000)

    def update_ops(self):
        self.step = self.optim.minimize(self.loss)
        
    def training_step(self, i):
        loss, _ = self.sess.run([self.loss, self.step])
        return loss
        
    def save_checkpoint(self, i):
        self.saver.save(self.sess, self.result_dir + "/" + str(i) + ".ckpt")
        if self.params["save_output"]:
            img, sparse, maps, ests = self.sess.run([self.images, self.sparse, self.maps, self.est_maps])
            _map = maps[0, :, :]
            imageio.imwrite(self.result_dir + "/gt" + str(i) + ".png", _map)
            _est = ests[0, :, :]
            imageio.imwrite(self.result_dir + "/pred" + str(i) + ".png", _est)
            _img = img[0, :, :, :]
            imageio.imwrite(self.result_dir + "/img" + str(i) + ".png", _img)
            _sparse = sparse[0, :, :]
            imageio.imwrite(self.result_dir + "/sparse" + str(i) + ".png", _sparse)
            
    def save_final(self):
        self.saver.save(self.sess, self.result_dir + "/final.ckpt")
        if self.params["save_output"]:
            img, sparse, maps, ests = self.sess.run([self.images, self.sparse, self.maps, self.est_maps])
            _map = maps[0, :, :]
            imageio.imwrite(self.result_dir + "/gt_final.png", _map)
            _est = ests[0, :, :]
            imageio.imwrite(self.result_dir + "/pred_final.png", _est)
            _img = img[0, :, :, :]
            imageio.imwrite(self.result_dir + "/img_final.png", _img)
            _sparse = sparse[0, :, :]
            imageio.imwrite(self.result_dir + "/sparse_final.png", _sparse)
