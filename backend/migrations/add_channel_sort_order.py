"""
添加渠道排序字段

运行方式：
python migrations/add_channel_sort_order.py
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine


async def migrate():
    """执行迁移"""
    async with engine.begin() as conn:
        # 检查列是否已存在
        result = await conn.execute(
            text("PRAGMA table_info(channels)")
        )
        columns = [row[1] for row in result.fetchall()]

        if 'sort_order' not in columns:
            print("添加 sort_order 字段...")
            await conn.execute(
                text("ALTER TABLE channels ADD COLUMN sort_order INTEGER DEFAULT 0 NOT NULL")
            )

            # 为现有渠道设置排序值（按ID顺序）
            await conn.execute(
                text("""
                    UPDATE channels
                    SET sort_order = id * 10
                """)
            )
            print("迁移完成！")
        else:
            print("sort_order 字段已存在，跳过迁移")


if __name__ == "__main__":
    asyncio.run(migrate())
