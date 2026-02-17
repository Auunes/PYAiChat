import ipaddress
from typing import Optional


def is_ip_in_range(ip: str, ip_range: str) -> bool:
    """
    检查 IP 是否在指定范围内
    支持单个 IP 和 CIDR 格式
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        network = ipaddress.ip_network(ip_range, strict=False)
        return ip_obj in network
    except ValueError:
        return False


def estimate_tokens(text: str) -> int:
    """
    估算文本的 token 数量
    简单估算：1 token ≈ 4 个字符（英文）或 1.5 个字符（中文）
    """
    # 统计中文字符数
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    # 统计其他字符数
    other_chars = len(text) - chinese_chars

    # 估算 tokens
    tokens = int(chinese_chars / 1.5 + other_chars / 4)
    return max(tokens, 1)
