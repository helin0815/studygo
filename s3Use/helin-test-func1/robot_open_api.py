#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2022/9/6 5:37 PM
@Author  : jingxuyang
@Project : py-robot-keyword
@FileName: robot_open_api.py
"""

import json
import logging
import traceback
import requests


# 罗伯特开放平台接口
class RobotOpenApi(object):
    _robot_data = {
        "appName": "lichat-robot",
        "action": "",
        "groupId": "",
        "userIds": "",
        "message": "罗伯特基础服务",
        "callbackUrl": "",
        "rootId": "",
        "actionReason": "",
        "actionExecuteType": 1    # 0，未知，1，手动；2，自动
    }

    @classmethod
    def _call_open_api(cls, env: str="dev"):
        if env == "prod":
            robot_open_url = "https://feishu.chehejia.com"
        else:
            robot_open_url = "https://feishu-test.chehejia.com"
            # robot_open_url = "https://op-feishu-robot-api.dev.k8s.chj.cloud"
        logging.info(f"robot: {robot_open_url}, {cls._robot_data}")
        try:
            data = requests.post(robot_open_url + "/robot/api/v1/open/", data=json.dumps(cls._robot_data)).json()
            return data
        except Exception as e:
            logging.error(f"Feishu ApiError: {traceback.format_exc()}")
            return dict()

    # 创群
    @classmethod
    def create_group(cls, env, users, group_name):

        cls._robot_data["action"] = "create"
        cls._robot_data["userIds"] = users
        cls._robot_data["message"] = group_name
        return cls._call_open_api(env)

    # 加人 踢人
    @classmethod
    def update_member(cls, env, group_id, users, t="add"):

        if t == "add":
            cls._robot_data["action"] = "addMember"
            cls._robot_data["message"] = "加人"
        else:
            cls._robot_data["action"] = "removeMember"
            cls._robot_data["message"] = "踢人"
        cls._robot_data["groupId"] = group_id
        cls._robot_data["userIds"] = users
        return cls._call_open_api(env)

    # 修改群名称
    @classmethod
    def update_title(cls, env, group_id, title_name, root_id=""):

        cls._robot_data["action"] = "updateTitle"
        cls._robot_data["groupId"] = group_id
        cls._robot_data["message"] = title_name
        cls._robot_data["rootId"] = root_id
        return cls._call_open_api(env)

    # 发送消息
    @classmethod
    def send_message(cls, env, group_id, root_id="", message=None, at_users="", is_markdown=False):

        cls._robot_data["action"] = "send"
        cls._robot_data["groupId"] = group_id
        cls._robot_data["userIds"] = at_users
        cls._robot_data["message"] = message
        cls._robot_data["isMarkdown"] = is_markdown
        cls._robot_data["rootId"] = root_id
        return cls._call_open_api(env)

    # 发送卡片消息
    @classmethod
    def send_message_card(cls, env, group_id, root_id="", message=None, at_users="", is_markdown=False):

        if message is None:
            message = {}
        cls._robot_data["action"] = "sendCard"
        cls._robot_data["groupId"] = group_id
        cls._robot_data["userIds"] = at_users
        cls._robot_data["message"] = message
        cls._robot_data["isMarkdown"] = is_markdown
        cls._robot_data["rootId"] = root_id
        return cls._call_open_api(env)

    # 群内发送仅对个人可见卡片消息
    @classmethod
    def send_message_card_ephemeral(cls, env, group_id, message, at_users="", is_markdown=True):

        cls._robot_data["action"] = "sendCardEphemeral"
        cls._robot_data["groupId"] = group_id
        cls._robot_data["userIds"] = at_users
        cls._robot_data["message"] = message
        cls._robot_data["isMarkdown"] = is_markdown
        return cls._call_open_api(env)

    # 获取群成员列表
    @classmethod
    def get_group_members(cls, env, group_id):

        cls._robot_data["action"] = "getGroupMembers"
        cls._robot_data["groupId"] = group_id
        cls._robot_data["message"] = "获取群成员列表"
        return cls._call_open_api(env)

    # 表情回复，默认done表情
    @classmethod
    def send_reaction(cls, env, root_id, emoji_type: str="DONE"):
        cls._robot_data["action"] = "sendReaction"
        cls._robot_data["rootId"] = root_id
        cls._robot_data["emojiType"] = emoji_type
        return cls._call_open_api(env)

    # 原地更新卡片消息
    @classmethod
    def update_message(cls, env, message, at_users="", update_message_id="", root_id=""):
        cls._robot_data["action"] = "updateCard"
        cls._robot_data["userIds"] = at_users
        cls._robot_data["message"] = message
        cls._robot_data["updateMessageId"] = update_message_id
        cls._robot_data["isMarkdown"] = True
        cls._robot_data["rootId"] = root_id
        return cls._call_open_api(env)
