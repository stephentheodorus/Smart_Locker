import string
import re
from kink import inject, di
from .lock import *
from .repository import *
from .observer import *
import random
from datetime import datetime


@inject
class BoxService:
    def __init__(
        self,
        repository: BoxRepository,
        lock: BoxLock,
        user_subject: UserSubject,
        locker_subject: LockerSubject,
    ):
        self.repository = repository
        self.user_subject = user_subject
        self.locker_subject = locker_subject
        self.lock = lock

    ### Initialize database (True or False)
    def db_init(self, dbinit):
        self.repository.init(dbinit)

    # END#

    ### User log in
    def log_in(self, id, password):
        search_user = self.repository.search_by_id(id)

        if search_user == False:
            return "WRONG ID OR PASSWORD"
        elif id == search_user[0] and password == search_user[3]:
            return True

    # END#

    ### Operator log in
    def op_log_in(self, op_id, op_pass):
        search_op = self.repository.search_operator_by_id(op_id)

        if search_op == False:
            return False
        elif op_pass != search_op[2]:
            return False

        return True

    # END#

    ### Register a new operator
    def register_op(self, op_name, op_id, op_pass):
        if len(op_pass) < 8:
            return "PASSWORD TOO SHORT"

        verify = self.check_op_id_validity(op_id)

        if verify == True:  # ID taken
            return False
        else:  # Successful
            self.repository.register_op(op_name, op_id, op_pass)
            return True

    # END

    ### Register a new user
    def register(self, name, email, password):
        ### Check email validity
        check_email = self.check_email_validity(email)

        if check_email == True:
            return "EMAIL HAS BEEN USED"
        elif check_email == False:
            pass
        else:
            return "INVALID EMAIL"
        # END#

        ### Password must be at least 8 characters
        if len(password) < 8:
            return "PASSWORD TOO SHORT"
        # END#

        ### Generate new id and search if generated id has been used or not
        new_id = self.create_id()
        search = self.repository.search_by_id(new_id)

        while True:
            if search == False:
                break
            else:
                new_id = self.create_id()
                search = self.repository.search_by_id(new_id)
        # END#

        self.repository.register(new_id, name, email, password)
        self.send_email_to_new_user(new_id, name, email)
        return True

    # END#

    ### Unregister/delete a user
    def unregister(self, name, email):
        search = self.repository.search_user_by_email(email)

        if search == False:  # Invalid email
            return False
        elif name == search[1]:  # Successful
            self.repository.unregister(search[0])
            return True
        else:
            return False

    # END#

    ### Retrieve a package from a locker
    def retrieve_package(self, id, locker_id, verification):
        verify = self.retrieve_package_verify(id, locker_id, verification)

        if verify == True:
            search_trans = self.repository.search_incomplete_transaction_by_locker_id(
                locker_id
            )
            cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.repository.complete_transaction(
                id, locker_id, search_trans[0], cur_time
            )
            return True
        else:
            return verify
        # END#

    # END#

    ### Store new package to locker
    def store_package(self, id, item_type, item_size):
        verify = self.store_package_verify(id, item_size)

        if verify == False:  # Wrong ID input
            return False
        elif verify == "NO LOCKER AVAILABLE":
            return verify

        ### Insert new data to database
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        verification = self.create_verification()  # Create new verification code

        ### Create a new transaction id, then check if it has been used or not
        trans_id = self.create_transaction_id()  # Create new transaction id
        verify_trans_id = self.repository.search_trans_by_trans_id(
            trans_id
        )  # Check if trans_id has been used or not
        while True:  # Loop: if transaction id has been used, create new one again
            if verify_trans_id == False:
                break
            else:
                trans_id = self.create_transaction_id()
                verify_trans_id = self.repository.search_trans_by_trans_id(trans_id)
        # END#

        self.repository.store_package_update(
            trans_id, id, item_type, item_size, verify, cur_time, verification
        )  # Insert new transaction data

        ### Send emails
        search_user_details = self.repository.search_by_id(id)

        self.notify_new_package_to_user(
            search_user_details[2],
            search_user_details[1],
            verify,
            item_type,
            item_size,
            verification,
        )
        self.check_if_one_empty_locker_left()
        return verify
        # END#

        # END#

    # END#

    ### Search available locker by size
    def search_available_locker_by_size(self, item_size):
        search_locker = ""

        if item_size == "KECIL":
            search_locker = self.repository.get_available_locker_by_size("KECIL")
            if len(search_locker) == 0:
                search_locker += self.repository.get_available_locker_by_size("SEDANG")
                if len(search_locker) == 0:
                    search_locker += self.repository.get_available_locker_by_size(
                        "BESAR"
                    )
        elif item_size == "SEDANG":
            search_locker = self.repository.get_available_locker_by_size("SEDANG")
            if len(search_locker) == 0:
                search_locker += self.repository.get_available_locker_by_size("BESAR")
        elif item_size == "BESAR":
            search_locker = self.repository.get_available_locker_by_size("BESAR")
        else:
            return "INVALID SIZE"

        return search_locker

    # END#

    ### Check email validity when registering
    def check_email_validity(self, email):
        ### Check if email input is in email format or not
        regex = "^[a-z0-9]+[\.__]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

        if re.search(regex, email):
            pass
        else:
            return "INVALID EMAIL"
        # END#

        ### Check if email has been used or not
        search_user_by_email = self.repository.search_user_by_email(email)

        if search_user_by_email == False:
            return False
        else:
            return True
        # END#

    # END#

    def check_op_id_validity(self, op_id):
        search = self.repository.search_operator_by_id(op_id)

        if search == False:
            return False  # Operator id is still available
        else:
            return True  # Not available

    ### Send email to new user
    def send_email_to_new_user(self, id, name, email):
        self.user_subject.notify(NewUserMessage(id, name, email))

    # END#

    ### Notify to user for their new package
    def notify_new_package_to_user(
        self, email, name, locker_id, item_type, item_size, verification
    ):
        self.locker_subject.notify(
            NewPackageMessage(
                email, name, locker_id, item_type, item_size, verification
            )
        )

    # END#

    ### Get all users
    def get_all_users(self):
        return self.repository.get_all_users()

    # END#

    ### Check if there is only one empty locker left
    def check_if_one_empty_locker_left(self):
        search_empty_locker = self.find_empty_locker()

        if len(search_empty_locker) == 1:
            self.remind_users_to_retrieve_package()

    # END#

    ### Sending an email to remind users to retrieve package
    def remind_users_to_retrieve_package(self):
        search_incomplete_transactions = (
            self.repository.search_user_name_and_email_with_incomplete_transactions()
        )
        self.locker_subject.notify(
            RetrievePackageReminderMessage(search_incomplete_transactions)
        )

    # END#

    ### Verify user data for package retrieval
    def retrieve_package_verify(self, id, locker_id, verification):
        ### Search if locker is empty or not. If not empty, continue below this comment.
        search_locker = self.repository.search_target_locker(locker_id)

        if search_locker == False:
            return "NO LOCKER"  # No such locker
        elif search_locker[2] == 0:
            return "LOCKER EMPTY"
        # END#

        ### Search the incomplete transaction by occupied locker id and then complete the transaction
        search_trans = self.repository.search_incomplete_transaction_by_locker_id(
            locker_id
        )
        search_user = self.repository.search_by_id(id)
        search_trans_detail = self.repository.search_trans_detail_by_locker_id(
            locker_id, search_trans[0]
        )

        if id == search_trans[1] and verification == search_trans_detail[4]:
            return True
        else:
            return "WRONG ID OR VERIFICATION CODE"

    # END#

    ### Verify user id for package delivery
    def store_package_verify(self, id, item_size):
        ### Search if user exists or not by id
        search_user = self.repository.search_by_id(id)
        if search_user == False:
            self.user_subject.notify(WrongIdInputMessage())
            return False
        # END#

        ### Search if there is an available locker
        search_available_locker = self.search_available_locker_by_size(item_size)
        if len(search_available_locker) == 0:
            return "NO LOCKER AVAILABLE"
        else:
            return search_available_locker[0][0]
        # END#

    # END#

    ### Create a verification code
    def create_verification(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # END#

    ### Create an id
    def create_id(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))

    # END#

    ### Search user by id
    def search_by_id(self, id):
        return self.repository.search_by_id(id)

    # END#

    ### Find empty locker
    def find_empty_locker(self):
        return self.repository.search_empty_locker()

    # END#

    ### Search average keep time for every items
    def search_avg_keep_time_for_every_items(self):
        return self.repository.search_avg_keep_time_for_every_items()

    # END#

    ### Search average keep time for every item size
    def search_avg_keep_time_for_every_item_size(self):
        return self.repository.search_avg_keep_time_for_every_item_size()

    # END#

    ### Open locker
    def open_locker(self, locker_id):
        self.lock.unlock(locker_id)

    # END#

    ### Close locker
    def close_locker(self, locker_id):
        self.lock.lock(locker_id)

    # END#

    ### Create random transaction id
    def create_transaction_id(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # END#
