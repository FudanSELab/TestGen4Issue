#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-----------------------------------------
@Author: duyi
@Email: yangty21@m.fudan.edu.cn
@Created: 2022/01/04
------------------------------------------
@Modify: 2022/01/04
------------------------------------------
@Description:
"""


class BaseUtil:
    @staticmethod
    def response(code, message, data=None):
        return {'code': code, 'message': message, 'data': data}
