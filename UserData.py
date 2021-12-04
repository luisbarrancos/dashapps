#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 21:54:24 2021

@author: cgwork
"""


class UserData:
    def __init__(
        self,
        user_name=None,
        user_age=None,
        birthplace=None,
        residence=None,
        sex=None,
        veggie=None,
        driver=None,
        smoker=None,
    ):
        self.__user_name = user_name
        # this requires user_age is numeric

        if user_age is not None and str(user_age).isdigit():
            self.__user_age = user_age
        else:
            self.__user_age = 0

        self.__user_age = user_age
        self.__birthplace = birthplace
        self.__residence = residence
        self.__sex = sex
        self.__veggie = veggie
        self.__driver = driver
        self.__smoker = smoker
        self.__allcheck = False

    def set_age(self, user_age):
        self.__user_age = (
            int(user_age) if user_age is not None and str(user_age).isdigit() else 0
        )

    def set_name(self, user_name):
        self.__user_name = user_name

    def set_birthplace(self, birthplace):
        self.__birthplace = birthplace

    def set_residence(self, residence):
        self.__residence = residence

    def set_sex(self, sex):
        self.__sex = sex

    def set_veggie(self, veggie):
        self.__veggie = veggie

    def set_driver(self, driver):
        self.__driver = driver

    def set_smoker(self, smoker):
        self.__smoker = smoker

    def print_data(self):
        print(
            self.__user_name,
            self.__user_age,
            self.__birthplace,
            self.__residence,
            self.__sex,
            self.__veggie,
            self.__driver,
            self.__smoker,
        )

    def get_data(self):
        return [
            self.__user_name,
            self.__user_age,
            self.__birthplace,
            self.__residence,
            self.__sex,
            self.__veggie,
            self.__driver,
            self.__smoker,
        ]

    def check_data(self):
        data = self.get_data()
        check = filter(lambda x: x is not None, data)
        return True if len(list(check)) > 0 else False
