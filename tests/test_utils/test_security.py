"""测试 utils/security.py —— bcrypt 密码加密与校验。

这是最基础的「纯函数」单元测试：
- 不依赖数据库
- 不依赖网络
- 不依赖文件系统
- 输入确定 → 输出确定（或行为确定）
"""

from utils.security import get_hashed_password, verify_password


class TestGetHashedPassword:
    """测试密码加密函数 get_hashed_password"""

    def test_returns_string(self):
        """加密后应该返回字符串类型"""
        # Arrange: 准备明文密码
        plain = "123456"

        # Act: 调用加密函数
        result = get_hashed_password(plain)

        # Assert: 验证结果是字符串
        assert isinstance(result, str)

    def test_result_different_from_plain(self):
        """加密结果不应该和原文一样（否则等于没加密）"""
        plain = "mypassword"

        result = get_hashed_password(plain)

        assert result != plain

    def test_same_password_produces_different_hash(self):
        """同一密码加密两次，结果不同 —— bcrypt 每次用随机 salt"""
        plain = "123456"

        hash1 = get_hashed_password(plain)
        hash2 = get_hashed_password(plain)

        # 两次结果不同，说明 salt 在起作用
        assert hash1 != hash2

    def test_result_starts_with_bcrypt_prefix(self):
        """bcrypt 哈希以 $2b$ 开头"""
        result = get_hashed_password("hello")

        assert result.startswith("$2b$")


class TestVerifyPassword:
    """测试密码校验函数 verify_password"""

    def test_correct_password_returns_true(self):
        """正确密码校验返回 True"""
        # Arrange: 先加密
        hashed = get_hashed_password("secret123")

        # Act: 用正确密码校验
        result = verify_password("secret123", hashed)

        # Assert
        assert result is True

    def test_wrong_password_returns_false(self):
        """错误密码校验返回 False"""
        hashed = get_hashed_password("secret123")

        result = verify_password("wrong_password", hashed)

        assert result is False

    def test_empty_password(self):
        """空密码也能正常加密和校验"""
        hashed = get_hashed_password("")

        assert verify_password("", hashed) is True
        assert verify_password("x", hashed) is False
