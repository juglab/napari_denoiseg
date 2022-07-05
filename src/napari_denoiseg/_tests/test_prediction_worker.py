import pytest
import numpy as np
from napari_denoiseg._tests.test_utils import create_model, save_img, save_weights_h5
from napari_denoiseg.utils.prediction_worker import _run_lazy_prediction, _run_prediction
from napari_denoiseg.utils import State, UpdateType, lazy_load_generator, load_from_disk


# TODO: test from layers, and all with thresholding.
# TODO: test the prediction worker itself
@pytest.mark.parametrize('shape, axes',  # they are already reshaped
                         [((1, 16, 16, 1), 'SYXC'),
                          ((5, 16, 16, 1), 'SYXC'),
                          ((5, 16, 16, 3), 'SYXC'),
                          ((1, 16, 32, 32, 1), 'SZYXC'),
                          ((1, 16, 32, 32, 3), 'SZYXC'),
                          ((5, 16, 32, 32, 3), 'SZYXC')])
def test_run_prediction_from_disk(tmp_path, make_napari_viewer, shape, axes):
    n = 10
    new_shape_seg = (n * shape[0], *shape[1:-1], 3 + 2 * shape[-1])
    new_shape_den = (n * shape[0], *shape[1:])

    class MonkeyPatchWidget:
        def __init__(self, path):
            self.path = path
            self.state = State.RUNNING
            self.seg_prediction = np.zeros(new_shape_seg)
            self.denoi_prediction = np.zeros(new_shape_den)

        def get_model_path(self):
            return self.path

    # create model and save it to disk
    model = create_model(tmp_path, shape)
    path_to_h5 = save_weights_h5(model, tmp_path)

    # create files
    save_img(tmp_path, n, shape)

    # instantiate generator
    images = load_from_disk(tmp_path, axes)
    assert images.shape == new_shape_den

    # run prediction (it is a generator)
    mk = MonkeyPatchWidget(path_to_h5)
    hist = list(_run_prediction(mk, axes, images))
    assert hist[-1] == {UpdateType.DONE}
    assert len(hist) == new_shape_seg[0]+2


@pytest.mark.parametrize('shape, axes',  # they are already reshaped
                         [((1, 16, 16, 1), 'SYXC'),
                          ((5, 16, 16, 1), 'SYXC'),
                          ((5, 16, 16, 3), 'SYXC'),
                          ((1, 16, 32, 32, 1), 'SZYXC'),
                          ((1, 16, 32, 32, 3), 'SZYXC'),
                          ((5, 16, 32, 32, 3), 'SZYXC')])
def test_run_lazy_prediction(tmp_path, shape, axes):
    class MonkeyPatchWidget:
        def __init__(self, path):
            self.path = path
            self.state = State.RUNNING

        def get_model_path(self):
            return self.path

    # create model and save it to disk
    model = create_model(tmp_path, shape)
    path_to_h5 = save_weights_h5(model, tmp_path)

    # create files
    n = 10
    save_img(tmp_path, n, shape)

    # instantiate generator
    gen, m = lazy_load_generator(tmp_path)
    assert m == n

    # run prediction (it is a generator)
    mk = MonkeyPatchWidget(path_to_h5)
    hist = list(_run_lazy_prediction(mk, axes, gen))
    assert hist[-1] == {UpdateType.DONE}
    assert len(hist) == n+1

    # check that images have been saved
    image_files = [f for f in tmp_path.glob('*.tif*')]
    assert len(image_files) == 3 * n
