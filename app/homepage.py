from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.appbar import MDTopAppBar, MDTopAppBarTitle
from kivymd.uix.button import MDFabButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.pickers import MDTimePickerDialVertical
from alarmcard import AlarmCard
from select_days import DaysDialog

class MainApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        screen = MDScreen()

        #topbar
        topbar = MDTopAppBar(
            MDTopAppBarTitle(text="Aerium", halign="center"),
            type="large",
            pos_hint={"top": 1},
        )
        screen.add_widget(topbar)

        #Layout principal vertical
        main_layout = MDBoxLayout(
            orientation="vertical",
            padding=("20dp", "160dp", "20dp", "22p"),
            spacing="20dp",
        )


        #Label de base
        self.label = MDLabel(
            text="Ajoutez une alarme !",
            halign="center",
            font_style="Headline",
        )
        main_layout.add_widget(self.label)

        #layout d'alarmes avec scroll
        scroll = MDScrollView(size_hint=(1, 1))

        self.alarms_layout = MDBoxLayout(
            orientation="vertical",
            spacing="15dp",
            size_hint_y=None,
        )
        self.alarms_layout.bind(minimum_height=self.alarms_layout.setter("height"))

        scroll.add_widget(self.alarms_layout)

        main_layout.add_widget(scroll)
        screen.add_widget(main_layout)

        #FAB
        fab = MDFabButton(
            icon="plus",
            pos_hint={"right": 0.95, "y": 0.04},
            on_release=self.show_time_picker,
        )
        screen.add_widget(fab)

        return screen
    
    def show_time_picker(self, *args):
        time_picker = MDTimePickerDialVertical()
        time_picker.bind(on_ok=self.on_ok)
        time_picker.open()
        
    def on_ok(self, timepicker):
        time = f"{timepicker.hour.zfill(2)}:{timepicker.minute.zfill(2)}"
        timepicker.dismiss()
        self.show_days_dialog(time)
        
    def on_cancel(self, timepicker):   
        timepicker.dismiss()
        
    def show_days_dialog(self, time):
        dialog = DaysDialog()
        dialog.open()
        dialog.bind(on_dismiss=lambda instance: self.on_dialog_dismiss(instance, time))
        
    def on_dialog_dismiss(self, dialog, time):
        if dialog.state == False:
            selected_days = ", ".join([i[:3] for i in dialog.selected_days]) if dialog.selected_days else "Tout les jours"
            self.add_alarm(time, selected_days)
            
    def add_alarm(self, time,selected_days=None):
        # supprime le label si première alarme
        if self.label.parent:
            self.label.parent.remove_widget(self.label)
            
        card = AlarmCard(time, selected_days)
        self.alarms_layout.add_widget(card)


MainApp().run()