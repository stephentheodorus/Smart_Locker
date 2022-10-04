from service import *
from repository import *
from ui import *

# di["db_file"] = r"/Users/domin/locker_mock"

repo_test = MockRepository(r"/Users/domin/locker_mock")
serv_test = BoxService(repo_test, MockLock(), UserSubject(), LockerSubject())
ui_test = BoxUI(serv_test)

### 1. Mendaftar dan menghapus user
def test_should_return_error_when_registering_existing_user():
    ### Testing an existing user: Dominique, dominokiiro@gmail.com
    register = ui_test.service.register("Dominique", "dominokiiro@gmail.com", "hello123456")

    assert register == 'EMAIL HAS BEEN USED'

def test_should_return_true_when_deleting_existing_user():
    ### Testing an existing user: Dominique, dominokiiro@gmail.com
    delete = ui_test.service.unregister("Dominique", "dominokiiro@gmail.com")

    assert delete == True

def test_should_return_False_when_deleting_non_existing_user():
    delete = ui_test.service.unregister("Dominiq", "dominooo@gmail.com")

    assert delete == False
#END#

### 2. Pengambilan barang
def test_should_return_False_when_retrieving_package_with_invalid_id_and_pass():
    retrieve = ui_test.service.retrieve_package("VB0", 1, "5DIX0")

    assert retrieve == 'WRONG ID OR VERIFICATION CODE'

def test_should_return_true_when_retrieving_package_with_valid_id_and_pass():
    retrieve = ui_test.service.retrieve_package("VB09J", 1, "5DIX0I")

    assert retrieve == True
#END#

### 4. Memasukkan paket kedalam kotak
def test_should_return_false_when_delivering_package_with_invalid_id():
    deliver = ui_test.service.store_package("VB0J", "SNACKS", "KECIL")

    assert deliver == False

def test_should_return_true_when_delivering_package_with_valid_id():
    deliver = ui_test.service.store_package("ABCD02", "SNACKS", "KECIL")

    assert type(deliver) == int
#END#


### 5. Report
def test_should_return_item_type_per_wait_and_item_size_per_wait_graph():
    graph = ui_test.show_chart()
    assert True == graph

