from .service import *

import time
from tkinter import *
import tkinter.ttk as ttk
from pathlib import Path
import matplotlib.pyplot as plt


class Image:
    def __init__(self, photos):
        self.image = photos


### UI MAKER ###
class UIMaker:
    def __init__(self):
        self.window = Tk()
        self.window.title("SchliessFach")
        self.window.geometry("1440x1024")
        self.window.configure(bg="#ffffff")
        self.canvas = Canvas(
            self.window,
            bg="#ffffff",
            height=1024,
            width=1440,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )
        self.canvas.place(x=0, y=0)
        self.OUTPUT_PATH = Path(__file__).parent
        self.ASSETS_PATH = self.OUTPUT_PATH / Path(".")

    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)

    def make_background(self, file_name):
        global background_image
        background_image = PhotoImage(file=self.relative_to_assets(file_name))
        background = self.canvas.create_image(720.0, 512.0, image=background_image)
        return background

    def make_buton(self, file_name, commands):
        global button_image
        button_image = PhotoImage(file=self.relative_to_assets(file_name))
        button = Button(
            image=button_image,
            borderwidth=0,
            highlightthickness=0,
            command=commands,
            relief="flat",
        )
        return button, button_image

    def make_entry(self, file_name, x, y):
        global entry_image
        entry_image = PhotoImage(file=self.relative_to_assets(file_name))
        entry_background = self.canvas.create_image(x, y, image=entry_image)

        entry = Entry(bd=0, bg="#e1e1e1", highlightthickness=0)
        return entry, entry_image

    def create_text(self, x, y, texts):
        return self.canvas.create_text(
            x, y, text=texts, fill="#000000", font=("None", int(20.0))
        )


# END# UI MAKER #END#


@inject
class BoxUI:
    def __init__(self, service: BoxService):
        self.service = service
        self.make = UIMaker()

        self.current_op = None  # Current operator logging in
        self.current_user = None  # Current user logging in
        self.req_size = None  # For courier

    ### Report avg keep time for items
    def show_chart(self):
        ### Plot
        avg_time = self.service.search_avg_keep_time_for_every_items()
        item_type_avg_time = []
        item_type = []
        for i in avg_time:
            if avg_time[i].avg_time == None:
                item_type_avg_time.append(0)
            else:
                item_type_avg_time.append(avg_time[i].avg_time)

            item_type.append(avg_time[i].item_type)

        avg_time2 = self.service.search_avg_keep_time_for_every_item_size()
        item_size_avg_time = []
        item_size = []
        for i in avg_time2:
            if avg_time2[i].avg_time == None:
                item_size_avg_time.append(0)
            else:
                item_size_avg_time.append(avg_time2[i].avg_time)

            item_size.append(avg_time2[i].item_size)

        fig, axs = plt.subplots(1, 2, figsize=(12, 5))
        axs[0].bar(item_type, item_type_avg_time, width=0.1)
        axs[0].set_title("item type / time(min)")
        axs[1].bar(item_size, item_size_avg_time, width=0.1)
        axs[1].set_title("item size / time(min)")
        fig.tight_layout()

        plt.show()
        return True
        # END#

    # END#

    ### User log in
    def log_in(self, id, password):
        if id == "" or password == "":
            return

        # print("login")
        log_in = self.service.log_in(id, password)

        if log_in == True:
            self.current_user = id
            self.switch_frames()
            self.show_open_locker1()
        else:
            self.show_main02()

    # END#

    ### Switch frames in the ui
    def switch_frames(self):
        self.make.window.destroy()
        self.make = UIMaker()

    # END#

    ### Back to main menu
    def back_to_main(self):
        self.set_cur_user_to_none()
        self.switch_frames()
        self.show_main01()

    # END#

    ### Operator menu
    def switch_to_operator_menu(self):
        self.switch_frames()
        self.show_operator_sign_in1()

    # END#

    ### Register User or Sign Up
    def switch_to_register_user(self):
        self.switch_frames()
        self.show_sign_up1()

    # END#

    ### Courier package delivery menu
    def switch_to_courier_menu(self):
        self.switch_frames()
        self.show_courier1()

    # END#

    ### Operator mode menu
    def switch_to_operator_mode(self, op_id, op_pass):  # Operator log in
        if op_id == "" or op_pass == "":
            return

        op_log_in = self.service.op_log_in(op_id, op_pass)

        if op_log_in == False:  # Invalid operator id or pass
            self.show_operator_sign_in2()
        elif op_log_in == True:  # Successful
            self.switch_frames()
            self.show_operator_mode1()

    # END#

    ### Open and Close Locker Box
    def open_box(self, locker_id):
        self.service.open_locker(int(locker_id))
        # time.sleep(2)

    def close_box(self, locker_id):
        self.service.close_locker(int(locker_id))
        # time.sleep(2)
        self.set_cur_user_to_none()
        self.switch_frames()
        self.show_main01()

    # END#

    ### Retrieve and Deliver Package
    def retrieve_package(self, id, locker_id, verification):
        if locker_id == "" or verification == "":
            return

        retrieve = self.service.retrieve_package(id, locker_id, verification)

        if retrieve == True:
            self.open_box(locker_id)
            self.switch_frames()
            self.show_retrieve_package(locker_id)
        else:
            self.show_open_locker2()

    def deliver_package(self, id, item_type, item_size):
        if item_size == None or id == "" or item_type == "":
            return

        deliver = self.service.store_package(id, item_type, item_size)

        if deliver == False:  # Wrong ID Input
            self.switch_frames()
            self.show_courier3(id)
        elif deliver == "NO LOCKER AVAILABLE":  # No locker available
            self.switch_frames()
            self.show_courier4()
        else:  # Successful
            self.open_box(int(deliver))
            self.set_req_size_to_none()
            self.switch_frames()
            self.show_courier2(deliver, id, item_type, item_size)

    # END#

    ### Request Package Size for Delivering
    def request_big(self):
        self.req_size = "BESAR"

    def request_med(self):
        self.req_size = "SEDANG"

    def request_sml(self):
        self.req_size = "KECIL"

    # END#

    # Sign Up or Register New User
    def register(self, name, email, password):
        if name == "" or email == "" or password == "":
            return

        register = self.service.register(name, email, password)

        if register == "PASSWORD TOO SHORT":
            self.show_sign_up5()
        elif register == "EMAIL HAS BEEN USED":
            self.show_sign_up2()
        elif register == "INVALID EMAIL":
            self.show_sign_up3()
        elif register == True:
            self.switch_frames()
            self.show_sign_up4()

    # END#

    def switch_to_report(self):
        self.show_report()

    def switch_to_main_from_report(self, window):
        window.destroy()
        self.make = UIMaker()
        self.show_main01()

    def switch_to_operator_mode_from_report(self, window):
        window.destroy()
        self.make = UIMaker()
        self.show_operator_mode1()

    ### Operator delete account menu
    def switch_to_delete_acc(self):
        self.switch_frames()
        self.show_delete_user1()

    # END#

    ### Operator register new operator menu
    def switch_to_regist_op(self):
        self.make.window.destroy()
        self.show_regis_op1()

    # END#

    ### Register new operator
    def regis_op(self, op_name, op_id, op_pass):
        if op_id == "" or op_name == "" or op_pass == "":
            return

        register = self.service.register_op(op_name, op_id, op_pass)

        if register == False:
            self.show_regis_op4()
        elif register == "PASSWORD TOO SHORT":
            self.show_regis_op3()
        elif register == True:
            self.switch_frames()
            self.show_regis_op2()

    # END#

    ### Unregister/delete a user
    def delete_user(self, name, email):
        if name == "" or email == "":
            return

        delete = self.service.unregister(name, email)

        if delete == False:  # Invalid name or email
            self.show_delete_user2()
        else:  # Successful
            self.switch_frames()
            self.show_delete_user3()

    # END#

    ### Set current user, current operator, req size to none in attribute
    def set_cur_user_to_none(self):
        self.current_user = None

    def set_cur_op_to_none(self):
        self.current_op = None

    def set_req_size_to_none(self):
        self.req_size = None

    # END#

    ### SHOWSHOW ###

    ### Main menu
    def show_main01(self):
        background = self.make.make_background("background1.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("login.png"))

        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.log_in(entry0.get(), entry1.get()),
            relief="flat",
        )
        b0.place(x=625, y=600, width=190, height=44)

        b1, b1.image = self.make.make_buton(
            "signup_now.png", self.switch_to_register_user
        )
        b1.place(x=764, y=683, width=104, height=19)

        b3, b3.image = self.make.make_buton(
            "iamcourier.png", self.switch_to_courier_menu
        )
        b3.place(x=651, y=710, width=126, height=19)

        b4, b4.image = self.make.make_buton(
            "iamadmin.png", self.switch_to_operator_menu
        )
        b4.place(x=654, y=737, width=128, height=20)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 738.5, 446.0)
        entry0.place(x=609, y=429, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 738.5, 520.0)
        entry1.place(x=609, y=503, width=259, height=32)

        self.make.window.mainloop()
        return None

    def show_main02(self):  # wrong id or pass
        background = self.make.make_background("background2.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("login.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.log_in(entry0.get(), entry1.get()),
            relief="flat",
        )
        b0.place(x=625, y=600, width=190, height=44)

        b1, b1.image = self.make.make_buton(
            "signup_now.png", self.switch_to_register_user
        )
        b1.place(x=764, y=683, width=104, height=19)

        b3, b3.image = self.make.make_buton(
            "iamcourier.png", self.switch_to_courier_menu
        )
        b3.place(x=651, y=710, width=126, height=19)

        b4, b4.image = self.make.make_buton(
            "iamadmin.png", self.switch_to_operator_mode
        )
        b4.place(x=654, y=737, width=128, height=20)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 738.5, 446.0)
        entry0.place(x=609, y=429, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 738.5, 520.0)
        entry1.place(x=609, y=503, width=259, height=32)

        self.make.window.mainloop()
        return None

    # END#

    ### Retrieve Package
    def show_retrieve_package(self, locker_id):
        background = self.make.make_background("background22.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("closebox.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.close_box(locker_id),
            relief="flat",
        )
        b0.place(x=625, y=600, width=190, height=44)

        self.make.window.mainloop()
        return None

    # END#

    ### Courier Menu
    def show_courier1(self):  # open box
        background = self.make.make_background("background3.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("openbox.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.deliver_package(
                entry0.get(), entry1.get().upper(), self.req_size
            ),
            relief="flat",
        )
        b0.place(x=280, y=690, width=190, height=44)

        b1, b1.image = self.make.make_buton("big.png", self.request_big)
        b1.place(x=184, y=621, width=115, height=38)

        b2, b2.image = self.make.make_buton("med.png", self.request_med)
        b2.place(x=315, y=621, width=115, height=38)

        b3, b3.image = self.make.make_buton("sml.png", self.request_sml)
        b3.place(x=452, y=621, width=115, height=38)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 385.5, 452.0)
        entry0.place(x=256, y=435, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox0.png", 389.5, 546.0)
        entry1.place(x=260, y=529, width=259, height=32)

        self.make.window.mainloop()
        return None

    def show_courier2(self, locker_id, id, item_type, item_size):  # close box
        background = self.make.make_background("background4.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("closebox.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.close_box(locker_id),
            relief="flat",
        )
        b0.place(x=281, y=725, width=190, height=44)

        self.make.create_text(382.5, 527.0, ("Recipient ID: " + f"{id}"))
        self.make.create_text(382.5, 575.0, ("Locker ID: " + f"{locker_id}"))
        self.make.create_text(382.5, 623.0, ("Item type: " + f"{item_type}"))
        self.make.create_text(382.5, 671.0, ("Item size: " + f"{item_size}"))

        self.make.window.mainloop()
        return None

    def show_courier3(self, invalid_id):  # invalid id
        background = self.make.make_background("background5.png")

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        self.make.create_text(370.0, 500.0, (f"{invalid_id}"))
        self.make.create_text(375.5, 537.0, ("is an invalid post ID."))
        self.make.create_text(368.0, 574.0, ("Please contact security."))
        self.make.create_text(374.0, 613.5, ("Thank you."))

        self.make.window.mainloop()
        return None

    def show_courier4(self):  # box full
        background = self.make.make_background("background6.png")

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        self.make.window.mainloop()
        return None

    # END#

    ### Sign Up Menu
    def show_sign_up1(self):
        background = self.make.make_background("background7.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("signup.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.register(entry0.get(), entry1.get(), entry3.get()),
            relief="flat",
        )
        b0.place(x=628, y=711, width=190, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 733.5, 473.0)
        entry0.place(x=604, y=456, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 737.5, 567.0)
        entry1.place(x=608, y=550, width=259, height=32)

        entry3, entry3.image = self.make.make_entry("img_textBox2.png", 739.5, 657.0)
        entry3.place(x=610, y=640, width=259, height=32)

        self.make.window.mainloop()
        return None

    def show_sign_up2(self):  # email taken
        background = self.make.make_background("background8.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("signup.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.register(entry0.get(), entry1.get(), entry3.get()),
            relief="flat",
        )
        b0.place(x=628, y=711, width=190, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 733.5, 473.0)
        entry0.place(x=604, y=456, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 737.5, 567.0)
        entry1.place(x=608, y=550, width=259, height=32)

        entry3, entry3.image = self.make.make_entry("img_textBox2.png", 739.5, 657.0)
        entry3.place(x=610, y=640, width=259, height=32)

        self.make.window.mainloop()
        return None

    def show_sign_up3(self):  # invalid email add
        background = self.make.make_background("background9.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("signup.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.register(entry0.get(), entry1.get(), entry3.get()),
            relief="flat",
        )
        b0.place(x=628, y=711, width=190, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 733.5, 473.0)
        entry0.place(x=604, y=456, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 737.5, 567.0)
        entry1.place(x=608, y=550, width=259, height=32)

        entry3, entry3.image = self.make.make_entry("img_textBox2.png", 739.5, 657.0)
        entry3.place(x=610, y=640, width=259, height=32)

        self.make.window.mainloop()
        return None

    def show_sign_up4(self):  # succ sign up
        background = self.make.make_background("background20.png")

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        self.make.window.mainloop()
        return None

    def show_sign_up5(self):  # Password too short
        background = self.make.make_background("background23.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("signup.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.register(entry0.get(), entry1.get(), entry3.get()),
            relief="flat",
        )
        b0.place(x=628, y=711, width=190, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 733.5, 473.0)
        entry0.place(x=604, y=456, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 737.5, 567.0)
        entry1.place(x=608, y=550, width=259, height=32)

        entry3, entry3.image = self.make.make_entry("img_textBox2.png", 739.5, 657.0)
        entry3.place(x=610, y=640, width=259, height=32)

        self.make.window.mainloop()
        return None

    # END#

    ### Retrieving locker step after log in
    def show_open_locker1(self):  # after login
        background = self.make.make_background("background10.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("openlocker.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.retrieve_package(
                self.current_user, entry0.get(), entry1.get()
            ),
            relief="flat",
        )
        b0.place(x=625, y=640, width=190, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 734.5, 517.0)
        entry0.place(x=605, y=500, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 734.5, 591.0)
        entry1.place(x=605, y=574, width=259, height=32)

        self.make.window.mainloop()
        return None

    def show_open_locker2(self):  # wrong ver code or locker id
        background = self.make.make_background("background11.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("openlocker.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.retrieve_package(
                self.current_user, entry0.get(), entry1.get()
            ),
            relief="flat",
        )
        b0.place(x=625, y=640, width=190, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 734.5, 517.0)
        entry0.place(x=605, y=500, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 734.5, 591.0)
        entry1.place(x=605, y=574, width=259, height=32)

        self.make.window.mainloop()
        return None

    def show_open_locker3(self):  # wrong ver code or locker id
        background = self.make.make_background("background12.png")

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        self.make.create_text(719.5, 499.0, "Sorry, your locker verification ")
        self.make.create_text(720.5, 528.0, "code has expired. You have to pay")
        self.make.create_text(719.0, 558.0, "self.dues")
        self.make.create_text(726.0, 584.0, "to reactivate your code. Please ")
        self.make.create_text(726.0, 612.0, "visit our nearest operator to pay")
        self.make.create_text(726.0, 639.5, "your dues. Thank you.")

        self.make.window.mainloop()
        return None

    # END#

    ### Operator sign in
    def show_operator_sign_in1(self):
        background = self.make.make_background("background13.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("login.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.switch_to_operator_mode(entry0.get(), entry1.get()),
            relief="flat",
        )
        b0.place(x=625, y=644, width=190, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 738.5, 513.0)
        entry0.place(x=609, y=500, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 738.5, 587.0)
        entry1.place(x=609, y=574, width=259, height=32)

        self.make.window.mainloop()
        return None

    def show_operator_sign_in2(self):  # wrong op id or pass
        background = self.make.make_background("background14.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("login.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.switch_to_operator_mode(entry0.get(), entry1.get()),
            relief="flat",
        )
        b0.place(x=625, y=644, width=190, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 738.5, 513.0)
        entry0.place(x=609, y=500, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 738.5, 587.0)
        entry1.place(x=609, y=574, width=259, height=32)

        self.make.window.mainloop()
        return None

    # END#

    ### Operator Mode
    def show_operator_mode1(self):  # op menu
        background = self.make.make_background("background15.png")

        b0, b0.image = self.make.make_buton("deleteacc.png", self.switch_to_delete_acc)
        b0.place(x=609, y=549, width=222, height=44)

        b1, b1.image = self.make.make_buton("report.png", self.switch_to_report)
        b1.place(x=609, y=629, width=222, height=44)

        b2, b2.image = self.make.make_buton("registerop.png", self.switch_to_regist_op)
        b2.place(x=609, y=469, width=222, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        self.make.window.mainloop()
        return None

    ### Registering new operator menu
    def show_regis_op1(self):
        background = self.make.make_background("background16.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("register.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.regis_op(entry0.get(), entry1.get(), entry3.get()),
            relief="flat",
        )
        b0.place(x=628, y=711, width=190, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        b5, b5.image = self.make.make_buton("back.png", self.switch_to_operator_menu)
        b5.place(x=41, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 733.5, 473.0)
        entry0.place(x=604, y=456, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 737.5, 567.0)
        entry1.place(x=608, y=550, width=259, height=32)

        entry3, entry3.image = self.make.make_entry("img_textBox2.png", 739.5, 657.0)
        entry3.place(x=610, y=640, width=259, height=32)

        self.make.window.mainloop()
        return None

    def show_regis_op2(self):  # succ making new op
        background = self.make.make_background("background18.png")

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        b5, b5.image = self.make.make_buton("back.png", self.switch_to_operator_menu)
        b5.place(x=41, y=17, width=90, height=93)

        self.make.window.mainloop()
        return None

    def show_regis_op3(self):  # Invalid operator pass
        background = self.make.make_background("background24.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("register.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.regis_op(entry0.get(), entry1.get(), entry3.get()),
            relief="flat",
        )
        b0.place(x=628, y=711, width=190, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        b5, b5.image = self.make.make_buton("back.png", self.switch_to_operator_menu)
        b5.place(x=41, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 733.5, 473.0)
        entry0.place(x=604, y=456, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 737.5, 567.0)
        entry1.place(x=608, y=550, width=259, height=32)

        entry3, entry3.image = self.make.make_entry("img_textBox2.png", 739.5, 657.0)
        entry3.place(x=610, y=640, width=259, height=32)

        self.make.window.mainloop()
        return None

    def show_regis_op4(self):  # Invalid operator id
        background = self.make.make_background("background25.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("register.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.regis_op(entry0.get(), entry1.get(), entry3.get()),
            relief="flat",
        )
        b0.place(x=628, y=711, width=190, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        b5, b5.image = self.make.make_buton("back.png", self.switch_to_operator_menu)
        b5.place(x=41, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 733.5, 473.0)
        entry0.place(x=604, y=456, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 737.5, 567.0)
        entry1.place(x=608, y=550, width=259, height=32)

        entry3, entry3.image = self.make.make_entry("img_textBox2.png", 739.5, 657.0)
        entry3.place(x=610, y=640, width=259, height=32)

        self.make.window.mainloop()
        return None

    # END#

    ### Delete user in operator menu
    def show_delete_user1(self):
        background = self.make.make_background("background17.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("deleteuser.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.delete_user(entry0.get(), entry1.get()),
            relief="flat",
        )
        b0.place(x=625, y=644, width=190, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        b5, b5.image = self.make.make_buton("back.png", self.switch_to_operator_menu)
        b5.place(x=41, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 738.5, 513.0)
        entry0.place(x=609, y=496, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 738.5, 587.0)
        entry1.place(x=609, y=570, width=259, height=32)

        self.make.window.mainloop()
        return None

    def show_delete_user2(self):  # Invalid name or email
        background = self.make.make_background("background21.png")

        b0_image = PhotoImage(file=self.make.relative_to_assets("deleteuser.png"))
        b0 = Button(
            image=b0_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.delete_user(entry0.get(), entry1.get()),
            relief="flat",
        )
        b0.place(x=625, y=644, width=190, height=44)

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        b5, b5.image = self.make.make_buton("back.png", self.switch_to_operator_menu)
        b5.place(x=41, y=17, width=90, height=93)

        entry0, entry0.image = self.make.make_entry("img_textBox0.png", 738.5, 513.0)
        entry0.place(x=609, y=496, width=259, height=32)

        entry1, entry1.image = self.make.make_entry("img_textBox1.png", 738.5, 587.0)
        entry1.place(x=609, y=570, width=259, height=32)

        self.make.window.mainloop()
        return None

    def show_delete_user3(self):  # succ delete user
        background = self.make.make_background("background19.png")

        b4, b4.image = self.make.make_buton("home.png", self.back_to_main)
        b4.place(x=1315, y=17, width=90, height=93)

        b5, b5.image = self.make.make_buton("back.png", self.switch_to_operator_menu)
        b5.place(x=41, y=17, width=90, height=93)

        self.make.window.mainloop()
        return None

    # END#

    ### Show Report
    def show_report(self):
        self.make.window.destroy()

        ws = Tk()
        ws.title("Report")
        ws.geometry("1080x720")
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#FFB800",
            foreground="black",
            rowheight=50,
            fieldbackground="#D3D3D3",
        )
        tv = ttk.Treeview(ws)
        tv["columns"] = ("User_Id", "Name", "Email", "Last_Pickup")
        tv.column("#0", width=0, stretch=NO)
        column = ["User_Id", "Name", "Email", "Last_Pickup"]
        for col in column:
            tv.column(col, anchor=CENTER, width=250)
        tv.heading("#0", text="", anchor=CENTER)
        for heading in column:
            tv.heading(heading, text=heading, anchor=CENTER)
        l = self.service.get_all_users()
        tv.tag_configure("oddrow", background="white")
        tv.tag_configure("evenrow", background="lightblue")
        for i, dtos in enumerate(l):
            if i % 2 == 0:
                tv.insert(
                    parent="",
                    index=i,
                    iid=i,
                    text="",
                    values=(
                        l[dtos].id,
                        l[dtos].name,
                        l[dtos].email,
                        l[dtos].last_pickup,
                    ),
                    tags=("evenrow",),
                )
            else:
                tv.insert(
                    parent="",
                    index=i,
                    iid=i,
                    text="",
                    values=(
                        l[dtos].id,
                        l[dtos].name,
                        l[dtos].email,
                        l[dtos].last_pickup,
                    ),
                    tags=("oddrow",),
                )
        tv.pack(pady=20)

        b4_image = PhotoImage(file=self.make.relative_to_assets("home2.png"))
        b4 = Button(
            image=b4_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.switch_to_main_from_report(ws),
            relief="flat",
        )
        b4.place(x=950, y=570)

        b5_image = PhotoImage(file=self.make.relative_to_assets("back2.png"))
        b5 = Button(
            image=b5_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.switch_to_operator_mode_from_report(ws),
            relief="flat",
        )
        b5.place(x=30, y=570)

        b6_image = PhotoImage(file=self.make.relative_to_assets("report2.png"))
        b6 = Button(
            image=b6_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.show_chart(),
            relief="flat",
        )
        b6.place(x=490, y=570)

        ws.mainloop()

    # END#

    def run(self, dbinit):
        self.service.db_init(dbinit)  # Initialize database

        self.show_main01()  # Show UI
