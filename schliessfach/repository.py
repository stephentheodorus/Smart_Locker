import sqlite3

from kink import inject
from .dto import *

db_file = r"/Users/Steven/proyek_UAS/immerverloren"

### Real Repository
@inject
class BoxRepository:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)

    def init(self, dbinit=False):
        if dbinit == False:
            return
        elif dbinit == True:
            c = self.conn.cursor()

            drop_user = """
            DROP TABLE IF EXISTS user
            """
            drop_operator = """
            DROP TABLE IF EXISTS operator
            """
            drop_transactions = """
            DROP TABLE IF EXISTS transactions
            """
            drop_transactions_detail = """
            DROP TABLE IF EXISTS transactions_detail
            """
            drop_item = """
            DROP TABLE IF EXISTS item
            """
            drop_locker = """
            DROP TABLE IF EXISTS locker
            """

            c.execute(drop_user)
            c.execute(drop_operator)
            c.execute(drop_transactions)
            c.execute(drop_transactions_detail)
            c.execute(drop_item)
            c.execute(drop_locker)

            self.conn.commit()

            self.create_all_tables()  # Create all tables
            self.insert_locker_data()  # Insert locker data
            self.insert_items_data()  # Insert items data
            self.insert_operator_data()  # Insert operator data

    ### This is table and data creation for dbinit = True
    def create_all_tables(self):
        c = self.conn.cursor()

        create_user = """
            CREATE TABLE user(
            id TEXT NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL, password TEXT NOT NULL, last_pickup TEXT)
        """

        c.execute(create_user)

        create_operator = """
            CREATE TABLE operator(
            op_id TEXT PRIMARY KEY,
            op_name TEXT NOT NULL,
            op_pass TEXT NOT NULL)
        """

        c.execute(create_operator)

        create_item = """
                    CREATE TABLE item(
                    item_id TEXT NOT NULL PRIMARY KEY,
                    item_type TEXT NOT NULL)
                """

        c.execute(create_item)

        create_locker = """
                    CREATE TABLE locker(
                    locker_id INTEGER PRIMARY KEY,
                    locker_size TEXT NOT NULL,
                    is_occupied INTEGER NOT NULL DEFAULT 0
                    );
                """

        c.execute(create_locker)

        create_transactions = """
            CREATE TABLE transactions(
            trans_id TEXT NOT NULL PRIMARY KEY,
            id TEXT NOT NULL,
            time_in TEXT NOT NULL,
            time_out TEXT,
            FOREIGN KEY(id) REFERENCES user(id))
        """

        c.execute(create_transactions)

        create_transactions_detail = """
            CREATE TABLE transactions_detail(
            trans_id TEXT NOT NULL,
            locker_id INTEGER NOT NULL,
            item_id TEXT NOT NULL,
            item_size TEXT NOT NULL,
            verification TEXT NOT NULL,
            FOREIGN KEY(trans_id) REFERENCES transactions(trans_id),
            FOREIGN KEY(locker_id) REFERENCES locker(locker_id),
            FOREIGN KEY(item_id) REFERENCES item(item_id))
        """

        c.execute(create_transactions_detail)

        self.conn.commit()

    def insert_locker_data(self):
        c = self.conn.cursor()

        for i in range(1, 9):
            add_locker = """
                insert into locker values(?, ?, ?)
                """

            if 1 <= i <= 4:
                c.execute(
                    add_locker,
                    (
                        i,
                        "KECIL",
                        0,
                    ),
                )
            elif i == 5 or i == 6:
                c.execute(
                    add_locker,
                    (
                        i,
                        "SEDANG",
                        0,
                    ),
                )
            else:
                c.execute(
                    add_locker,
                    (
                        i,
                        "BESAR",
                        0,
                    ),
                )

        self.conn.commit()

    def insert_items_data(self):
        c = self.conn.cursor()

        insert_apparels = """
            insert into item values(?, ?)
            """
        c.execute(
            insert_apparels,
            (
                "I-01",
                "APPARELS",
            ),
        )

        insert_snacks = """
            insert into item values(?, ?)
            """
        c.execute(
            insert_snacks,
            (
                "I-02",
                "SNACKS",
            ),
        )

        insert_skincare = """
            insert into item values(?, ?)
            """
        c.execute(
            insert_skincare,
            (
                "I-03",
                "SKINCARE",
            ),
        )

        insert_electronics = """
            insert into item values(?, ?)
            """
        c.execute(
            insert_electronics,
            (
                "I-04",
                "ELECTRONICS",
            ),
        )

        self.conn.commit()

    def insert_operator_data(self):
        c = self.conn.cursor()

        insert_operator = """
            insert into operator values(?, ?, ?)
            """

        c.execute(
            insert_operator,
            (
                "OP-01",
                "Stephen",
                "op123456",
            ),
        )

        self.conn.commit()

    # END#

    ### Register a new operator
    def register_op(self, op_name, op_id, op_pass):
        c = self.conn.cursor()

        add_op = """
            insert into operator values(?, ?, ?)
        """

        c.execute(
            add_op,
            (
                op_id,
                op_name,
                op_pass,
            ),
        )
        self.conn.commit()

    # END#

    ### Register new user
    def register(self, id, name, email, password):
        c = self.conn.cursor()

        add_user = """
        insert into user(id, name, email, password) values(?, ?, ?, ?)
        """

        c.execute(
            add_user,
            (
                id,
                name,
                email,
                password,
            ),
        )
        self.conn.commit()

    # END#

    ### Unregister a user
    def unregister(self, id):
        c = self.conn.cursor()

        remove_user = """
        DELETE FROM user
              WHERE id = ?
        """

        c.execute(remove_user, (id,))
        self.conn.commit()

    # END#

    ### Get all users and their data and send it as DTOs
    def get_all_users(self):
        c = self.conn.cursor()

        get_all = """
            SELECT *
            FROM user
        """

        c.execute(get_all)
        rows = c.fetchall()

        returned_dto = {}
        for i in rows:
            user = UserDTO(i[0], i[1], i[2], i[4])
            returned_dto[i[0]] = user

        return returned_dto

    # END#

    ### Search transaction by transaction id
    def search_trans_by_trans_id(self, trans_id):
        c = self.conn.cursor()

        search_trans = """
            SELECT *
              FROM transactions
             WHERE trans_id = ?
            """

        c.execute(search_trans, (trans_id,))
        rows = c.fetchall()

        if len(rows) == 0:
            return False
        else:
            return rows[0]

    # END#

    ### Search user by id
    def search_by_id(self, id):
        c = self.conn.cursor()

        search_user = """
            SELECT *
              FROM user
             WHERE id = ?
            """

        c.execute(search_user, (id,))
        rows = c.fetchall()

        if len(rows) == 0:
            return False
        else:
            return rows[0]

    # END#

    ### Search user by email
    def search_user_by_email(self, email):
        c = self.conn.cursor()

        search_user = """
            SELECT *
              FROM user
             WHERE email = ?
        """

        c.execute(search_user, (email,))
        rows = c.fetchall()

        if len(rows) == 0:
            return False
        else:
            return rows[0]

    # END#

    ### Search target locker by locker id
    def search_target_locker(self, locker_id):
        c = self.conn.cursor()

        search_locker = """
            SELECT *
              FROM locker
             WHERE locker_id = ?
            """

        c.execute(search_locker, (locker_id,))
        rows = c.fetchall()

        if len(rows) == 0:
            return False
        else:
            return rows[0]

    # END#

    ### This is for retrieving package purposes
    def search_incomplete_transaction_by_locker_id(self, locker_id):
        c = self.conn.cursor()

        search_incomplete_trans_by_locker_id = """
            SELECT transactions.*
              FROM transactions INNER JOIN transactions_detail ON transactions.trans_id = transactions_detail.trans_id
             WHERE transactions_detail.locker_id = ? AND transactions.time_out IS NULL
            """

        c.execute(search_incomplete_trans_by_locker_id, (locker_id,))
        rows = c.fetchall()

        if len(rows) == 0:
            return False
        else:
            return rows[0]

    # END#

    ### Completing transaction, meaning that package has been retrieved
    def complete_transaction(self, id, locker_id, trans_id, time_out):
        c = self.conn.cursor()

        ### Update the transaction
        update_transaction = """
            UPDATE transactions
               SET time_out = ?
             WHERE trans_id = ?
        """

        c.execute(
            update_transaction,
            (
                time_out,
                trans_id,
            ),
        )
        # END#

        ### Update locker availability
        update_locker = """
            UPDATE locker
               SET is_occupied = 0
             WHERE locker_id = ?
            """

        c.execute(update_locker, (locker_id,))
        # END#

        ### Update user last pickup
        update_last_pickup = """
            UPDATE user
               SET last_pickup = ?
             WHERE id = ?
        """

        c.execute(
            update_last_pickup,
            (
                time_out,
                id,
            ),
        )
        # END#

        self.conn.commit()

    # END#

    ### Get available locker by size
    def get_available_locker_by_size(self, locker_size):
        c = self.conn.cursor()

        search_locker = """
            SELECT *
              FROM locker
             WHERE locker_size = ? AND is_occupied = 0
        """
        c.execute(search_locker, (locker_size,))
        rows = c.fetchall()

        return rows

    # END#

    ### Add data when storing new package to locker
    def store_package_update(
        self, trans_id, id, item_type, item_size, locker_id, time_in, verification
    ):
        c = self.conn.cursor()

        ### Update locker data
        update_locker = """
            UPDATE locker
               SET is_occupied = 1
             WHERE locker_id = ?
        """
        c.execute(update_locker, (locker_id,))
        # END#

        ### Add new transaction
        add_transaction = """
            INSERT INTO transactions(trans_id, id, time_in) values(?, ?, ?)
        """
        c.execute(
            add_transaction,
            (
                trans_id,
                id,
                time_in,
            ),
        )
        # END#

        ### Add transaction detail
        search_item_id = self.search_item_id_by_item_type(item_type)

        add_transaction_detail = """
            INSERT INTO transactions_detail values(?, ?, ?, ?, ?)
        """
        c.execute(
            add_transaction_detail,
            (
                trans_id,
                locker_id,
                search_item_id,
                item_size,
                verification,
            ),
        )
        # END#

        self.conn.commit()

    # END#

    ### Search item id by item type
    def search_item_id_by_item_type(self, item_type):
        c = self.conn.cursor()

        search_item_id = """
            SELECT *
              FROM item
             WHERE item_type = ?
        """

        c.execute(search_item_id, (item_type,))
        rows = c.fetchall()

        return rows[0][0]

    # END#

    ### Search transaction detail by locker id
    def search_trans_detail_by_locker_id(self, locker_id, trans_id):
        c = self.conn.cursor()

        search_trans_detail = """
            SELECT *
              FROM transactions_detail
             WHERE locker_id = ? AND trans_id = ?
        """

        c.execute(
            search_trans_detail,
            (
                locker_id,
                trans_id,
            ),
        )
        rows = c.fetchall()

        return rows[0]

    # END#

    ### Search user name and the email with incomplete transactions
    def search_user_name_and_email_with_incomplete_transactions(self):
        c = self.conn.cursor()

        search_transaction = """
            SELECT user.name, user.email
              FROM transactions INNER JOIN user ON transactions.id = user.id
             WHERE time_out IS NULL
             GROUP BY transactions.id
        """

        c.execute(search_transaction)
        rows = c.fetchall()

        return rows

    # END#

    ### Search empty locker
    def search_empty_locker(self):
        c = self.conn.cursor()

        search_empty_locker = """
            SELECT *
              FROM locker
             WHERE is_occupied = 0
        """

        c.execute(search_empty_locker)
        rows = c.fetchall()

        return rows

    # END#

    ### Search operator by operator id
    def search_operator_by_id(self, op_id):
        c = self.conn.cursor()

        search_op = """
            SELECT *
              FROM operator
             WHERE op_id = ?
        """

        c.execute(search_op, (op_id,))
        rows = c.fetchall()

        if len(rows) == 0:
            return False
        else:
            return rows[0]

    # END#

    ### Search average keep time for every items
    def search_avg_keep_time_for_every_items(self):
        c = self.conn.cursor()

        search_avg_time = """
            SELECT item.item_type, AVG(ROUND((JULIANDAY(time_out) - JULIANDAY(time_in))*1440,2)) as avg_time
            FROM item INNER JOIN transactions_detail on item.item_id = transactions_detail.item_id
            INNER JOIN transactions on transactions.trans_id = transactions_detail.trans_id
            GROUP BY item.item_type
        """

        c.execute(search_avg_time)
        rows = c.fetchall()

        returned_dto = {}
        for i in rows:
            dto = AvgItemTypeTimeDTO(i[0], i[1])
            returned_dto[i[0]] = dto

        return returned_dto

    # END#

    ### Search average keep time for every item size
    def search_avg_keep_time_for_every_item_size(self):
        c = self.conn.cursor()

        search_avg_time = """
            SELECT transactions_detail.item_size as item_size, AVG(ROUND((JULIANDAY(time_out) - JULIANDAY(time_in))*1440,2)) as avg_time
            FROM item INNER JOIN transactions_detail on item.item_id = transactions_detail.item_id
            INNER JOIN transactions on transactions.trans_id = transactions_detail.trans_id
            GROUP BY transactions_detail.item_size
        """

        c.execute(search_avg_time)
        rows = c.fetchall()

        returned_dto = {}
        for i in rows:
            dto = AvgItemSizeTimeDTO(i[0], i[1])
            returned_dto[i[0]] = dto

        return returned_dto

    # END#

    ### Search average keep time for every item size and item type
    def search_avg_keep_time_for_every_item_size_and_item_type(self):
        c = self.conn.cursor()

        search_avg_time = """
            SELECT item.item_type as item_type, transactions_detail.item_size as item_size, AVG(ROUND((JULIANDAY(time_out) - JULIANDAY(time_in))*1440,2)) as avg_time
            FROM item INNER JOIN transactions_detail on item.item_id = transactions_detail.item_id
            INNER JOIN transactions on transactions.trans_id = transactions_detail.trans_id
            GROUP BY transactions_detail.item_size AND item.item_type
        """

        c.execute(search_avg_time)
        rows = c.fetchall()

        return rows

    # END#


# END#


### Mock Repository
class MockRepository:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)

    def init(self, dbinit=False):
        if dbinit == False:
            return
        elif dbinit == True:
            c = self.conn.cursor()

            drop_user = """
            DROP TABLE IF EXISTS user
            """
            drop_operator = """
            DROP TABLE IF EXISTS operator
            """
            drop_transactions = """
            DROP TABLE IF EXISTS transactions
            """
            drop_transactions_detail = """
            DROP TABLE IF EXISTS transactions_detail
            """
            drop_item = """
            DROP TABLE IF EXISTS item
            """
            drop_locker = """
            DROP TABLE IF EXISTS locker
            """

            c.execute(drop_user)
            c.execute(drop_operator)
            c.execute(drop_transactions)
            c.execute(drop_transactions_detail)
            c.execute(drop_item)
            c.execute(drop_locker)

            self.conn.commit()

            self.create_all_tables()  # Create all tables
            self.insert_locker_data()  # Insert locker data
            self.insert_items_data()  # Insert items data
            self.insert_operator_data()  # Insert operator data

    ### This is table and data creation for dbinit = True
    def create_all_tables(self):
        c = self.conn.cursor()

        create_user = """
            CREATE TABLE user(
            id TEXT NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL, password TEXT NOT NULL, last_pickup TEXT)
        """

        c.execute(create_user)

        create_operator = """
            CREATE TABLE operator(
            op_id TEXT PRIMARY KEY,
            op_name TEXT NOT NULL,
            op_pass TEXT NOT NULL)
        """

        c.execute(create_operator)

        create_item = """
                    CREATE TABLE item(
                    item_id TEXT NOT NULL PRIMARY KEY,
                    item_type TEXT NOT NULL)
                """

        c.execute(create_item)

        create_locker = """
                    CREATE TABLE locker(
                    locker_id INTEGER PRIMARY KEY,
                    locker_size TEXT NOT NULL,
                    is_occupied INTEGER NOT NULL DEFAULT 0
                    );
                """

        c.execute(create_locker)

        create_transactions = """
            CREATE TABLE transactions(
            trans_id TEXT NOT NULL PRIMARY KEY,
            id TEXT NOT NULL,
            time_in TEXT NOT NULL,
            time_out TEXT,
            FOREIGN KEY(id) REFERENCES user(id))
        """

        c.execute(create_transactions)

        create_transactions_detail = """
            CREATE TABLE transactions_detail(
            trans_id TEXT NOT NULL,
            locker_id INTEGER NOT NULL,
            item_id TEXT NOT NULL,
            item_size TEXT NOT NULL,
            verification TEXT NOT NULL,
            FOREIGN KEY(trans_id) REFERENCES transactions(trans_id),
            FOREIGN KEY(locker_id) REFERENCES locker(locker_id),
            FOREIGN KEY(item_id) REFERENCES item(item_id))
        """

        c.execute(create_transactions_detail)

        self.conn.commit()

    def insert_locker_data(self):
        c = self.conn.cursor()

        for i in range(1, 9):
            add_locker = """
                insert into locker values(?, ?, ?)
                """

            if 1 <= i <= 4:
                c.execute(
                    add_locker,
                    (
                        i,
                        "KECIL",
                        0,
                    ),
                )
            elif i == 5 or i == 6:
                c.execute(
                    add_locker,
                    (
                        i,
                        "SEDANG",
                        0,
                    ),
                )
            else:
                c.execute(
                    add_locker,
                    (
                        i,
                        "BESAR",
                        0,
                    ),
                )

        self.conn.commit()

    def insert_items_data(self):
        c = self.conn.cursor()

        insert_apparels = """
            insert into item values(?, ?)
            """
        c.execute(
            insert_apparels,
            (
                "I-01",
                "APPARELS",
            ),
        )

        insert_snacks = """
            insert into item values(?, ?)
            """
        c.execute(
            insert_snacks,
            (
                "I-02",
                "SNACKS",
            ),
        )

        insert_skincare = """
            insert into item values(?, ?)
            """
        c.execute(
            insert_skincare,
            (
                "I-03",
                "SKINCARE",
            ),
        )

        insert_electronics = """
            insert into item values(?, ?)
            """
        c.execute(
            insert_electronics,
            (
                "I-04",
                "ELECTRONICS",
            ),
        )

        self.conn.commit()

    def insert_operator_data(self):
        c = self.conn.cursor()

        insert_operator = """
            insert into operator values(?, ?, ?)
            """

        c.execute(
            insert_operator,
            (
                "OP-01",
                "Stephen",
                "op123456",
            ),
        )

        self.conn.commit()

    # END#

    ### Register a new operator
    def register_op(self, op_name, op_id, op_pass):
        c = self.conn.cursor()

        add_op = """
            insert into operator values(?, ?, ?)
        """

        c.execute(
            add_op,
            (
                op_id,
                op_name,
                op_pass,
            ),
        )

    # END#

    ### Register new user
    def register(self, id, name, email, password):
        c = self.conn.cursor()

        add_user = """
        insert into user(id, name, email, password) values(?, ?, ?, ?)
        """

        c.execute(
            add_user,
            (
                id,
                name,
                email,
                password,
            ),
        )

    # END#

    ### Unregister a user
    def unregister(self, id):
        c = self.conn.cursor()

        remove_user = """
        DELETE FROM user
              WHERE id = ?
        """

        c.execute(remove_user, (id,))

    # END#

    ### Get all users and their data and send it as DTOs
    def get_all_users(self):
        c = self.conn.cursor()

        get_all = """
            SELECT *
            FROM user
        """

        c.execute(get_all)
        rows = c.fetchall()

        returned_dto = {}
        for i in rows:
            user = UserDTO(i[0], i[1], i[2], i[4])
            returned_dto[i[0]] = user

        return returned_dto

    # END#

    ### Search transaction by transaction id
    def search_trans_by_trans_id(self, trans_id):
        c = self.conn.cursor()

        search_trans = """
            SELECT *
              FROM transactions
             WHERE trans_id = ?
            """

        c.execute(search_trans, (trans_id,))
        rows = c.fetchall()

        if len(rows) == 0:
            return False
        else:
            return rows[0]

    # END#

    ### Search user by id
    def search_by_id(self, id):
        c = self.conn.cursor()

        search_user = """
            SELECT *
              FROM user
             WHERE id = ?
            """

        c.execute(search_user, (id,))
        rows = c.fetchall()

        if len(rows) == 0:
            return False
        else:
            return rows[0]

    # END#

    ### Search user by email
    def search_user_by_email(self, email):
        c = self.conn.cursor()

        search_user = """
            SELECT *
              FROM user
             WHERE email = ?
        """

        c.execute(search_user, (email,))
        rows = c.fetchall()

        if len(rows) == 0:
            return False
        else:
            return rows[0]

    # END#

    ### Search target locker by locker id
    def search_target_locker(self, locker_id):
        c = self.conn.cursor()

        search_locker = """
            SELECT *
              FROM locker
             WHERE locker_id = ?
            """

        c.execute(search_locker, (locker_id,))
        rows = c.fetchall()

        if len(rows) == 0:
            return False
        else:
            return rows[0]

    # END#

    ### This is for retrieving package purposes
    def search_incomplete_transaction_by_locker_id(self, locker_id):
        c = self.conn.cursor()

        search_incomplete_trans_by_locker_id = """
            SELECT transactions.*
              FROM transactions INNER JOIN transactions_detail ON transactions.trans_id = transactions_detail.trans_id
             WHERE transactions_detail.locker_id = ? AND transactions.time_out IS NULL
            """

        c.execute(search_incomplete_trans_by_locker_id, (locker_id,))
        rows = c.fetchall()

        if len(rows) == 0:
            return False
        else:
            return rows[0]

    # END#

    ### Completing transaction, meaning that package has been retrieved
    def complete_transaction(self, id, locker_id, trans_id, time_out):
        c = self.conn.cursor()

        ### Update the transaction
        update_transaction = """
            UPDATE transactions
               SET time_out = ?
             WHERE trans_id = ?
        """

        c.execute(
            update_transaction,
            (
                time_out,
                trans_id,
            ),
        )
        # END#

        ### Update locker availability
        update_locker = """
            UPDATE locker
               SET is_occupied = 0
             WHERE locker_id = ?
            """

        c.execute(update_locker, (locker_id,))
        # END#

        ### Update user last pickup
        update_last_pickup = """
            UPDATE user
               SET last_pickup = ?
             WHERE id = ?
        """

        c.execute(
            update_last_pickup,
            (
                time_out,
                id,
            ),
        )
        # END#

    # END#

    ### Get available locker by size
    def get_available_locker_by_size(self, locker_size):
        c = self.conn.cursor()

        search_locker = """
            SELECT *
              FROM locker
             WHERE locker_size = ? AND is_occupied = 0
        """
        c.execute(search_locker, (locker_size,))
        rows = c.fetchall()

        return rows

    # END#

    ### Add data when storing new package to locker
    def store_package_update(
        self, trans_id, id, item_type, item_size, locker_id, time_in, verification
    ):
        c = self.conn.cursor()

        ### Update locker data
        update_locker = """
            UPDATE locker
               SET is_occupied = 1
             WHERE locker_id = ?
        """
        c.execute(update_locker, (locker_id,))
        # END#

        ### Add new transaction
        add_transaction = """
            INSERT INTO transactions(trans_id, id, time_in) values(?, ?, ?)
        """
        c.execute(
            add_transaction,
            (
                trans_id,
                id,
                time_in,
            ),
        )
        # END#

        ### Add transaction detail
        search_item_id = self.search_item_id_by_item_type(item_type)

        add_transaction_detail = """
            INSERT INTO transactions_detail values(?, ?, ?, ?, ?)
        """
        c.execute(
            add_transaction_detail,
            (
                trans_id,
                locker_id,
                search_item_id,
                item_size,
                verification,
            ),
        )
        # END#

    # END#

    ### Search item id by item type
    def search_item_id_by_item_type(self, item_type):
        c = self.conn.cursor()

        search_item_id = """
            SELECT *
              FROM item
             WHERE item_type = ?
        """

        c.execute(search_item_id, (item_type,))
        rows = c.fetchall()

        return rows[0][0]

    # END#

    ### Search transaction detail by locker id
    def search_trans_detail_by_locker_id(self, locker_id, trans_id):
        c = self.conn.cursor()

        search_trans_detail = """
            SELECT *
              FROM transactions_detail
             WHERE locker_id = ? AND trans_id = ?
        """

        c.execute(
            search_trans_detail,
            (
                locker_id,
                trans_id,
            ),
        )
        rows = c.fetchall()

        return rows[0]

    # END#

    ### Search user name and the email with incomplete transactions
    def search_user_name_and_email_with_incomplete_transactions(self):
        c = self.conn.cursor()

        search_transaction = """
            SELECT user.name, user.email
              FROM transactions INNER JOIN user ON transactions.id = user.id
             WHERE time_out IS NULL
             GROUP BY transactions.id
        """

        c.execute(search_transaction)
        rows = c.fetchall()

        return rows

    # END#

    ### Search empty locker
    def search_empty_locker(self):
        c = self.conn.cursor()

        search_empty_locker = """
            SELECT *
              FROM locker
             WHERE is_occupied = 0
        """

        c.execute(search_empty_locker)
        rows = c.fetchall()

        return rows

    # END#

    ### Search operator by operator id
    def search_operator_by_id(self, op_id):
        c = self.conn.cursor()

        search_op = """
            SELECT *
              FROM operator
             WHERE op_id = ?
        """

        c.execute(search_op, (op_id,))
        rows = c.fetchall()

        if len(rows) == 0:
            return False
        else:
            return rows[0]

    # END#

    ### Search average keep time for every items
    def search_avg_keep_time_for_every_items(self):
        c = self.conn.cursor()

        search_avg_time = """
            SELECT item.item_type, AVG(ROUND((JULIANDAY(time_out) - JULIANDAY(time_in))*1440,2)) as avg_time
            FROM item INNER JOIN transactions_detail on item.item_id = transactions_detail.item_id
            INNER JOIN transactions on transactions.trans_id = transactions_detail.trans_id
            GROUP BY item.item_type
        """

        c.execute(search_avg_time)
        rows = c.fetchall()

        returned_dto = {}
        for i in rows:
            dto = AvgItemTypeTimeDTO(i[0], i[1])
            returned_dto[i[0]] = dto

        return returned_dto

    # END#

    ### Search average keep time for every item size
    def search_avg_keep_time_for_every_item_size(self):
        c = self.conn.cursor()

        search_avg_time = """
            SELECT transactions_detail.item_size as item_size, AVG(ROUND((JULIANDAY(time_out) - JULIANDAY(time_in))*1440,2)) as avg_time
            FROM item INNER JOIN transactions_detail on item.item_id = transactions_detail.item_id
            INNER JOIN transactions on transactions.trans_id = transactions_detail.trans_id
            GROUP BY transactions_detail.item_size
        """

        c.execute(search_avg_time)
        rows = c.fetchall()

        returned_dto = {}
        for i in rows:
            dto = AvgItemSizeTimeDTO(i[0], i[1])
            returned_dto[i[0]] = dto

        return returned_dto

    # END#

    ### Search average keep time for every item size and item type
    def search_avg_keep_time_for_every_item_size_and_item_type(self):
        c = self.conn.cursor()

        search_avg_time = """
            SELECT item.item_type as item_type, transactions_detail.item_size as item_size, AVG(ROUND((JULIANDAY(time_out) - JULIANDAY(time_in))*1440,2)) as avg_time
            FROM item INNER JOIN transactions_detail on item.item_id = transactions_detail.item_id
            INNER JOIN transactions on transactions.trans_id = transactions_detail.trans_id
            GROUP BY transactions_detail.item_size AND item.item_type
        """

        c.execute(search_avg_time)
        rows = c.fetchall()

        return rows

    # END#


# END#
