"""
知识点管理控制器
"""
from typing import List
from fastapi import HTTPException
from app.models.knowledge_point import KnowledgePoint
from app.schemas.knowledge_point import KnowledgePointCreate, KnowledgePointUpdate, KnowledgePointOut


class KnowledgePointController:
    """知识点管理控制器"""

    @staticmethod
    async def get_knowledge_points_by_chapter(chapter_id: int) -> List[KnowledgePointOut]:
        """获取章节的所有知识点"""
        knowledge_points = await KnowledgePoint.filter(chapter_id=chapter_id).all()
        return [KnowledgePointOut.from_orm(kp) for kp in knowledge_points]

    @staticmethod
    async def get_knowledge_point(knowledge_point_id: int) -> KnowledgePointOut:
        """获取知识点详情"""
        knowledge_point = await KnowledgePoint.filter(id=knowledge_point_id).first()
        if not knowledge_point:
            raise HTTPException(status_code=404, detail="知识点不存在")
        return KnowledgePointOut.from_orm(knowledge_point)

    @staticmethod
    async def create_knowledge_point(knowledge_point_data: KnowledgePointCreate) -> KnowledgePointOut:
        """创建知识点"""
        knowledge_point = await KnowledgePoint.create(**knowledge_point_data.dict())
        return KnowledgePointOut.from_orm(knowledge_point)

    @staticmethod
    async def update_knowledge_point(
        knowledge_point_id: int, 
        knowledge_point_data: KnowledgePointUpdate
    ) -> KnowledgePointOut:
        """更新知识点"""
        knowledge_point = await KnowledgePoint.filter(id=knowledge_point_id).first()
        if not knowledge_point:
            raise HTTPException(status_code=404, detail="知识点不存在")
        
        update_data = knowledge_point_data.dict(exclude_unset=True)
        await knowledge_point.update_from_dict(update_data).save()
        return KnowledgePointOut.from_orm(knowledge_point)

    @staticmethod
    async def delete_knowledge_point(knowledge_point_id: int) -> None:
        """删除知识点"""
        knowledge_point = await KnowledgePoint.filter(id=knowledge_point_id).first()
        if not knowledge_point:
            raise HTTPException(status_code=404, detail="知识点不存在")
        await knowledge_point.delete()

    @staticmethod
    async def reorder_knowledge_points(knowledge_points_data: List[dict]) -> dict:
        """批量更新知识点顺序"""
        for kp_data in knowledge_points_data:
            knowledge_point = await KnowledgePoint.filter(id=kp_data["id"]).first()
            if knowledge_point:
                knowledge_point.order = kp_data["order"]
                await knowledge_point.save()
        return {"message": "知识点顺序更新成功"}
