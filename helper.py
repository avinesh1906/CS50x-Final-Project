import os

from flask import redirect, render_template, request, session
from functools import wraps
from datetime import date
import datetime
import calendar


def apology(message):
    return render_template("apology.html", message=message)


def cardvalidation(cardnum):
    n = cardnum

    # calculate the number of digits
    length = len(str(n))
    l = n
    total = 0
    checking = 0

    # 16 digits card
    if length == 16:

        while l > 10:

            remainder1 = 0
            remainder1digit = 0
            multiply = 0
            remainder1 = int(l % 100)  # break the number into groups of 2

            remainder1digit = int(remainder1 / 10)  # choose the first digit of the group as selected

            multiply = remainder1digit * 2   # multiply the selected first digit by 2

            # checking if the multiplication exceed 10
            if multiply < 10:
                total += multiply
            elif multiply > 9:
                total = total + int(multiply / 10) + int(multiply % 10)

            total = total + int(remainder1 % 10)  # add the unselected digit with sum

            l /= 100  # reduce the size of the number of digits by 2 starting rightmost
        checking = total % 10
        if checking == 0:
            if n >= 4e12 and n < 5e12 or n >= 4e15 and n < 5e15:  # e represent leading zero's
                return 0
            elif n >= 51e14 and n <= 56e14:
                return 0
            else:
                return -1
        else:
            return -1

    # 15 digits card
    elif length == 15:
        fif = int(l / 10)
        last1 = int(l % 10)
        while fif > 10:  # loop until the number becomes a 2 digit integer
            remain = 0
            remain1digit = 0
            multiply1 = 0
            remain = int(fif % 100)  # break the number into groups of 2
            remain1digit = int(remain % 10)  # choose the second digit as selected
            multiply1 = int(remain1digit * 2)   # multiply the selected first digit by 2
            # checking if the multiplication exceed 10
            if multiply1 < 10:
                total += multiply1
            elif multiply1 > 9:
                total = total + int(multiply1 / 10) + int(multiply1 % 10)
            total = total + int(remain / 10)  # add the unselected digit with sum
            fif /= 100  # reduce the size of the number of digits by 2 starting rightmost
        total = total + last1
        # checking if the total of the multiplication of selected digits plus the totals unselected digits has a modulus of zero
        checking = int(total % 10)
        if checking == 0:
            if n >= 34e13 and n < 35e13 or n >= 37e13 and n < 38e13:
                return 0
            else:
                return -1
        else:
            return -1  # reject if the modulus is not zero

    # 13 digits card
    elif length == 13:
        third = int(l / 10)  # removing the rightmost digit
        last = int(l % 10)  # choose the second digit of the removed digit
        while third > 10:  # loop until the number becomes a 2 digit integer
            re = 0
            redigit = 0
            multiply2 = 0
            re = int(third % 100)  # break the number into groups of 2
            redigit = int(re % 10)  # choose the second digit as selected
            multiply2 = int(redigit * 2)  # multiply the selected first digit by 2
            # checking if the multiplication exceed 10
            if multiply2 < 10:
                total = total + multiply2
            elif (multiply2 > 9):
                total = total + int(multiply2 / 10) + int(multiply2 % 10)
            total = total + int(re / 10)  # add the unselected digit with sum
            third /= 100  # reduce the size of the number of digits by 2 starting rightmost

        total = total + last
        # checking if the total of the multiplication of selected digits plus the totals unselected digits has a modulus of zero
        checking = int(total % 10)
        if checking == 0:
            if n >= 4e12 and n < 5e12 or n >= 4e15 and n < 5e15:
                return 0
            else:
                return -1
        else:
            return -1  # reject if the modulus is not zero
    else:
        # reject if the total digits in the number is not 13 or 15 or 16
        return -1


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def password_validation(password):

    if len(password) < 8:
        return -1
    digits = 0
    letters = 0
    for x in password:
        if x.isdigit() == True:  # make use of isalpha which check alphanumeric characters
            digits += 1
        if x.isalpha() == True:
            letters += 1
    if digits == 0:
        return -1
    if letters == 0:
        return -1
    return 0

def findDay(date):
    # find the day of a specifc date
    year, month, day = (int(i) for i in date.split('-'))
    dayNumber = calendar.weekday(year, month, day)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]
    return (days[dayNumber])
