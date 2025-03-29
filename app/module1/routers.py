#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: duyi
@Email: yangty21@m.fudan.edu.cn
@Created: 2022/01/06
------------------------------------------
@Modify: 2022/01/06
------------------------------------------
@Description:
"""
from fastapi import APIRouter

from app.util.base_util import BaseUtil

module1_router = APIRouter()


@module1_router.get('/')
async def root():
    return {'message': 'Hello Module1!'}


@module1_router.get("/hello/{name}")
async def say_hello(name: str):
    return BaseUtil.response(1, f"Hello {name}")