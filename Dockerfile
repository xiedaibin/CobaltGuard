# 1. 基础镜像：Python 3.10 slim 版本
FROM python:3.10.14-slim

# 2. 替换为阿里云镜像源以加速构建 (兼容新旧两种 Debian 源配置格式)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || true && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || true && \
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
        sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources; \
    fi

# 3. 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Asia/Shanghai

# 4. 安装基础系统工具（Matplotlib 等渲染需要）
RUN apt-get update && apt-get install -y \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 5. 复制依赖并安装 (使用阿里云 PyPI 镜像)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 6. 复制源码及相关文件
COPY src/ /app/src/

# 7. 安装中文字体支持 (Matplotlib 生成图片使用)
RUN mkdir -p /usr/share/fonts/truetype/wqy && \
    cp /app/src/fonts/wqy-zenhei.ttc /usr/share/fonts/truetype/wqy/ && \
    fc-cache -fv

# 确保必要的运行时目录存在（不依赖宿主机路径）
RUN mkdir -p /app/data /app/logs

COPY test_init.py /app/test_init.py

# 8. 设置持久化卷
VOLUME ["/app/data", "/app/logs"]

# 9. 暴露 FastAPI 端口
EXPOSE 8000

# 10. 启动应用
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
