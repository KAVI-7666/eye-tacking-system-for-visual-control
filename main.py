# --------------- Imports (Keep these at the top) ---------------
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.properties import ObjectProperty
import requests
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.clock import Clock
from threading import Thread

import cursor
import onlyleft
import onlyright
import bothclick


# --------------- Settings ---------------
Window.size = (600, 500)
Window.resizable = False

# --------------- Global Variable ---------------
datarunfile = ""

stop_flag = False


# --------------- Widget & Logic Classes ---------------
class Footer(GridLayout):
    pass


class SettingButton(BoxLayout):
    def print_switch_id(self, switch_id, is_active):
        global datarunfile
        datarunfile = switch_id


class Startbutton(BoxLayout):
    button_text = StringProperty("Start")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tracking_thread = None
        self.is_running = False

    def start_button_clicked(self):
        if not self.is_running:
            self.is_running = True
            self.button_text = "Stop"
            self.tracking_thread = Thread(target=cursor.eye_controlled_mouse)
            self.tracking_thread.start()
        else:
            self.is_running = False
            self.button_text = "Start"
            cursor.stop_eye_control()  # <- THIS is the line that caused your error



# --------------- Screen Classes ---------------
class Home(Screen):
    pass


class About(Screen):
    pass


class FlowChart(Screen):
    pass


class Setting(Screen):
    pass


class LoginScreen(Screen):
    pass


class SignupScreen(Screen):
    pass


# --------------- Layout Classes ---------------
class WindowManger(ScreenManager):
    pass


class Sidebar(GridLayout):
    pass


class Bodysection(GridLayout):
    pass


class HoriLine(GridLayout):
    pass


class MainBox(GridLayout):
    header = ObjectProperty(None)
    bodysection = ObjectProperty(None)


class Header(GridLayout):
    loginsign = ObjectProperty(None)


class Loginsign(BoxLayout):
    login_btn = ObjectProperty(None)
    signup_btn = ObjectProperty(None)


# --------------- App Class ---------------
class EyeTrack(App):
    def build(self):
        Builder.load_file("main.kv")
        root = MainBox()
        print("🪪 Checking login_btn:", root.ids.header.ids.loginsign.ids.login_btn)

        # On app start: hide welcome/logout, show login/signup
        root.ids.header.ids.loginsign.ids.welcome_label.opacity = 0
        root.ids.header.ids.loginsign.ids.logout_btn.opacity = 0
        root.ids.header.ids.loginsign.ids.login_btn.opacity = 1
        root.ids.header.ids.loginsign.ids.signup_btn.opacity = 1
        root.ids.header.ids.loginsign.ids.login_btn.disabled = False
        root.ids.header.ids.loginsign.ids.signup_btn.disabled = False

        return root

    def on_start(self):
        print(
            "Login Opacity:", self.root.ids.header.ids.loginsign.ids.login_btn.opacity
        )
        print(
            "Login Disabled:", self.root.ids.header.ids.loginsign.ids.login_btn.disabled
        )

    def login(self, username, password):
        try:
            url = "http://127.0.0.1:8000/api/login/"
            data = {"username": username, "password": password}
            response = requests.post(url, json=data)

            if response.status_code == 200:
                token = response.json().get("token")
                print("✅ Login Successful! Token:", token)
                self.root.ids.bodysection.ids.screen_manager.current = "home"
                self.root.ids.header.ids.loginsign.ids.login_btn.disabled = True
                self.root.ids.header.ids.loginsign.ids.login_btn.disabled = True
                self.root.ids.header.ids.loginsign.ids.login_btn.opacity = 0
                self.root.ids.header.ids.loginsign.ids.signup_btn.opacity = 0

                # logout
                self.root.ids.header.ids.loginsign.ids.welcome_label.text = (
                    f"Welcome, {username}"
                )
                self.root.ids.header.ids.loginsign.ids.welcome_label.opacity = 1
                self.root.ids.header.ids.loginsign.ids.logout_btn.opacity = 1

            else:
                print("❌ Login Failed:", response.json())

        except Exception as e:
            print("🔥 Error during login:", e)

    def signup(self, name, username, password):
        try:
            url = "http://127.0.0.1:8000/api/signup/"
            data = {"name": name, "username": username, "password": password}
            response = requests.post(url, json=data)

            if response.status_code == 200:
                print("✅ Signup Successful!")
                App.get_running_app().root.ids.bodysection.ids.screen_manager.current = (
                    "login"
                )

            else:
                print("❌ Signup Failed:", response.json())

        except Exception as e:
            print("🔥 Error during signup:", e)

    def logout(self):
        try:
            headers = {"Authorization": f"Token {self.user_token}"}
            requests.post("http://127.0.0.1:8000/api/logout/", headers=headers)
            print("✅ Logged out from backend.")
        except Exception as e:
            print("🔥 Logout failed:", e)

        # Show login/signup again
        self.root.ids.header.ids.loginsign.ids.login_btn.opacity = 1
        self.root.ids.header.ids.loginsign.ids.signup_btn.opacity = 1
        self.root.ids.header.ids.loginsign.ids.login_btn.disabled = False
        self.root.ids.header.ids.loginsign.ids.signup_btn.disabled = False

        # Hide welcome + logout
        self.root.ids.header.ids.loginsign.ids.welcome_label.text = ""
        self.root.ids.header.ids.loginsign.ids.welcome_label.opacity = 0
        self.root.ids.header.ids.loginsign.ids.logout_btn.opacity = 0

        # Go back to login screen
        self.root.ids.bodysection.ids.screen_manager.current = "login"


# --------------- Run the App ---------------
EyeTrack().run()
