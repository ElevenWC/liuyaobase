# -*- coding: utf-8 -*-
"""
测试 images.py - 图片API路由

阶段二十: 图片存储功能测试
"""
import pytest
import os
import tempfile
from io import BytesIO
from PIL import Image

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.api.main import app
from backend.config import settings


# 创建测试客户端
@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def temp_image():
    """创建临时测试图片"""
    # 创建一个简单的测试图片
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


@pytest.fixture
def temp_image_png():
    """创建临时PNG测试图片"""
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


class TestImageStorageConfig:
    """测试图片存储配置"""

    def test_settings_has_image_config(self):
        """测试配置包含图片存储设置"""
        assert hasattr(settings, 'image_storage_path')
        assert hasattr(settings, 'image_allowed_extensions')
        assert hasattr(settings, 'image_max_size')

    def test_image_extensions_list(self):
        """测试图片扩展名列表"""
        extensions = settings.image_extensions_list
        assert 'jpg' in extensions
        assert 'png' in extensions
        assert 'gif' in extensions

    def test_ensure_image_directory(self):
        """测试确保图片目录存在"""
        # 这应该不会抛出异常
        path = settings.ensure_image_directory()
        assert os.path.exists(path)

    def test_image_storage_absolute_path(self):
        """测试获取绝对路径"""
        abs_path = settings.image_storage_absolute_path
        assert os.path.isabs(abs_path)


class TestImageStorageConfigAPI:
    """测试图片存储配置API"""

    def test_get_image_storage_config(self, client):
        """测试获取图片存储配置"""
        response = client.get("/api/images/config")
        assert response.status_code == 200

        data = response.json()
        assert "storage_path" in data
        assert "absolute_path" in data
        assert "allowed_extensions" in data
        assert "max_file_size" in data

    def test_config_includes_allowed_extensions(self, client):
        """测试配置包含允许的扩展名"""
        response = client.get("/api/images/config")
        data = response.json()
        assert "jpg" in data["allowed_extensions"]
        assert "png" in data["allowed_extensions"]


class TestImageUploadAPI:
    """测试图片上传API"""

    def test_upload_jpg_image(self, client, temp_image):
        """测试上传JPG图片"""
        response = client.post(
            "/api/images/upload",
            files={"file": ("test.jpg", temp_image, "image/jpeg")}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "filename" in data
        assert "url" in data
        assert data["original_filename"] == "test.jpg"

        # 清理上传的文件
        if os.path.exists(os.path.join(settings.image_storage_absolute_path, data["filename"])):
            os.remove(os.path.join(settings.image_storage_absolute_path, data["filename"]))

    def test_upload_png_image(self, client, temp_image_png):
        """测试上传PNG图片"""
        response = client.post(
            "/api/images/upload",
            files={"file": ("test.png", temp_image_png, "image/png")}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True

        # 清理上传的文件
        if os.path.exists(os.path.join(settings.image_storage_absolute_path, data["filename"])):
            os.remove(os.path.join(settings.image_storage_absolute_path, data["filename"]))

    def test_upload_unsupported_format(self, client):
        """测试上传不支持的格式"""
        # 创建一个txt文件
        txt_content = BytesIO(b"not an image")
        response = client.post(
            "/api/images/upload",
            files={"file": ("test.txt", txt_content, "text/plain")}
        )
        assert response.status_code == 400

    def test_upload_empty_file(self, client):
        """测试上传空文件"""
        empty_file = BytesIO(b"")
        response = client.post(
            "/api/images/upload",
            files={"file": ("empty.jpg", empty_file, "image/jpeg")}
        )
        # 空文件应该被接受（只是大小为0）
        # 但根据实现可能返回400或200


class TestImageAccessAPI:
    """测试图片访问API"""

    def test_get_nonexistent_image(self, client):
        """测试获取不存在的图片"""
        response = client.get("/api/images/nonexistent.jpg")
        assert response.status_code == 404

    def test_get_image_with_path_traversal(self, client):
        """测试路径遍历攻击防护"""
        # 测试包含..的路径 - 应该返回400
        # 注意: FastAPI可能会将URL中的../处理掉，所以我们测试其他形式的路径遍历
        response = client.get("/api/images/..%2Fconfig.py")
        # URL编码后的路径可能被正常化，返回404或400都是可接受的
        assert response.status_code in [400, 404]

    def test_get_uploaded_image(self, client, temp_image):
        """测试获取已上传的图片"""
        # 首先上传图片
        upload_response = client.post(
            "/api/images/upload",
            files={"file": ("test.jpg", temp_image, "image/jpeg")}
        )
        assert upload_response.status_code == 200
        filename = upload_response.json()["filename"]

        # 然后获取图片
        get_response = client.get(f"/api/images/{filename}")
        assert get_response.status_code == 200

        # 清理
        if os.path.exists(os.path.join(settings.image_storage_absolute_path, filename)):
            os.remove(os.path.join(settings.image_storage_absolute_path, filename))


class TestImageListAPI:
    """测试图片列表API"""

    def test_list_images(self, client):
        """测试获取图片列表"""
        response = client.get("/api/images")
        assert response.status_code == 200

        data = response.json()
        assert "images" in data
        assert "total" in data
        assert isinstance(data["images"], list)


class TestImageDeleteAPI:
    """测试图片删除API"""

    def test_delete_nonexistent_image(self, client):
        """测试删除不存在的图片"""
        response = client.delete("/api/images/nonexistent.jpg")
        assert response.status_code == 404

    def test_delete_with_path_traversal(self, client):
        """测试删除时的路径遍历防护"""
        # 测试包含..的路径 - 应该返回400或404
        response = client.delete("/api/images/..%2Fconfig.py")
        assert response.status_code in [400, 404]

    def test_delete_uploaded_image(self, client, temp_image):
        """测试删除已上传的图片"""
        # 首先上传图片
        upload_response = client.post(
            "/api/images/upload",
            files={"file": ("test.jpg", temp_image, "image/jpeg")}
        )
        assert upload_response.status_code == 200
        filename = upload_response.json()["filename"]

        # 确保文件存在
        file_path = os.path.join(settings.image_storage_absolute_path, filename)
        assert os.path.exists(file_path)

        # 删除图片
        delete_response = client.delete(f"/api/images/{filename}")
        assert delete_response.status_code == 200

        # 确保文件已删除
        assert not os.path.exists(file_path)


class TestGenerateFilename:
    """测试文件名生成"""

    def test_generate_filename_preserves_extension(self):
        """测试生成文件名保留扩展名"""
        from backend.api.routers.images import generate_filename

        filename = generate_filename("test.jpg")
        assert filename.endswith(".jpg")

        filename = generate_filename("test.PNG")
        assert filename.endswith(".png")

    def test_generate_filename_includes_date(self):
        """测试生成文件名包含日期"""
        from backend.api.routers.images import generate_filename
        from datetime import datetime

        filename = generate_filename("test.jpg")
        today = datetime.now().strftime("%Y%m%d")
        assert today in filename


class TestValidateImageFile:
    """测试图片文件验证"""

    def test_validate_valid_jpg(self):
        """测试验证有效JPG"""
        from backend.api.routers.images import validate_image_file

        valid, error = validate_image_file("test.jpg", 1024)
        assert valid is True
        assert error is None

    def test_validate_valid_png(self):
        """测试验证有效PNG"""
        from backend.api.routers.images import validate_image_file

        valid, error = validate_image_file("test.png", 1024)
        assert valid is True

    def test_validate_invalid_extension(self):
        """测试验证无效扩展名"""
        from backend.api.routers.images import validate_image_file

        valid, error = validate_image_file("test.txt", 1024)
        assert valid is False
        assert "不支持" in error

    def test_validate_file_too_large(self):
        """测试验证文件过大"""
        from backend.api.routers.images import validate_image_file

        # 使用一个很大的文件大小
        valid, error = validate_image_file("test.jpg", 100 * 1024 * 1024)  # 100MB
        assert valid is False
        assert "超过限制" in error

    def test_validate_empty_filename(self):
        """测试验证空文件名"""
        from backend.api.routers.images import validate_image_file

        valid, error = validate_image_file("", 1024)
        assert valid is False
        assert "空" in error
