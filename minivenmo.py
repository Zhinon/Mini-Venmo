"""
Questions:


    1. Complete the `MiniVenmo.create_user()` method to allow our application to create new users.

    2. Complete the `User.pay()` method to allow users to pay each other. Consider the following: if user A is paying user B, user's A balance should be used if there's enough balance to cover the whole payment, if not, user's A credit card should be charged instead.

    3. Venmo has the Feed functionality, that shows the payments that users have been doing in the app. If Bobby paid Carol $5, and then Carol paid Bobby $15, it should look something like this


    Bobby paid Carol $5.00 for Coffee
    Carol paid Bobby $15.00 for Lunch

    Implement the `User.retrieve_activity()` and `MiniVenmo.render_feed()` methods so the MiniVenmo application can render the feed.

    4. Now users should be able to add friends. Implement the `User.add_friend()` method to allow users to add friends.
    5. Now modify the methods involved in rendering the feed to also show when user's added each other as friends.
"""

"""
MiniVenmo! Imagine that your phone and wallet are trying to have a beautiful
baby. In order to make this happen, you must write a social payment app.
Implement a program that will feature users, credit cards, and payment feeds.
"""
import abc
import re
import unittest
from unittest.mock import MagicMock
import uuid


ACTIVITY_PAYMENT_TYPE = 'payment'
ACTIVITY_NEW_FRIEND_TYPE = 'new_friend'


class UsernameException(Exception):
    pass


class PaymentException(Exception):
    pass


class CreditCardException(Exception):
    pass


class InsufficientBalance(Exception):
    pass


class FriendException(Exception):
    pass


class Activities(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def representation(self):
        ...


class PaymentActivity(Activities):

    def __init__(self, payment):
        self.payment = payment

    def representation(self):
        return '{actor} paid {target} ${amount} for {note}'.format(
            actor=self.payment.actor.username,
            target=self.payment.target.username,
            amount=self.payment.amount,
            note=self.payment.note,
        )


class NewFriendActivity(Activities):

    def __init__(self, actor, new_friend):
        self.actor = actor
        self.new_friend = new_friend

    def representation(self):
        return '{actor} now is friend of {new_friend}'.format(
            actor=self.actor.username,
            new_friend=self.new_friend.username,
        )


class Payment:

    def __init__(self, amount, actor, target, note):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note


class User:

    def __init__(self, username):
        self.credit_card_number = None
        self.balance = 0.0
        self.activities = []
        self.friends = []
        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException('Username not valid.')

    def retrieve_feed(self):
        return self.activities

    def add_friend(self, new_friend):
        if new_friend not in self.friends:
            self.friends.append(new_friend)
            new_friend.add_friend(self)
            self.activities.append(NewFriendActivity(self, new_friend))

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def subtract_to_balance(self, amount):
        self.balance -= float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number

        else:
            raise CreditCardException('Invalid credit card number.')

    def pay(self, target, amount, note):
        amount = float(amount)
        payment = None
        if amount <= self.balance:
            payment = self.pay_with_balance(
                target=target,
                amount=amount,
                note=note
            )
        elif self.credit_card_number:
            payment = self.pay_with_card(
                target=target,
                amount=amount,
                note=note
            )
        else:
            raise PaymentException("Couldn't complete the payment")

        self.activities.append(PaymentActivity(payment))
        target.activities.append(PaymentActivity(payment))

        return payment

    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')

        self._charge_credit_card(self.credit_card_number)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def pay_with_balance(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        payment = Payment(
            amount=amount,
            actor=self,
            target=target,
            note=note,
        )
        self.subtract_to_balance(amount)
        target.add_to_balance(amount)

        return payment

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        return re.match('^[A-Za-z0-9_\\-]{4,15}$', username)

    def _charge_credit_card(self, credit_card_number):
        # magic method that charges a credit card thru the card processor
        pass


class MiniVenmo:
    def create_user(self, username, balance, credit_card_number):
        new_user = User(username)
        new_user.add_to_balance(balance)
        new_user.add_credit_card(credit_card_number)
        return new_user

    def render_feed(self, feed):
        for activity in feed:
            print(activity.representation())

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")

            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)


class TestUser(unittest.TestCase):

    def setUp(self):
        self.user1 = User('Bobby')
        self.user2 = User('Carol')

    def test_add_friend(self):
        self.user1.add_friend(self.user2)

        self.assertTrue(len(self.user1.friends) == 1)
        self.assertTrue(len(self.user2.friends) == 1)
        self.assertTrue(self.user2 in self.user1.friends)
        self.assertTrue(self.user1 in self.user2.friends)

    def test_add_credit_card(self):
        valid_credit_card = '4111111111111111'

        self.user1.add_credit_card(valid_credit_card)

        self.assertTrue(self.user1.credit_card_number == valid_credit_card)

    def test_add_anotther_credit(self):
        another_credit_card = '4242424242424242'
        self.user1.credit_card_number = '4111111111111111'

        with self.assertRaises(CreditCardException):
            self.user1.add_credit_card(another_credit_card)

    def test_add_invalid_credit_card(self):
        invalid_credit_card = '3111111111111111'

        with self.assertRaises(CreditCardException):
            self.user1.add_credit_card(invalid_credit_card)

    def test_pay_with_card(self):
        self.user1.credit_card_number = '4111111111111111'

        self.user1.pay_with_card(self.user2, 80.0, 'test')

        self.assertTrue(self.user2.balance == 80.0)

    def test_try_to_pay_with_credit_card_to_himself(self):
        self.user1.credit_card_number = '4111111111111111'

        with self.assertRaises(PaymentException):
            self.user1.pay_with_card(self.user1, 80.0, 'test')

    def test_try_to_pay_with_credit_card_a_negative_number(self):
        self.user1.credit_card_number = '4111111111111111'

        with self.assertRaises(PaymentException):
            self.user1.pay_with_card(self.user2, -80.0, 'test')

    def test_try_to_pay_without_credit_card(self):

        with self.assertRaises(PaymentException):
            self.user1.pay_with_card(self.user2, 80.0, 'test')

    def test_pay_with_balance(self):
        self.user1.balance = 50.0

        self.user1.pay_with_balance(self.user2, 20.0, 'test')

        self.assertTrue(self.user1.balance == 30.0)
        self.assertTrue(self.user2.balance == 20.0)

    def test_try_to_pay_with_balance_to_himself(self):
        self.user1.balance = 50.0

        with self.assertRaises(PaymentException):
            self.user1.pay_with_card(self.user1, 50.0, 'test')

    def test_try_to_pay_with_balance_a_negative_number(self):
        self.user1.balance = 50.0

        with self.assertRaises(PaymentException):
            self.user1.pay_with_card(self.user2, -80.0, 'test')

    def test_pay_through_credit_card(self):
        self.user1.credit_card_number = '4111111111111111'
        self.user1.pay_with_card = MagicMock()
        self.user1.pay_with_balance = MagicMock()

        self.user1.pay(self.user2, 80.0, 'test')

        self.assertTrue(self.user1.pay_with_card.called)
        self.assertFalse(self.user1.pay_with_balance.called)
        self.assertTrue(len(self.user1.activities) == 1)
        self.assertTrue(len(self.user2.activities) == 1)

    def test_pay_through_balance(self):
        self.user1.balance = 100
        self.user1.pay_with_card = MagicMock()
        self.user1.pay_with_balance = MagicMock()

        self.user1.pay(self.user2, 80.0, 'test')

        self.assertFalse(self.user1.pay_with_card.called)
        self.assertTrue(self.user1.pay_with_balance.called)
        self.assertTrue(len(self.user1.activities) == 1)
        self.assertTrue(len(self.user2.activities) == 1)

    def test_pay_could_not_pay(self):
        self.user1.pay_with_card = MagicMock()
        self.user1.pay_with_balance = MagicMock()

        with self.assertRaises(PaymentException):
            self.user1.pay(self.user2, 80.0, 'test')

        self.assertFalse(self.user1.pay_with_card.called)
        self.assertFalse(self.user1.pay_with_balance.called)


if __name__ == '__main__':
    # MiniVenmo.run()
    unittest.main()
