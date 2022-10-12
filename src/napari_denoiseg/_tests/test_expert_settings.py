import pytest

import numpy as np

from qtpy.QtWidgets import QWidget

from napari_denoiseg.widgets import TrainingSettingsWidget
from napari_denoiseg.utils import generate_config


@pytest.mark.parametrize('shape', [(1, 16, 16, 1),
                                   (1, 16, 16, 16, 1)])
def test_default_values(qtbot, shape):
    # parent widget
    widget = QWidget()

    # expert settings
    widget_settings = TrainingSettingsWidget(widget)
    settings = widget_settings.get_settings()

    # create default N2V configuration
    config = generate_config(np.ones(shape), shape[1:-1])

    # compare the default values
    assert config.unet_kern_size == settings['unet_kern_size']
    assert config.unet_n_first == settings['unet_n_first']
    assert config.unet_n_depth == settings['unet_n_depth']
    assert config.unet_residual == settings['unet_residual']
    assert config.train_learning_rate == settings['train_learning_rate']
    assert config.n2v_neighborhood_radius == settings['n2v_neighborhood_radius']
    assert config.n2v_perc_pix == settings['n2v_perc_pix']
    assert config.relative_weights == settings['relative_weights']
    assert config.denoiseg_alpha == settings['denoiseg_alpha']


@pytest.mark.parametrize('shape', [(1, 16, 16, 1), (1, 16, 16, 16, 1)])
def test_configuration_compatibility(qtbot, shape):
    # parent widget
    widget = QWidget()

    # expert settings
    widget_settings = TrainingSettingsWidget(widget)
    settings = widget_settings.get_settings()

    # create configuration using the expert settings
    config = generate_config(np.ones(shape), shape[1:-1], **settings)
    assert config.is_valid()