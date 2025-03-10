import numpy as np


import pyvista

from .theme import *
from .tools import *
from .plotting import *


def plot(var_item, off_screen=None, full_screen=False, screenshot=None,
         interactive=True, cpos=None, window_size=None,
         show_bounds=False, show_axes=True, notebook=None, background=None,
         text='', return_img=False, eye_dome_lighting=False, use_panel=None,
         volume=False, **kwargs):
    """
    Convenience plotting function for a vtk or numpy object.

    Parameters
    ----------
    item : vtk or numpy object
        VTK object or numpy array to be plotted.

    off_screen : bool
        Plots off screen when True.  Helpful for saving screenshots
        without a window popping up.

    full_screen : bool, optional
        Opens window in full screen.  When enabled, ignores window_size.
        Default False.

    screenshot : str or bool, optional
        Saves screenshot to file when enabled.  See:
        help(pyvistanterface.Plotter.screenshot).  Default disabled.

        When True, takes screenshot and returns numpy array of image.

    window_size : list, optional
        Window size in pixels.  Defaults to [1024, 768]

    show_bounds : bool, optional
        Shows mesh bounds when True.  Default False. Alias ``show_grid`` also
        accepted.

    notebook : bool, optional
        When True, the resulting plot is placed inline a jupyter notebook.
        Assumes a jupyter console is active.

    show_axes : bool, optional
        Shows a vtk axes widget.  Enabled by default.

    text : str, optional
        Adds text at the bottom of the plot.

    volume : bool, optional
        Use the ``add_volume`` method for volume rendering.

    **kwargs : optional keyword arguments
        See help(Plotter.add_mesh) for additional options.

    Returns
    -------
    cpos : list
        List of camera position, focal point, and view up.

    img :  numpy.ndarray
        Array containing pixel RGB and alpha.  Sized:
        [Window height x Window width x 3] for transparent_background=False
        [Window height x Window width x 4] for transparent_background=True
        Returned only when screenshot enabled

    """
    if notebook is None:
        notebook = scooby.in_ipykernel()

    if notebook:
        off_screen = notebook
    plotter = Plotter(off_screen=off_screen, notebook=notebook)
    if show_axes:
        plotter.add_axes()

    plotter.set_background(background)

    if isinstance(var_item, list):
        if len(var_item) == 2:  # might be arrows
            isarr_0 = isinstance(var_item[0], np.ndarray)
            isarr_1 = isinstance(var_item[1], np.ndarray)
            if isarr_0 and isarr_1:
                plotter.add_arrows(var_item[0], var_item[1])
            else:
                for item in var_item:
                    if volume or (isinstance(item, np.ndarray) and item.ndim == 3):
                        plotter.add_volume(item, **kwargs)
                    else:
                        plotter.add_mesh(item, **kwargs)
        else:
            for item in var_item:
                if volume or (isinstance(item, np.ndarray) and item.ndim == 3):
                    plotter.add_volume(item, **kwargs)
                else:
                    plotter.add_mesh(item, **kwargs)
    else:
        if volume or (isinstance(var_item, np.ndarray) and var_item.ndim == 3):
            plotter.add_volume(var_item, **kwargs)
        else:
            plotter.add_mesh(var_item, **kwargs)

    if text:
        plotter.add_text(text)

    if show_bounds or kwargs.get('show_grid', False):
        if kwargs.get('show_grid', False):
            plotter.show_grid()
        else:
            plotter.show_bounds()

    if cpos is None:
        cpos = plotter.get_default_cam_pos()
        plotter.camera_position = cpos
        plotter.camera_set = False
    else:
        plotter.camera_position = cpos

    if eye_dome_lighting:
        plotter.enable_eye_dome_lighting()

    result = plotter.show(window_size=window_size,
                          auto_close=False,
                          interactive=interactive,
                          full_screen=full_screen,
                          screenshot=screenshot,
                          return_img=return_img,
                          use_panel=use_panel,
                          height=kwargs.get('height', 400))

    # close and return camera position and maybe image
    plotter.close()

    # Result will be handled by plotter.show(): cpos or [cpos, img]
    return result


def plot_arrows(cent, direction, **kwargs):
    """
    Plots arrows as vectors

    Parameters
    ----------
    cent : np.ndarray
        Accepts a single 3d point or array of 3d points.

    directions : np.ndarray
        Accepts a single 3d point or array of 3d vectors.
        Must contain the same number of items as cent.

    **kwargs : additional arguments, optional
        See help(pyvista.Plot)

    Returns
    -------
    Same as Plot.  See help(pyvista.Plot)

    """
    return plot([cent, direction], **kwargs)

def plot_compare_four(data_a, data_b, data_c, data_d, disply_kwargs=None,
                      plotter_kwargs=None, show_kwargs=None, screenshot=None,
                      camera_position=None, outline=None, outline_color='k',
                      labels=('A', 'B', 'C', 'D'), link=True, notebook=None):
    """Plot a 2 by 2 comparison of data objects. Plotting parameters and camera
    positions will all be the same.
    """
    datasets = [[data_a, data_b], [data_c, data_d]]
    labels = [labels[0:2], labels[2:4]]

    if plotter_kwargs is None:
        plotter_kwargs = {}
    if disply_kwargs is None:
        disply_kwargs = {}
    if show_kwargs is None:
        show_kwargs = {}

    plotter_kwargs['notebook'] = notebook

    p = pyvista.Plotter(shape=(2,2), **plotter_kwargs)

    for i in range(2):
        for j in range(2):
            p.subplot(i, j)
            p.add_mesh(datasets[i][j], **disply_kwargs)
            p.add_text(labels[i][j])
            if is_pyvista_obj(outline):
                p.add_mesh(outline, color=outline_color)
            if camera_position is not None:
                p.camera_position = camera_position

    if link:
        p.link_views()

    return p.show(screenshot=screenshot, **show_kwargs)
