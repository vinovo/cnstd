# coding: utf-8
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import os
from pathlib import Path
import logging
import platform
import zipfile

import cv2
import mxnet as mx
import numpy as np
from PIL import Image
from mxnet import gluon
from mxnet.gluon.utils import download

from .consts import MODEL_VERSION, BACKBONE_NET_NAME, AVAILABLE_MODELS


fmt = '[%(levelname)s %(asctime)s %(funcName)s:%(lineno)d] %(' 'message)s '
logging.basicConfig(format=fmt)
logging.captureWarnings(True)
logger = logging.getLogger()


def set_logger(log_file=None, log_level=logging.INFO, log_file_level=logging.NOTSET):
    """
    Example:
        >>> set_logger(log_file)
        >>> logger.info("abc'")
    """
    log_format = logging.Formatter(fmt)
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.handlers = [console_handler]
    if log_file and log_file != '':
        if not Path(log_file).parent.exists():
            os.makedirs(Path(log_file).parent)
        if isinstance(log_file, Path):
            log_file = str(log_file)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_file_level)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
    return logger


def model_fn_prefix(backbone, epoch):
    return 'cnstd-v%s-%s-%04d.params' % (MODEL_VERSION, backbone, epoch)


def gen_context(num_gpu):
    if num_gpu < 0:
        num_gpu = mx.context.num_gpus()

    if num_gpu > 0:
        context = [mx.context.gpu(i) for i in range(num_gpu)]
    else:
        context = [mx.context.cpu()]
    return context


def check_context(context):
    if isinstance(context, str):
        return context.lower() in ('gpu', 'cpu')
    if isinstance(context, list):
        if len(context) < 1:
            return False
        return all(isinstance(ctx, mx.Context) for ctx in context)
    return isinstance(context, mx.Context)


def to_cpu(nd_array):
    return nd_array.as_in_context(mx.cpu())


def split_and_load(xs, ctx_list):
    return gluon.utils.split_and_load(
        xs, ctx_list=ctx_list, batch_axis=0, even_split=False
    )


def data_dir_default():
    """

    :return: default data directory depending on the platform and environment variables
    """
    system = platform.system()
    if system == 'Windows':
        return os.path.join(os.environ.get('APPDATA'), 'cnstd')
    else:
        return os.path.join(os.path.expanduser("~"), '.cnstd')


def data_dir():
    """

    :return: data directory in the filesystem for storage, for example when downloading models
    """
    return os.getenv('CNOCR_HOME', data_dir_default())


def check_model_name(model_name):
    assert model_name in BACKBONE_NET_NAME


def get_model_file(model_dir):
    r"""Return location for the downloaded models on local file system.

    This function will download from online model zoo when model cannot be found or has mismatch.
    The root directory will be created if it doesn't exist.

    Parameters
    ----------
    model_dir : str, default $CNOCR_HOME
        Location for keeping the model parameters.

    Returns
    -------
    file_path
        Path to the requested pretrained model file.
    """
    model_dir = os.path.expanduser(model_dir)
    par_dir = os.path.dirname(model_dir)
    os.makedirs(par_dir, exist_ok=True)

    zip_file_path = model_dir + '.zip'
    if not os.path.exists(zip_file_path):
        model_name = os.path.basename(model_dir)
        if model_name not in AVAILABLE_MODELS:
            raise NotImplementedError('%s is not an available downloaded model' % model_name)
        url = AVAILABLE_MODELS[model_name][1]
        download(url, path=zip_file_path, overwrite=True)
    with zipfile.ZipFile(zip_file_path) as zf:
        zf.extractall(par_dir)
    os.remove(zip_file_path)

    return model_dir


def read_charset(charset_fp):
    alphabet = [None]
    # 第0个元素是预留id，在CTC中用来分割字符。它不对应有意义的字符
    with open(charset_fp, encoding='utf-8') as fp:
        for line in fp:
            alphabet.append(line.rstrip('\n'))
    # print('Alphabet size: %d' % len(alphabet))
    try:
        space_idx = alphabet.index('<space>')
        alphabet[space_idx] = ' '
    except ValueError:
        pass
    inv_alph_dict = {_char: idx for idx, _char in enumerate(alphabet)}
    return alphabet, inv_alph_dict


def normalize_img_array(img, dtype='float32'):
    """ rescale to [-1.0, 1.0] """
    img = img.astype(dtype)
    img = img / 255.0
    img -= np.array((0.485, 0.456, 0.406))
    img /= np.array((0.229, 0.224, 0.225))
    return img


def imread(img_fp):
    """返回RGB格式的numpy数组"""
    # im = cv2.imdecode(np.fromfile(img_fp, dtype=np.uint8), flag)
    im = cv2.imread(img_fp, flags=1)  # res: color BGR
    if im is None:
        im = np.asarray(Image.open(img_fp).convert('RGB'))
    else:
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    return im
