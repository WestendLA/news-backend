"""测试 utils/response.py —— 统一响应格式。

这也是纯函数测试，但返回值是 FastAPI 的 JSONResponse 对象。
"""

import json
from utils.response import success_response


class TestSuccessResponse:
    """测试 success_response 函数"""

    def test_default_status_code_is_200(self):
        """默认状态码应该是 200"""
        resp = success_response(data={"id": 1})

        assert resp.status_code == 200

    def test_response_body_is_valid_json(self):
        """返回的 body 必须是合法 JSON"""
        resp = success_response(data={"name": "test"})

        # JSONResponse.body 是 bytes，需要解码
        body = json.loads(resp.body)
        assert isinstance(body, dict)

    def test_data_field_in_response(self):
        """data 字段应该正确传递"""
        resp = success_response(data={"username": "tom"})

        body = json.loads(resp.body)
        assert body["data"] == {"username": "tom"}

    def test_default_message(self):
        """不传 message 时，默认应该是 'success'"""
        resp = success_response(data=None)

        body = json.loads(resp.body)
        assert body["message"] == "success"

    def test_custom_message(self):
        """传入自定义 message"""
        resp = success_response(message="操作成功", data=None)

        body = json.loads(resp.body)
        assert body["message"] == "操作成功"

    def test_code_field_is_200(self):
        """响应体中的 code 字段始终为 200"""
        resp = success_response(data=[])

        body = json.loads(resp.body)
        assert body["code"] == 200

    def test_data_is_none(self):
        """data 为 None 时也能正常工作"""
        resp = success_response(data=None)

        body = json.loads(resp.body)
        assert body["data"] is None
