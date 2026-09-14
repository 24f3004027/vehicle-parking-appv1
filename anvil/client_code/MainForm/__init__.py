"""
ParkSmart Anvil Client UI Form
Pure Python Client-side Form for Anvil Web Applications.
"""

from ._anvil_designer import MainFormTemplate
import anvil.server

class MainForm(MainFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.current_user = None
        self.show_login_view()

    def show_login_view(self):
        self.title_label.text = "ParkSmart - Welcome Back"
        self.status_label.text = "Log in to manage or book parking spots"
        self.login_card.visible = True
        self.dashboard_card.visible = False

    def login_btn_click(self, **event_args):
        username = self.username_box.text.strip()
        password = self.password_box.text
        
        result = anvil.server.call('login_user', username, password)
        if result['success']:
            self.current_user = result
            self.show_dashboard_view()
        else:
            self.status_label.text = f"Error: {result['message']}"

    def show_dashboard_view(self):
        self.login_card.visible = False
        self.dashboard_card.visible = True
        self.user_label.text = f"User: {self.current_user['username']} ({self.current_user['role']})"
        
        # Load lots
        lots = anvil.server.call('get_parking_lots')
        self.lots_repeater.items = lots

    def park_btn_click(self, sender, **event_args):
        lot_id = sender.tag['id']
        veh_num = self.vehicle_input.text.strip().upper()
        if not veh_num:
            self.status_label.text = "Please enter vehicle plate number."
            return

        result = anvil.server.call('park_vehicle', self.current_user['user_id'], lot_id, veh_num, "EV")
        if result['success']:
            self.status_label.text = f"Parked vehicle at Spot {result['spot_number']}!"
            self.show_dashboard_view()
        else:
            self.status_label.text = f"Error: {result['message']}"

    def logout_btn_click(self, **event_args):
        self.current_user = None
        self.show_login_view()
