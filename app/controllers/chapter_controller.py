"""
章节管理控制器
"""
from typing import List, Optional
from fastapi import HTTPException
from app.models.chapter import Chapter
from app.schemas.chapter import ChapterCreate, ChapterUpdate, ChapterOut


class ChapterController:
    """章节管理控制器"""

    @staticmethod
    async def get_chapters_by_course(course_id: int) -> List[ChapterOut]:
        """获取课程的所有章节"""
        chapters = await Chapter.filter(course_id=course_id).order_by('order')
        return [ChapterOut.from_orm(chapter) for chapter in chapters]

    @staticmethod
    async def get_chapter(chapter_id: int) -> ChapterOut:
        """获取章节详情"""
        chapter = await Chapter.filter(id=chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="章节不存在")
        return ChapterOut.from_orm(chapter)

    @staticmethod
    async def create_chapter(chapter_data: ChapterCreate) -> ChapterOut:
        """创建章节"""
        # 获取当前课程的最大order值
        max_order_chapter = await Chapter.filter(
            course_id=chapter_data.course_id
        ).order_by('-order').first()
        
        # 如果没有指定order，则设置为最大值+1
        if chapter_data.order == 0:
            chapter_data.order = (max_order_chapter.order + 1) if max_order_chapter else 1
        
        chapter = await Chapter.create(**chapter_data.dict())
        return ChapterOut.from_orm(chapter)

    @staticmethod
    async def update_chapter(chapter_id: int, chapter_data: ChapterUpdate) -> ChapterOut:
        """更新章节"""
        chapter = await Chapter.filter(id=chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="章节不存在")
        
        update_data = chapter_data.dict(exclude_unset=True)
        await chapter.update_from_dict(update_data).save()
        return ChapterOut.from_orm(chapter)

    @staticmethod
    async def delete_chapter(chapter_id: int) -> None:
        """删除章节"""
        chapter = await Chapter.filter(id=chapter_id).first()
        if not chapter:
            raise HTTPException(status_code=404, detail="章节不存在")
        await chapter.delete()

    @staticmethod
    async def reorder_chapters(chapters: List[dict]) -> dict:
        """
        批量更新章节顺序
        :param chapters: 章节列表，每个元素包含 id 和 order_num
        :return: 更新结果
        """
        updated_count = 0
        for chapter_data in chapters:
            chapter_id = chapter_data.get('id')
            # Support both 'order_num' and 'order' field names
            order_value = chapter_data.get('order_num') or chapter_data.get('order')
            
            if chapter_id is None or order_value is None:
                continue
            
            chapter = await Chapter.filter(id=chapter_id).first()
            if chapter:
                chapter.order = order_value
                await chapter.save()
                updated_count += 1
        
        return {
            "message": f"成功更新 {updated_count} 个章节的顺序",
            "updated_count": updated_count
        }
