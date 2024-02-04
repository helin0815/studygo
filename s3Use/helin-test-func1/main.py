#!/usr/bin/env python
import json
import logging
import os
import sys
import traceback
import uuid
#aaa
import requests
import uvicorn
from fastapi import FastAPI
from starlette.background import BackgroundTasks
from starlette.requests import Request

from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from log_handler import InterceptHandler
from message_card_base import MessageCardBase
from redis_manage import REDIS
from robot_open_api import RobotOpenApi

app_name = "lichat-im-entry"

docs_url = "/docs"
redoc_url = "/redoc"
if os.getenv("LI_ENV") == "prod":
    docs_url = None
    redoc_url = None


def init_app():
    app = FastAPI(
        title=app_name,
        description="LiChat机器人功能接口",
        version="1.0.0"
    )
    origins = [
        "http://localhost",
        "127.0.0.1:8080",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logging.getLogger().handlers = [InterceptHandler()]
    logger.configure(
        handlers=[{"sink": sys.stdout, "level": "INFO",
         "format": "[v1] [{time:YYYY-MM-DD HH:mm:ss.hhh}] [{level}] [{thread}] {file} [TID: N/A] {name} {function} {line} {message}"},
        {"sink": '/chj/data/log/op-feishu-robot-api/op-feishu-robot-api.log',
         "format": "[v1] [{time:YYYY-MM-DD HH:mm:ss.hhh}] [{level}] [{thread}] {file} [TID: N/A] {name} {function} {line} {message}",
         "level": "INFO","rotation": "1GB", "retention":"6 months", "compression":"zip", "encoding": 'utf-8'},
        {"sink": '/chj/data/log/op-feishu-robot-api/op-feishu-robot-api_error.log',
         "format": "[v1] [{time:YYYY-MM-DD HH:mm:ss.hhh}] [{level}] [{thread}] {file} [TID: N/A] {name} {function} {line} {message}",
         "level": 'ERROR', "rotation": "1GB", "retention":"6 months", "compression":"zip", "encoding": 'utf-8'},]
    )
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    return app


app = init_app()



@app.get('/healthz')
def healthz():
    return "health", 200


@app.get('/')
def entry():
    resp = {
        'code': 200,
        'data': [
            {
                'content': "这是一个redis的操作demo",
                'title': '入口',
            }
        ]
    }
    return resp


@app.post('/newChat')
async def new_chat(request: Request):
    try:
        request_data = await request.json() or dict()
        logger.info(f"new lichat feishu request_body:{request_data}")
        button_data = request_data.get("action", {}).get("value", {}).get("data", {})
        username = button_data.get("username", "")
        feishu_chat_id = button_data.get("feishu_chat_id", "")
        env = str(os.getenv("LI_ENV"))
        if env != "prod":
            env = "dev"
        # 删除redis key
        user_lichat_context_redis_key = "lichat-context-" + username
        REDIS.delete(user_lichat_context_redis_key)
        message_elements = [{
            "tag": "markdown",
            "content": "您已成功开启新会话，请向我提问"
        }]
        card_message = MessageCardBase(False, "", "", True).create_message(message_elements)
        if feishu_chat_id and feishu_chat_id.startswith("oc_"):
            username = ""
        else:
            feishu_chat_id = ""
        send_res = RobotOpenApi.send_message_card(env, feishu_chat_id, "", card_message, username, True)
        return {"code": 200}
    except Exception:
        logger.error(f"开启新会话失败：{traceback.format_exc()}")
        return {"code": 400, "msg": "error"}


@app.post('/contextChat')
async def context_chat(request: Request,  background_tasks: BackgroundTasks):
    try:
        request_data = await request.json () or dict ()
        logger.info(f"context lichat feishu request_body:{request_data}")
        input_data = parse_user_input(request_data)
        if input_data.get("chat_type") != "group":
            feishu_chat_id = ""
        else:
            feishu_chat_id = input_data.get("feishu_chat_id")

        if input_data.get("user_type") != 1:
            res = "暂不支持您使用LiChat"
            logger.info(f"not employee, feishu_chat_id:{feishu_chat_id}, request_data:{request_data}")
            RobotOpenApi.send_message(input_data.get("env"), feishu_chat_id,
                                      request_data.get("feishu_message_id", ""), res, input_data.get("username"), False)
            return {"code": 400, "data": "not employee"}
        if input_data.get("msg_type") != "text":
            res = "暂仅支持文本消息类型，其他类型正在路上，敬请期待"
            RobotOpenApi.send_message(input_data.get("env"), feishu_chat_id,
                                      request_data.get("feishu_message_id"), res, input_data.get("username"), False)
            return {"code": 400, "data": "not employee"}
        # 发送loading消息
        loading_message_res = send_loading_message(input_data.get("env"), request_data.get("feishu_message_id", ""), feishu_chat_id, input_data.get("username"))
        loading_message_id = loading_message_res.get("feishu_response", {}).get("data", {}).get("message_id", "")
        background_tasks.add_task ( get_lichat_res, input_data.get("username"), input_data.get("mobile"),
                                    input_data.get("user_input"), input_data.get("env"),
                                    feishu_chat_id, request_data.get("feishu_message_id", ""),
                                            input_data.get("chat_type"), loading_message_id)
        return {"code": 200, "data": "lichat success"}
    except Exception as e:
        logger.error("上下文会话失败：%s" % traceback.format_exc())
        return {"code": 500, "errMessage": f"上下文会话失败,{e}"}


# 解析用户输入信息
def parse_user_input(request_data):
    if request_data.get("chat_id") and request_data.get("chat_id").startswith("oc_"):
        feishu_chat_id = request_data.get("chat_id")
    else:
        feishu_chat_id = ""
    username = request_data.get("ldap_name")
    user_input = request_data.get("message_without_bot") if request_data.get("message_without_bot") else request_data.get("message")
    env = str(os.getenv("LI_ENV"))
    logger.info(f"env:{env}")
    if env != "prod":
        env = "dev"
    # 根据域账号解析手机号
    mobile = request_data.get("mobile")
    chat_type = request_data.get("chat_type")
    msg_type = request_data.get("msg_type")
    # 1:正式员工，2：外援
    user_type = int(request_data.get("user_type", 0)) if request_data.get("user_type") else 0
    return {"feishu_chat_id": feishu_chat_id, "username": username, "mobile": mobile, "env": env,
            "user_input": user_input, "chat_type": chat_type, "msg_type": msg_type, "user_type": user_type}


# 获取lichat回复
def get_lichat_res(username, mobile, content, env, feishu_chat_id, feishu_message_id, chat_type, loading_message_id):
    LiChat_url = os.getenv("LICHAT_URL")
    authorization = mobile
    if not mobile:
        authorization = username
    LiChat_headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
        # "X-CHJ-GWToken": os.getenv("APIHUB_TOKEN")
    }
    message_id = str(uuid.uuid4())
    user_lichat_context_redis_key = "lichat-context-" + username
    data = {
        "content": content,
        "messageId": message_id,
        "feishuChatId": feishu_chat_id,
        "feishuChatType": chat_type,
        "stream": True,
        "model": "MS-GPT-4-turbo"
    }
    if chat_type != "group":
        user_lichat_context_data = REDIS.get(user_lichat_context_redis_key)
        user_lichat_context_list = user_lichat_context_data.decode().split("+") if user_lichat_context_data else []
        if len(user_lichat_context_list) == 3:
            chat_id = user_lichat_context_list[0]
            parent_message_id = user_lichat_context_list[1]
            conversation_id = user_lichat_context_list[2]
            data = {
                "content": content,
                "messageId": message_id,
                "parentMessageId": parent_message_id,
                "chatId": chat_id,
                "conversationId": conversation_id,
                "feishuChatId": feishu_chat_id,
                "feishuChatType": chat_type,
                "stream": True,
                "model": "MS-GPT-4-turbo"
            }
    try:
        for i in range(3):
            logger.info(f"lichat request time={i+1}, lichat request_body:{data}")
            gpt_res = requests.post(url=LiChat_url, headers=LiChat_headers, data=json.dumps(data), stream=True)
            if gpt_res.status_code != 200:
                logger.error(
                    f"lichat request error!! feishu request_body:{data}，username={username}, feishu_chat_id={feishu_chat_id}, env={env}，lichat_res={gpt_res}")
                continue
            j = 0
            r_text = ""
            gpt_message_id = ""
            gpt_chat_id = ""
            gpt_conversation_id = ""
            for r in gpt_res.iter_lines(decode_unicode=True):
                if not r:
                    continue
                r_data = json.loads(r.replace("data:", ""))
                if r_data.get("chatId") and r_data.get("messageId") and r_data.get("conversationId"):
                    gpt_chat_id = r_data.get("chatId")
                    gpt_message_id = r_data.get("messageId")
                    gpt_conversation_id = r_data.get("conversationId")
                r_text = r_data.get("content")
                j = j + 1
                if (j % 4 == 0 or j == 1) and r_text:
                    send_lichat_res_message(env, feishu_chat_id, chat_type, r_text, username, loading_message_id, False)
            send_lichat_res_message(env, feishu_chat_id, chat_type, r_text, username, loading_message_id, True)

            logger.info(f"lichat feishu response: username={username}, message_id={gpt_message_id}, "
                             f"chat_id={gpt_chat_id}, gpt_conversation_id={gpt_conversation_id}, content={r_text}")
            # 保存用户本次LiChat返回的消息messageId，会话chatId，用作下次的上下文关联，仅保存私聊内容,包含敏感信息时不返回messageId，沿用之前的messageId
            if chat_type != "group" and gpt_chat_id and gpt_message_id and gpt_conversation_id:
                REDIS.set(user_lichat_context_redis_key, gpt_chat_id + "+" + gpt_message_id + "+" + gpt_conversation_id)
            return {"message_id": gpt_message_id, "chat_id": gpt_chat_id, "conversation_id": gpt_conversation_id, "content": r_text}
        raise Exception("lichat request error")

    except Exception as e:
        logger.error(f"openai error：{e}")
        res = "LiChat error, Sorry about that! Please try again later！"
        RobotOpenApi.send_message(env, feishu_chat_id, feishu_message_id, res, username, False)
        return {}


# 发送loading信息
def send_loading_message(env, feishu_message_id, feishu_chat_id, username):
    message_elements = [{
        "tag": "markdown",
        "content": "收到问题，正在思考..."
    },  {
        "tag": "div",
        "text": {
            "content": "**<font color='green'>努力回复中……</font>**",
            "tag": "lark_md"
        }
    }]
    card_message = MessageCardBase(False, "", "", True).create_message(message_elements)
    send_res = RobotOpenApi.send_message_card(env, feishu_chat_id, feishu_message_id, card_message, username, True)
    return send_res


# 发送lichat回复消息
def send_lichat_res_message(env, feishu_chat_id, chat_type, lichat_res_content, username, update_message_id, is_end):
    card_message = get_lichat_res_message_card(env, feishu_chat_id, chat_type, lichat_res_content, username, is_end)
    update_card_message = card_message.get("card")
    send_res = RobotOpenApi.update_message(env, update_card_message, username, update_message_id, "")
    return send_res


# 拼装回复卡片
def get_lichat_res_message_card(env, feishu_chat_id, chat_type, lichat_res_content, username, is_end):
    if env == "prod":
        callback_url = "https://lichat-im-entry.fc.chj.cloud/newChat"
    else:
        callback_url = "https://lichat-im-entry.dev.fc.chj.cloud/newChat"
    # 组装消息
    if chat_type != "group":
        message_elements = [{
            "tag": "markdown",
            "content": lichat_res_content if lichat_res_content else "我暂时无法回答您的问题，请您稍后再试或更换问题后重试"
        }, {
            "tag": "hr",
        }, {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "模型：MS-GPT-4-turbo"
            },
            "extra": {
                "tag": "button",
                "text": {
                    "tag": "lark_md",
                    "content": "创建新会话"
                },
                "type": "primary",
                "value": {
                    "business": "card_msg_callback",  # 固定值
                    "data": {
                        "callback_url": callback_url,  # 自己定义的回调地址
                        "app_name": "lichat-robot",  # 机器人名称，中台注册时的名称
                        "mode": "none",  # 固定值
                        "feishu_chat_id": feishu_chat_id,
                        "username": username
                    }
                }
            }
        } ]
    else:
        message_elements = [ {
            "tag": "markdown",
            "content": lichat_res_content if lichat_res_content else "我暂时无法回答您的问题，请您稍后再试或更换问题后重试"
        }, {
            "tag": "hr",
        }, {
            "tag": "div",
            "text": {
                "content": "模型：MS-GPT-4-turbo",
                "tag": "plain_text"
            }
        } ]
    if not is_end:
        message_elements.insert(1, {
            "tag": "div",
            "text": {
                "content": "**<font color='green'>努力回复中……</font>**",
                "tag": "lark_md"
            }
        })
    card_message = MessageCardBase(False, "", "", True).create_message(message_elements)
    return card_message


if __name__ == "__main__":
    import argparse

    # init_apm()

    # parser = argparse.ArgumentParser(description='FastApi Run Server Args')
    # parser.add_argument('--port', type=int)
    # args = parser.parse_args()
    # port = args.port
    uvicorn.run(app="main:app", host="0.0.0.0", port=8080)
