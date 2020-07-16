import Settings


def set_function(function, params=[]):
    Settings.shared_main.set_current_function(function, params)


def set_current_time(time):
    Settings.current_t_val = time


def set_time_step(t_step):
    Settings.t_val_step = t_step


def set_color(r, g, b):
    for node in Settings.nodes:
        node.get_actor().GetProperty().SetColor(r, g, b)
        node.get_poly_actor().GetProperty().SetColor(r, g, b)


def set_function_param(param_index, value):
    Settings.shared_main.set_function_param(param_index, value)

def set_camera_focal_point(x, y, z):
    print("Set")

def set_cam_focal_point(node):
    Settings.main_window.active_camera