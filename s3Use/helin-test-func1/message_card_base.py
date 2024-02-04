#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2022/9/6 5:37 PM
@Author  : jingxuyang
@Project : py-robot-keyword
@FileName: robot_open_api.py
"""


class MessageCardBase:
    def __init__(self, header:bool, title:str, template_color:str, wide_screen_mode:bool):
        self.header = header
        self.title = title
        self.template_color = template_color
        self.wide_screen_mode = wide_screen_mode

    def create_message(self, elements:list):
        self.base_message = {
            "msg_type":"interactive",
            "card":{
                "config": {
                    "wide_screen_mode": self.wide_screen_mode if self.wide_screen_mode else True,
                    "update_multi": True
                },
                "elements": elements
            }
        }
        if self.header:
            self.base_message.get("card")["header"] = {
                    "template": self.template_color if self.template_color else "orange",
                    "title": {
                        "content": self.title if self.title else "罗伯特平台提供技术支持",
                        "tag": "plain_text"
                    }
                }
        return self.base_message




