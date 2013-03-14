
#System Imports
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime

#Local Imports
from portcullis.models import Key, PortcullisUser, DataStream, Device, ScalingFunction


class ScalingFunctionManagerTest(TestCase):
    '''
    ' Unit Tests for the portcullis ScalingFunction Manager
    '''

    fixtures = ['test_portcullisUsers.json', 'test_scalingFunctions.json']



    ''''''''''''''''''' get_editable '''''''''''''''''''''''''

    def test_get_editable_normaluser(self):
        '''
        ' Test that a non superuser gets back an empty QuerySet using get_editable from ScalingFunctions
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        scalingFunctions = ScalingFunction.objects.none()

        scalingFuns = ScalingFunction.objects.get_editable(user)
        self.assertEqual(list(scalingFunctions), list(scalingFuns))
   
    def test_get_editable_superuser(self):
        '''
        ' Test that a superuser gets back all scaling functions using get_editable from ScalingFunctions
        '''

        user = PortcullisUser.objects.get(username="superuser")
        scalingFunctions = ScalingFunction.objects.all()

        scalingFuns = ScalingFunction.objects.get_editable(user)
        self.assertEqual(list(scalingFunctions), list(scalingFuns))

    def test_get_editable_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using PortcullisUser's get_editable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, PortcullisUser.objects.get_editable, user=aUser)



    ''''''''''''''''''' get_editable_by_pk '''''''''''''''''''''''''

    def test_get_editable_by_pk_nonSuperUser(self):
        '''
        ' Test that ScalingFunction manager method get_editable_by_pk returns
        ' None when given a non superuser and a scaling function pk.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        sf = ScalingFunction.objects.get(pk = 1)

        self.assertIsNone(ScalingFunction.objects.get_editable_by_pk(user, 1), sf)

    def test_get_editable_by_pk_superuser(self):
        '''
        ' Test that ScalingFunction manager method is_editable_by_user returns
        ' a scaling function when given a superuser and a scaling function pk.
        '''

        user = PortcullisUser.objects.get(username="superuser")
        sf = ScalingFunction.objects.get(pk = 2)

        self.assertEquals(ScalingFunction.objects.get_editable_by_pk(user, 2), sf)

    def test_get_editable_by_pk_nonuser(self):
        '''
        ' Test that ScalingFunction manager method is_editable_by_user returns
        ' a TypeError Exception when given a user that isn't really a portcullis user.
        '''

        bogusUser = "bogusssssss"
        pk = 1

        self.assertRaises(TypeError, ScalingFunction.objects.get_editable_by_pk, user = bogusUser, pk = pk)

    def test_get_editable_by_pk_does_not_exist(self):
        '''
        ' Test that ScalingFunction manager method is_editable_by_user returns
        ' a ScalingFunction.DoesNotExist when given a pk of a non existent scaling function.
        '''

        user = PortcullisUser.objects.get(username="superuser")
        pk = -1

        self.assertRaises(ScalingFunction.DoesNotExist, ScalingFunction.objects.get_editable_by_pk, user = user, pk = pk)


class ScalingFunctionModelTest(TestCase):
    '''
    ' Unit Tests for the portcullis ScalingFunction model
    '''

    fixtures = ['test_portcullisUsers.json', 'test_scalingFunctions.json']

   

    ''''''''''''''''''' is_editable_by_user '''''''''''''''''''''''''

    def test_is_editable_by_user_normaluser(self):
        '''
        ' Test that ScalingFuncitons method is_editable_by_user returns
        ' false when a nonsuper user checks if they can edit a given scaling function.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        sf = ScalingFunction.objects.get(pk = 1)

        self.assertFalse(sf.is_editable_by_user(user))

    def test_is_editable_by_user_superuser(self):
        '''
        ' Test that ScalingFuncitons method is_editable_by_user returns
        ' true when a superuser checks if they can edit a given scaling function.
        '''

        user = PortcullisUser.objects.get(username="superuser")
        sf = ScalingFunction.objects.get(pk = 1)

        self.assertTrue(sf.is_editable_by_user(user))

    def test_is_editable_by_user_nonuser(self):
        '''
        ' Test that ScalingFuncitons method is_editable_by_user returns
        ' a TypeError Exception when given a non user.
        '''

        user = "None User"
        sc = ScalingFunction.objects.get(pk = 1)

        self.assertRaises(TypeError, sc.is_editable_by_user, user = user)



    ''''''''''''''''''' can_view '''''''''''''''''''''''''

    def test_can_view_normaluser(self):
        '''
        ' Test that ScalingFuncitons method can_view returns
        ' true when a nonsuper user checks if they can view a given scaling function.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        sf = ScalingFunction.objects.get(pk = 1)

        self.assertTrue(sf.can_view(user))

    def test_can_view_superuser(self):
        '''
        ' Test that ScalingFuncitons method can_view returns
        ' true when a superuser checks if they can view a given scaling function.
        '''

        user = PortcullisUser.objects.get(username="superuser")
        sf = ScalingFunction.objects.get(pk = 1)

        self.assertTrue(sf.can_view(user))

    def test_can_view_nonuser(self):
        '''
        ' Test that ScalingFuncitons method can_view returns
        ' a TypeError Exception when given a non user.
        '''

        user = "None User"
        sc = ScalingFunction.objects.get(pk = 1)

        self.assertRaises(TypeError, sc.can_view, user = user)
   

class PortcullisUserManagerTest(TestCase):
    '''
    ' Unit Tests for the portcullis PortcullisUser Manager
    '''
    
    fixtures = ['test_portcullisUsers.json']



    ''''''''''''''''''' get_editable '''''''''''''''''''''''''

    def test_get_editable_by_superuser(self):
        '''
        ' Test that a superuser get's all users using get_editable from PortcullisUsers
        '''

        sUser = PortcullisUser.objects.get(username="superuser")
        users = PortcullisUser.objects.all()

        sPortcullisUsers = PortcullisUser.objects.get_editable(sUser)
        self.assertEqual(list(sPortcullisUsers), list(users))
    
    def test_get_editable_by_normal_user(self):
        '''
        ' Test that a non superuser get's only his/her users using get_editable from PortcullisUsers
        '''

        nUser = PortcullisUser.objects.get(username="normaluser")

        nPortcullisUsers = PortcullisUser.objects.get_editable(nUser)
        self.assertEqual([nUser], list(nPortcullisUsers))

    def test_get_editable_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using PortcullisUser's get_editable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, PortcullisUser.objects.get_editable, user=aUser)



    ''''''''''''''''''' get_editable_by_pk '''''''''''''''''''''''''

    def test_get_editable_by_pk_correctUser(self):
        '''
        ' Test that PortcullisUser manager method get_editable_by_pk returns
        ' a portcullis user when given a user and that users pk.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        pk = user.id

        self.assertEquals(PortcullisUser.objects.get_editable_by_pk(user, pk), user)

    def test_get_editable_by_pk_incorrectUser(self):
        '''
        ' Test that PortcullisUser manager method is_editable_by_user returns
        ' None when given a normaluser and some other users pk.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        pk = 2

        self.assertIsNone(PortcullisUser.objects.get_editable_by_pk(user, pk))

    def test_get_editable_by_pk_superuser(self):
        '''
        ' Test that PortcullisUser manager method is_editable_by_user returns
        ' a portcullis user when given a superuser and some other users pk.
        '''

        user = PortcullisUser.objects.get(username="superuser")
        otherUser = PortcullisUser.objects.get(username="normaluser")
        pk = otherUser.pk

        self.assertEquals(PortcullisUser.objects.get_editable_by_pk(user, pk), otherUser)

    def test_get_editable_by_pk_nonuser(self):
        '''
        ' Test that PortcullisUser manager method is_editable_by_user returns
        ' a TypeError Exception when given a user that isn't really a portcullis user.
        '''

        bogusUser = "bogusssssss"
        pk = 1

        self.assertRaises(TypeError, PortcullisUser.objects.get_editable_by_pk, user = bogusUser, pk = pk)

    def test_get_editable_by_pk_does_not_exist(self):
        '''
        ' Test that PortcullisUser manager method is_editable_by_user returns
        ' a PortcullisUser.DoesNotExist when given a pk of a non existent user.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        pk = -1

        self.assertRaises(PortcullisUser.DoesNotExist, PortcullisUser.objects.get_editable_by_pk, user = user, pk = pk)


class PortcullisUserModelTest(TestCase):
    '''
    ' Unit Tests for the portcullis PortcullisUser model
    '''

    fixtures = ['test_portcullisUsers.json']



    ''''''''''''''''''' is_editable_by_user '''''''''''''''''''''''''

    def test_is_editable_by_user_correctUser(self):
        '''
        ' Test that PortcullisUser method is_editable_by_user returns
        ' true when given a user trying to edit itself.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        self.assertTrue(user.is_editable_by_user(user))

    def test_is_editable_by_user_incorrectUser(self):
        '''
        ' Test that PortcullisUser method is_editable_by_user returns
        ' false when a non superuser checks if they can edit another user.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        otherUser = PortcullisUser.objects.get(username="staffuser")

        self.assertFalse(user.is_editable_by_user(otherUser))

    def test_is_editable_by_user_superuser(self):
        '''
        ' Test that PortcullisUser method is_editable_by_user returns
        ' true when a superuser checks if they can edit another user
        '''

        user = PortcullisUser.objects.get(username="superuser")
        otherUser = PortcullisUser.objects.get(username="normaluser")

        self.assertTrue(otherUser.is_editable_by_user(user))

    def test_is_editable_by_user_nonuser(self):
        '''
        ' Test that PortcullisUser method is_editable_by_user returns
        ' a TypeError Exception when given a non user.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        bogusUser = "bogusssssss"

        self.assertRaises(TypeError, user.is_editable_by_user, user = bogusUser)



    ''''''''''''''''''' can_view '''''''''''''''''''''''''

    def test_can_view_correctUser(self):
        '''
        ' Test that PortcullisUser method can_view returns
        ' true when given a user trying to view itself.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        self.assertTrue(user.can_view(user))

    def test_can_view_incorrectUser(self):
        '''
        ' Test that PortcullisUser method can_view returns
        ' false when a non superuser checks if they can view another user.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        otherUser = PortcullisUser.objects.get(username="staffuser")

        self.assertFalse(user.can_view(otherUser))

    def test_can_view_superuser(self):
        '''
        ' Test that PortcullisUser method can_view returns
        ' true when a superuser checks if they can view another user
        '''

        user = PortcullisUser.objects.get(username="superuser")
        otherUser = PortcullisUser.objects.get(username="normaluser")

        self.assertTrue(otherUser.can_view(user))

    def test_can_view_nonuser(self):
        '''
        ' Test that PortcullisUser method can_view returns
        ' a TypeError Exception when given a non user.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        bogusUser = "bogusssssss"

        self.assertRaises(TypeError, user.can_view, user = bogusUser)

    
class KeyManagerTest(TestCase):
    '''
    ' Unit Tests for the portcullis Key manager
    '''
    
    fixtures = ['test_portcullisUsers.json', 'test_keys.json']



    ''''''''''''''''''' get_editable '''''''''''''''''''''''''

    def test_get_editable_keys_by_superuser(self):
        '''
        ' Test that a superuser get's all keys using get_editable from Keys
        '''

        sUser = PortcullisUser.objects.get(username="superuser")
        keys = Key.objects.all()

        sKeys = Key.objects.get_editable(sUser)
        self.assertEqual(list(sKeys), list(keys))
    
    def test_get_editable_keys_by_normal_user(self):
        '''
        ' Test that a non superuser get's only his/her keys using get_editable from Keys
        '''

        nUser = PortcullisUser.objects.get(username="normaluser")
        keys = Key.objects.filter(owner = nUser)

        nKeys = Key.objects.get_editable(nUser)
        self.assertEqual(list(keys), list(nKeys))

    def test_get_editable_keys_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using Key's get_editable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, Key.objects.get_editable, user=aUser)



    ''''''''''''''''''' validate '''''''''''''''''''''''''

    def test_validate_bad_token(self):
        '''
        ' Test that KeyManager validate returns None if a bad token is supplied.
        '''

        badToken = "HADUUUUKIN!!"
        self.assertEquals(Key.objects.validate(badToken), None)

    def test_validate_exp_date(self):
        '''
        ' Test that KeyManager validate returns None if an expired date token is supplied.
        '''

        expToken = Key.objects.get(key = "exp_key")
        self.assertEquals(Key.objects.validate(expToken.key), None)

    def test_validate_no_uses(self):
        '''
        ' Test that KeyManager validate returns None if a token with no uses is supplied.
        '''

        expToken = Key.objects.get(key = "no_uses_key")
        self.assertEquals(Key.objects.validate(expToken.key), None)
    
    def test_validate_valid_uses(self):
        '''
        ' Test that KeyManager validate returns the key supplied if the supplied key has uses left. 
        '''

        key = Key.objects.get(key = "valid_uses_key")
        self.assertEquals(Key.objects.validate(key.key), key)



    ''''''''''''''''''' get_editable_by_pk '''''''''''''''''''''''''

    def test_get_editable_by_pk_correctUser(self):
        '''
        ' Test that Key manager method get_editable_by_pk returns
        ' a key when given a user and a keys pk owned by that user.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        pk = "normaluser_key4"
        key = Key.objects.get(key=pk)

        self.assertEquals(Key.objects.get_editable_by_pk(user, pk), key)

    def test_get_editable_by_pk_incorrectUser(self):
        '''
        ' Test that Key manager method is_editable_by_user returns
        ' None when given a normaluser and some other users key pk.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        pk = "staffuser_key3"

        self.assertIsNone(Key.objects.get_editable_by_pk(user, pk))

    def test_get_editable_by_pk_superuser(self):
        '''
        ' Test that Key manager method is_editable_by_user returns
        ' a key when given a superuser and some other users key pk.
        '''

        user = PortcullisUser.objects.get(username="superuser")
        pk = "normaluser_key4"
        key = Key.objects.get(key=pk)

        self.assertEquals(Key.objects.get_editable_by_pk(user, pk), key)

    def test_get_editable_by_pk_nonuser(self):
        '''
        ' Test that Key manager method is_editable_by_user returns
        ' a TypeError Exception when given a user that isn't really a portcullis user.
        '''

        bogusUser = "bogusssssss"
        pk = "normaluser_key4"

        self.assertRaises(TypeError, Key.objects.get_editable_by_pk, user = bogusUser, pk = pk)

    def test_get_editable_by_pk_does_not_exist(self):
        '''
        ' Test that Key manager method is_editable_by_user returns
        ' a Key.DoesNotExist when given a pk of a non existent user.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        pk = "boguss key pk"

        self.assertRaises(Key.DoesNotExist, Key.objects.get_editable_by_pk, user = user, pk = pk)


class KeyModelTest(TestCase):
    '''
    ' Unit Tests for the portcullis Key model
    '''

    fixtures = ['test_portcullisUsers.json', 'test_keys.json']



    ''''''''''''''''''' isCurrent '''''''''''''''''''''''''

    def test_isCurrent_expired_key(self):
        '''
        ' Test that an expired key get's false returned from Key's isCurrent
        '''

        key = Key.objects.get(key = "exp_key")
        self.assertFalse(key.isCurrent())

    def test_isCurrent_no_uses_key(self):
        '''
        ' Test that a key with no uses get's false returned from Key's isCurrent
        '''

        key = Key.objects.get(key = "no_uses_key")
        self.assertFalse(key.isCurrent())

    def test_isCurrent_has_uses_key(self):
        '''
        ' Test that a key with uses left get's true returned from Key's isCurrent
        '''

        key = Key.objects.get(key = "valid_uses_key")
        self.assertTrue(key.isCurrent())

    def test_isCurrent_valid_exp_key(self):
        '''
        ' Test that a key with a non expired date get's true returned from Key's isCurrent
        '''

        key = Key.objects.get(key = "valid_date_key")
        self.assertTrue(key.isCurrent())

    def test_isCurrent_valid_key(self):
        '''
        ' Test that a key with both valid date and num uses get's true returned from Key's isCurrent
        '''

        key = Key.objects.get(key = "valid_key")
        self.assertTrue(key.isCurrent())



    ''''''''''''''''''' is_editable_by_user '''''''''''''''''''''''''

    def test_is_editable_by_user_correctUser(self):
        '''
        ' Test that Key method is_editable_by_user returns
        ' true when a normal user checks if it can edit a key that they own.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        key = Key.objects.get(key="normaluser_key4")

        self.assertTrue(key.is_editable_by_user(user))

    def test_is_editable_by_user_incorrectUser(self):
        '''
        ' Test that Key method is_editable_by_user returns
        ' false when a non superuser checks if it can edit another users key.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        key = Key.objects.get(key="staffuser_key3")

        self.assertFalse(key.is_editable_by_user(user))

    def test_is_editable_by_user_superuser(self):
        '''
        ' Test that Key method is_editable_by_user returns
        ' true when a superuser checks if it can edit another users key.
        '''

        user = PortcullisUser.objects.get(username="superuser")
        key = Key.objects.get(key="normaluser_key4")

        self.assertTrue(key.is_editable_by_user(user))

    def test_is_editable_by_user_nonuser(self):
        '''
        ' Test that Key method is_editable_by_user returns
        ' a TypeError Exception when given a non user.
        '''

        user = "None User"
        key = Key.objects.get(key="normaluser_key4")

        self.assertRaises(TypeError, key.is_editable_by_user, user = user)



    ''''''''''''''''''' can_view '''''''''''''''''''''''''

    def test_can_view_correctUser(self):
        '''
        ' Test that Key method can_view returns
        ' true when a normal user checks if it can view a key that they own.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        key = Key.objects.get(key="normaluser_key4")

        self.assertTrue(key.can_view(user))

    def test_can_view_superuser(self):
        '''
        ' Test that Key method can_view returns
        ' true when a superuser checks if it can view another users key.
        '''

        user = PortcullisUser.objects.get(username="superuser")
        key = Key.objects.get(key="normaluser_key4")

        self.assertTrue(key.can_view(user))

    def test_can_view_nonuser(self):
        '''
        ' Test that Key method can_view returns
        ' a TypeError Exception when given a non user.
        '''

        user = "None User"
        key = Key.objects.get(key="normaluser_key4")

        self.assertRaises(TypeError, key.can_view, user = user)


class DeviceManagerTest(TestCase):
    '''
    ' Unit Tests for the portcullis Device manager
    '''

    fixtures = ['test_portcullisUsers.json', 'test_devices.json']



    ''''''''''''''''''' get_editable '''''''''''''''''''''''''

    def test_get_editable_devices_by_superuser(self):
        '''
        ' Test that a superuser get's all devices using get_editable from Devices
        '''

        sUser = PortcullisUser.objects.get(username="superuser")
        devices = Device.objects.all()

        sDevices = Device.objects.get_editable(sUser)
        self.assertEqual(list(sDevices), list(devices))
    
    def test_get_editable_devices_by_normal_user(self):
        '''
        ' Test that a non superuser get's only his/her devices using get_editable from Devices
        '''

        nUser = PortcullisUser.objects.get(username="normaluser")
        devices = Device.objects.filter(owner = nUser)

        nDevices = Device.objects.get_editable(nUser)
        self.assertEqual(list(devices), list(nDevices))

    def test_get_editable_devices_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using Device's get_editable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, Device.objects.get_editable, user=aUser)



    ''''''''''''''''''' get_editable_by_pk '''''''''''''''''''''''''

    def test_get_editable_by_pk_correctUser(self):
        '''
        ' Test that Device manager method get_editable_by_pk returns
        ' a device when given a user and the pk of a device owned by that user.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        device = Device.objects.get(pk=3)

        self.assertEquals(Device.objects.get_editable_by_pk(user, 3), device)

    def test_get_editable_by_pk_incorrectUser(self):
        '''
        ' Test that Device manager method is_editable_by_user returns
        ' None when given a normaluser and some other users device pk.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        pk = 2

        self.assertIsNone(Device.objects.get_editable_by_pk(user, pk))

    def test_get_editable_by_pk_superuser(self):
        '''
        ' Test that Device manager method is_editable_by_user returns
        ' a device when given a superuser and some other users device pk.
        '''

        user = PortcullisUser.objects.get(username="superuser")
        device = Device.objects.get(pk=3)

        self.assertEquals(Device.objects.get_editable_by_pk(user, 3), device)

    def test_get_editable_by_pk_nonuser(self):
        '''
        ' Test that Device manager method is_editable_by_user returns
        ' a TypeError Exception when given a user that isn't really a portcullis user.
        '''

        bogusUser = "bogusssssss"
        pk = 1

        self.assertRaises(TypeError, Device.objects.get_editable_by_pk, user = bogusUser, pk = pk)

    def test_get_editable_by_pk_does_not_exist(self):
        '''
        ' Test that Device manager method is_editable_by_user returns
        ' a Device.DoesNotExist when given a pk of a non existent user.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        pk = -1

        self.assertRaises(Device.DoesNotExist, Device.objects.get_editable_by_pk, user = user, pk = pk)


class DeviceModelTest(TestCase):
    '''
    ' Unit Tests for the portcullis Device model
    '''

    fixtures = ['test_portcullisUsers.json', 'test_devices.json']



    ''''''''''''''''''' is_editable_by_user '''''''''''''''''''''''''

    def test_is_editable_by_user_correctUser(self):
        '''
        ' Test that Device method is_editable_by_user returns
        ' true when a normal user checks if it can edit a device it owns.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        device = Device.objects.get(pk = 3)

        self.assertTrue(device.is_editable_by_user(user))

    def test_is_editable_by_user_incorrectUser(self):
        '''
        ' Test that Device method is_editable_by_user returns
        ' false when a normal user checks if it can edit another users device.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        device = Device.objects.get(pk=2)

        self.assertFalse(device.is_editable_by_user(user))

    def test_is_editable_by_user_superuser(self):
        '''
        ' Test that Device method is_editable_by_user returns
        ' true when a superuser checks if it can edit another users device.
        '''

        user = PortcullisUser.objects.get(username="superuser")
        device = Device.objects.get(pk=2)

        self.assertTrue(device.is_editable_by_user(user))

    def test_is_editable_by_user_nonuser(self):
        '''
        ' Test that Device method is_editable_by_user returns
        ' a TypeError Exception when given a non user.
        '''

        device = Device.objects.get(pk=1)
        user = "None User"

        self.assertRaises(TypeError, device.is_editable_by_user, user = user)



    ''''''''''''''''''' can_view '''''''''''''''''''''''''

    def test_can_view_correctUser(self):
        '''
        ' Test that Device method can_view returns
        ' true when a normal user checks if it can view a device it owns.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        device = Device.objects.get(pk = 3)

        self.assertTrue(device.can_view(user))

    def test_can_view_superuser(self):
        '''
        ' Test that Device method can_view returns
        ' true when a superuser checks if it can view another users device.
        '''

        user = PortcullisUser.objects.get(username="superuser")
        device = Device.objects.get(pk=2)

        self.assertTrue(device.can_view(user))

    def test_can_view_nonuser(self):
        '''
        ' Test that Device method can_view returns
        ' a TypeError Exception when given a non user.
        '''

        device = Device.objects.get(pk=1)
        user = "None User"

        self.assertRaises(TypeError, device.can_view, user = user)


class DataStreamManagerTest(TestCase):
    '''
    ' Unit Tests for the portcullis DataStream manager
    '''

    fixtures = ['test_portcullisUsers.json', 'test_keys.json', 'test_scalingFunctions.json', 'test_datastreams.json']



    ''''''''''''''''''' get_editable '''''''''''''''''''''''''

    def test_get_editable_datastreams_by_superuser(self):
        '''
        ' Test that a superuser get's all datastreams using get_editable from DataStreams
        '''

        sUser = PortcullisUser.objects.get(username="superuser")
        datastreams = DataStream.objects.all()

        sDataStreams = DataStream.objects.get_editable(sUser)
        self.assertEqual(list(sDataStreams), list(datastreams))
    
    def test_get_editable_datastreams_by_normal_user(self):
        '''
        ' Test that a non superuser get's only his/her datastreams using get_editable from DataStreams
        '''

        nUser = PortcullisUser.objects.get(username="normaluser")
        datastreams = DataStream.objects.filter(owner = nUser)

        nDataStreams = DataStream.objects.get_editable(nUser)
        self.assertEqual(list(datastreams), list(nDataStreams))

    def test_get_editable_datastreams_non_portcullis_user(self):
        '''
        ' Test that a non portcullisUser object raises an exception when using DataStream's get_editable
        '''

        aUser = User.objects.get(username="superuser")
        self.assertRaises(TypeError, DataStream.objects.get_editable, user=aUser)



    ''''''''''''''''''' get_readable_by_key '''''''''''''''''''''''''

    def test_get_readable_by_non_key(self):
        '''
        ' Test that a non Key object raises an exception when using DataStream's get_readable_by_key
        '''
        
        nonKey = "I am a Key... NOT!!!!"
        self.assertRaises(TypeError, DataStream.objects.get_readable_by_key, key=nonKey)

    def test_get_readable_by_date_expired_key(self):
        '''
        ' Test that a Key which has an expired date raises an exception when using DataStream's get_readable_by_key
        '''
        
        expKey = Key.objects.get(key="exp_key")
        try:
            DataStream.objects.get_readable_by_key(expKey)
        except Exception as e:
            self.assertEqual(str(e), "None is not a valid key.")

    def test_get_readable_by_no_uses_key(self):
        '''
        ' Test that a Key which has no more uses raises an exception when using DataStream's get_readable_by_key
        '''

        noUsesKey = Key.objects.get(key="no_uses_key")
        try:
            DataStream.objects.get_readable_by_key(noUsesKey)
        except Exception as e:
            self.assertEqual(str(e), "None is not a valid key.")

    def test_get_readable_by_valid_key(self):
        '''
        ' Test that a Key which is valid returns a QuerySet of appropriate DataStreams when using DataStream's 
        ' get_readable_by_key
        '''

        validKey = Key.objects.get(key="valid_key")
        dStream = DataStream.objects.filter(can_read = validKey)

        self.assertEqual(list(dStream), list(DataStream.objects.get_readable_by_key(validKey)))

    def test_get_readable_by_valid_date_key(self):
        '''
        ' Test that a Key which is valid by it's date returns a QuerySet of appropriate DataStreams when using DataStream's 
        ' get_readable_by_key
        '''

        validKey = Key.objects.get(key="valid_date_key")
        dStream = DataStream.objects.filter(can_read = validKey)

        self.assertEqual(list(dStream), list(DataStream.objects.get_readable_by_key(validKey)))

    def test_get_readable_by_valid_uses_key(self):
        '''
        ' Test that a Key which is valid by it's num_uses returns a QuerySet of appropriate DataStreams when using DataStream's 
        ' get_readable_by_key
        '''

        validKey = Key.objects.get(key="valid_uses_key")
        dStream = DataStream.objects.filter(can_read = validKey)

        self.assertEqual(list(dStream), list(DataStream.objects.get_readable_by_key(validKey))) 



    ''''''''''''''''''' get_viewable '''''''''''''''''''''''''

    def test_get_viewable__non_user(self):
        '''
        ' Test that a non PortcullisUser passed to DataStreams manager get_viewable_by_user
        ' throws a TypeError
        '''

        nonUser = "I are a PortcullisUser huehuehue"
        self.assertRaises(TypeError, DataStream.objects.get_viewable, user = nonUser)

    def test_get_viewable_super_user(self):
        '''
        ' Test that a super PortcullisUser passed to DataStreams manager get_viewable_by_user
        ' gets all DataStreams that he doesn't own.
        '''
    
        sUser = PortcullisUser.objects.get(username="superuser")
        sStreams = DataStream.objects.all()

        vStreams = DataStream.objects.get_viewable(sUser)
        self.assertEqual(list(sStreams), list(vStreams))

    def test_get_viewable_non_valid_keys(self):
        '''
        ' Test that a normal PortcullisUser passed to DataStreams manager get_viewable_by_user
        ' gets no DataStreams that he has keys for but those keys are all invalid (expired or no more uses)
        '''

        user = PortcullisUser.objects.get(username="invalidkeysuser")
        uStreams = DataStream.objects.get_viewable(user)
        self.assertEqual(list(uStreams), [])

    def test_get_viewable_valid_keys(self):
        '''
        ' Test that a normal PortcullisUser passed to DataStreams manager get_viewable_by_user
        ' gets DataStreams that he has valid keys for
        '''

        user = PortcullisUser.objects.get(username="validkeysuser")
        d1 = DataStream.objects.get(pk = 3)
        d2 = DataStream.objects.get(pk = 4)
        d3 = DataStream.objects.get(pk = 5)
        d4 = DataStream.objects.get(pk = 6)
        dStreams = [d1, d2, d3, d4]

        uStreams = DataStream.objects.get_viewable(user)
        self.assertEqual(list(uStreams), dStreams)



    ''''''''''''''''''' get_editable_by_pk '''''''''''''''''''''''''

    def test_get_editable_by_pk_correctUser(self):
        '''
        ' Test that DataStream manager method get_editable_by_pk returns
        ' a datastream when given a user and the pk of a datastream owned by that user.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        datastream = DataStream.objects.get(pk=4)

        self.assertEquals(DataStream.objects.get_editable_by_pk(user, 4), datastream)

    def test_get_editable_by_pk_incorrectUser(self):
        '''
        ' Test that DataStream manager method is_editable_by_user returns
        ' None when given a normaluser and some other users datastream pk.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        pk = 2

        self.assertIsNone(DataStream.objects.get_editable_by_pk(user, pk))

    def test_get_editable_by_pk_superuser(self):
        '''
        ' Test that DataStream manager method is_editable_by_user returns
        ' a datastream when given a superuser and some other users datastream pk.
        '''

        user = PortcullisUser.objects.get(username="superuser")
        datastream = DataStream.objects.get(pk=3)

        self.assertEquals(DataStream.objects.get_editable_by_pk(user, 3), datastream)

    def test_get_editable_by_pk_nonuser(self):
        '''
        ' Test that DataStream manager method is_editable_by_user returns
        ' a TypeError Exception when given a user that isn't really a portcullis user.
        '''

        bogusUser = "bogusssssss"
        pk = 1

        self.assertRaises(TypeError, DataStream.objects.get_editable_by_pk, user = bogusUser, pk = pk)

    def test_get_editable_by_pk_does_not_exist(self):
        '''
        ' Test that DataStream manager method is_editable_by_user returns
        ' a DataStream.DoesNotExist when given a pk of a non existent user.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        pk = -1

        self.assertRaises(DataStream.DoesNotExist, DataStream.objects.get_editable_by_pk, user = user, pk = pk)


class DataStreamModelTest(TestCase):
    '''
    ' Unit Tests for the portcullis model DataStream
    '''

    fixtures = ['test_portcullisUsers.json', 'test_keys.json', 'test_scalingFunctions.json', 'test_datastreams.json']



    ''''''''''''''''''' is_editable_by_user '''''''''''''''''''''''''

    def test_is_editable_by_user_correctUser(self):
        '''
        ' Test that DataStream method is_editable_by_user returns
        ' true when a normal user checks if it can edit a datastream it owns.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        ds = DataStream.objects.get(pk=4)

        self.assertTrue(ds.is_editable_by_user(user))

    def test_is_editable_by_user_incorrectUser(self):
        '''
        ' Test that DataStream method is_editable_by_user returns
        ' false when a normal user checks if it able to edit another users data stream.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        ds = DataStream.objects.get(pk=2)

        self.assertFalse(ds.is_editable_by_user(user))

    def test_is_editable_by_user_superuser(self):
        '''
        ' Test that DataStream method is_editable_by_user returns
        ' true when a superuser checks if it can edit another users data stream.
        '''

        user = PortcullisUser.objects.get(username="superuser")
        ds = DataStream.objects.get(pk=2)

        self.assertTrue(ds.is_editable_by_user(user))

    def test_is_editable_by_user_nonuser(self):
        '''
        ' Test that DataStream method is_editable_by_user returns
        ' a TypeError Exception when given a non user.
        '''

        ds = DataStream.objects.get(pk=1)
        user = "None User"

        self.assertRaises(TypeError, ds.is_editable_by_user, user = user)



    ''''''''''''''''''' can_view '''''''''''''''''''''''''

    def test_can_view_correctUser(self):
        '''
        ' Test that DataStream method can_view returns
        ' true when a normal user with no can_read keys checks if it can view a datastream it owns.
        '''

        user = PortcullisUser.objects.get(username="normaluser_nokeys")
        ds = DataStream.objects.get(pk=7)

        self.assertTrue(ds.can_view(user))

    def test_can_view_userCanReadDate(self):
        '''
        ' Test that DataStream method can_view returns
        ' true when a normal user checks if it can view a stream it does not own
        ' but has an key in the streams can_read that has a valid date.
        '''

        user = PortcullisUser.objects.get(username="validkeysuser")
        ds = DataStream.objects.get(pk=3)

        self.assertTrue(ds.can_view(user))

    def test_can_view_user_can_read_expDate(self):
        '''
        ' Test that DataStream method can_view returns
        ' false when a normal user checks if it can view a stream it does not own
        ' but has an key in the streams can_read that has a expired date.
        '''

        user = PortcullisUser.objects.get(username="normaluser_nokeys")
        key = Key.objects.get(key="exp_key")
        key.owner = user
        ds = DataStream.objects.get(pk=3)
        ds.can_read.add(key)

        self.assertFalse(ds.can_view(user))
        key.num_uses = 1
        key.save()
        self.assertFalse(ds.can_view(user))

    def test_can_view_user_can_read_noUses(self):
        '''
        ' Test that DataStream method can_view returns
        ' false when a normal user checks if it can view a stream it does not own
        ' but has an key in the streams can_read that has no uses left.
        '''

        user = PortcullisUser.objects.get(username="normaluser_nokeys")
        key = Key.objects.get(key="no_uses_key")
        key.owner = user
        ds = DataStream.objects.get(pk=3)
        ds.can_read.add(key)

        self.assertFalse(ds.can_view(user))
        key.expiration = "2030-01-01 09:30+00:00"
        key.save()
        self.assertFalse(ds.can_view(user))
 
    def test_can_view_user_can_read_noUses_expDate(self):
        '''
        ' Test that DataStream method can_view returns
        ' false when a normal user checks if it can view a stream it does not own
        ' but has an key in the streams can_read that has no uses left and an expired date.
        '''

        user = PortcullisUser.objects.get(username="normaluser_nokeys")
        key = Key.objects.get(key="exp_key")
        key.num_uses = 0
        key.owner = user
        ds = DataStream.objects.get(pk=3)
        ds.can_read.add(key)

        self.assertFalse(ds.can_view(user))

    def test_can_view_userCanReadUses(self):
        '''
        ' Test that DataStream method can_view returns
        ' true when a normal user checks if it can view a stream it does not own
        ' but has an key in the streams can_read that has a valid number of uses.
        '''

        user = PortcullisUser.objects.get(username="normaluser")
        key = Key.objects.get(key="valid_uses_key")
        key.owner = user
        key.save()
        ds = DataStream.objects.get(pk=3)
        ds.can_read.add(key)

        self.assertTrue(ds.can_view(user))

    def test_can_view_publicStream(self):
        '''
        ' Test that DataStream method can_view returns
        ' true when a user with no can_read keys checks if it can view a public stream it does
        ' not own.
        '''

        user = PortcullisUser.objects.get(username="normaluser_nokeys")
        ds = DataStream.objects.get(pk=8)

        self.assertTrue(ds.can_view(user))

    def test_can_view_incorrectUser(self):
        '''
        ' Test that DataStream method can_view returns
        ' false when a normal user with no can_read keys checks if it able to view another users data stream.
        '''

        user = PortcullisUser.objects.get(username="normaluser_nokeys")
        ds = DataStream.objects.get(pk=2)

        self.assertFalse(ds.can_view(user))

    def test_can_view_superuser(self):
        '''
        ' Test that DataStream method can_view returns
        ' true when a superuser with no can_read keys checks if it can view another users data stream.
        '''

        user = PortcullisUser.objects.get(username="superuser_nokeys")
        ds = DataStream.objects.get(pk=2)

        self.assertTrue(ds.can_view(user))

    def test_can_view_nonuser(self):
        '''
        ' Test that DataStream method can_view returns
        ' a TypeError Exception when given a non user.
        '''

        ds = DataStream.objects.get(pk=1)
        user = "None User"

        self.assertRaises(TypeError, ds.can_view, user = user)

    def test_can_view_isCurrent_date_key(self):
        '''
        ' Should return true if given a key in a streams can_read with a non expired date and no uses set.
        '''

        key = Key.objects.get(key="valid_date_key")
        ds = DataStream.objects.get(pk=1)
        ds.can_read.add(key)

        self.assertTrue(ds.can_view(key))

    def test_can_view_isCurrent_uses_key(self):
        '''
        ' Should return true if given a key in a streams can_read with uses left and no expiration set.
        '''

        key = Key.objects.get(key="valid_uses_key")
        ds = DataStream.objects.get(pk=1)
        ds.can_read.add(key)

        self.assertTrue(ds.can_view(key))

    def test_can_view_isCurrent_date_key_not_in_stream(self):
        '''
        ' Should return true if given a key not in a streams can_read with a non expired date and no uses set.
        '''

        key = Key.objects.get(key="valid_date_key")
        ds = DataStream.objects.get(pk=1)

        self.assertFalse(ds.can_view(key))

    def test_can_view_isCurrent_uses_key_not_in_stream(self):
        '''
        ' Should return true if given a key not in a streams can_read with uses left and no expiration set.
        '''

        key = Key.objects.get(key="valid_uses_key")
        ds = DataStream.objects.get(pk=1)

        self.assertFalse(ds.can_view(key))


    def test_can_view_isNot_current_date_key(self):
        '''
        ' Should return false if given a key in a streams can_read with a expired date and no uses.
        '''

        key = Key.objects.get(key="exp_key")
        ds = DataStream.objects.get(pk=1)
        ds.can_read.add(key)

        self.assertFalse(ds.can_view(key))

    def test_can_view_isNot_current_uses_key(self):
        '''
        ' Should return false if given a key in a streams can_read with a no uses left and None for expirations.
        '''

        key = Key.objects.get(key="no_uses_key")
        ds = DataStream.objects.get(pk=1)
        ds.can_read.add(key)

        self.assertFalse(ds.can_view(key))


