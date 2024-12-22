import getpass
import dbus
from qtpy.QtWidgets import QApplication, QInputDialog, QLineEdit

def get_password_gui():
    _app = QApplication.instance() or QApplication([])
    password, ok = QInputDialog.getText(
        None,
        "Password Input",
        "Enter your password:",
        QLineEdit.Password
    )
    if ok and password:
        return password
    else:
        return None

def open_db(gui=False):
    SERVICE_NAME = "org.kde.krunner_kdbx"
    OBJECT_PATH = "/runner"
    METHOD_NAME = "Password"

    if gui:
        input_string = get_password_gui()
    else:
        input_string = getpass.getpass()

    try:
        session_bus = dbus.SessionBus()
        dbus_object = session_bus.get_object(SERVICE_NAME, OBJECT_PATH)
        method = dbus_object.get_dbus_method(METHOD_NAME, SERVICE_NAME)
        result = method(input_string)
        print(f"Service response: {result}")

    except dbus.DBusException as e:
        print(f"Error: {e}")
