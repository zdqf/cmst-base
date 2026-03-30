"""Seed script — populate database with initial data for development."""

import asyncio
import uuid
from decimal import Decimal

from sqlalchemy import select, text

from app.database import async_session_factory, engine, Base
from app.models.user import User
from app.models.herb import Herb
from app.models.product import Product
from app.models.prompt_template import PromptTemplate
from app.models.compliance_word import ComplianceWord


async def seed():
    async with async_session_factory() as db:
        # Check if already seeded
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Database already has data, skipping seed.")
            return

        print("Seeding database...")

        # ===== Admin user =====
        admin = User(phone="13800000000", nickname="管理员", is_admin=True)
        db.add(admin)

        # ===== Test user =====
        test_user = User(phone="13900000001", nickname="测试用户")
        db.add(test_user)

        # ===== Herbs =====
        herbs_data = [
            {"name": "黄芪", "category": "补益药", "origin_and_form": "豆科植物蒙古黄芪或膜荚黄芪的干燥根。主产于内蒙古、山西、甘肃等地。秋季采挖，除去须根和根头，晒干。", "flavor_meridian": "甘，微温。归肺、脾经。", "common_pairings": "常与人参、白术、茯苓配伍，用于补气健脾；与当归配伍，用于补气生血。", "unsuitable_groups": "表实邪盛、气滞湿阻、食积内停、阴虚阳亢者慎用。", "precautions": "不宜与龟甲、白鲜皮同用。用量一般为9-30g。"},
            {"name": "当归", "category": "补益药", "origin_and_form": "伞形科植物当归的干燥根。主产于甘肃、云南、四川等地。", "flavor_meridian": "甘、辛，温。归肝、心、脾经。", "common_pairings": "与黄芪配伍补气生血，与川芎、白芍、熟地黄组成四物汤。", "unsuitable_groups": "湿盛中满、大便溏泄者慎用。", "precautions": "用量一般为6-12g。酒当归活血作用增强。"},
            {"name": "枸杞子", "category": "补益药", "origin_and_form": "茄科植物宁夏枸杞的干燥成熟果实。主产于宁夏、甘肃、青海等地。", "flavor_meridian": "甘，平。归肝、肾经。", "common_pairings": "与菊花配伍明目，与熟地黄、山茱萸配伍滋补肝肾。", "unsuitable_groups": "外邪实热、脾虚有湿及泄泻者慎用。", "precautions": "用量一般为6-12g。"},
            {"name": "金银花", "category": "清热药", "origin_and_form": "忍冬科植物忍冬的干燥花蕾或带初开的花。主产于山东、河南等地。", "flavor_meridian": "甘，寒。归肺、心、胃经。", "common_pairings": "与连翘配伍清热解毒，与菊花配伍疏散风热。", "unsuitable_groups": "脾胃虚寒及气虚疮疡脓清者慎用。", "precautions": "用量一般为6-15g。"},
            {"name": "菊花", "category": "清热药", "origin_and_form": "菊科植物菊的干燥头状花序。主产于浙江、安徽、河南等地。", "flavor_meridian": "甘、苦，微寒。归肺、肝经。", "common_pairings": "与枸杞配伍明目，与桑叶配伍疏散风热。", "unsuitable_groups": "气虚胃寒、食少泄泻者慎用。", "precautions": "用量一般为5-10g。"},
            {"name": "板蓝根", "category": "清热药", "origin_and_form": "十字花科植物菘蓝的干燥根。主产于河北、江苏、安徽等地。", "flavor_meridian": "苦，寒。归心、胃经。", "common_pairings": "与金银花、连翘配伍清热解毒。", "unsuitable_groups": "体虚而无实火热毒者慎用。", "precautions": "用量一般为9-15g。"},
            {"name": "人参", "category": "补益药", "origin_and_form": "五加科植物人参的干燥根和根茎。主产于吉林、辽宁、黑龙江等地。", "flavor_meridian": "甘、微苦，微温。归脾、肺、心、肾经。", "common_pairings": "与黄芪配伍大补元气，与白术、茯苓组成四君子汤。", "unsuitable_groups": "实证、热证者慎用。不宜与藜芦同用。", "precautions": "用量一般为3-9g。"},
            {"name": "陈皮", "category": "理气药", "origin_and_form": "芸香科植物橘及其栽培变种的干燥成熟果皮。主产于广东、福建等地。", "flavor_meridian": "苦、辛，温。归脾、肺经。", "common_pairings": "与半夏配伍燥湿化痰，与白术配伍健脾理气。", "unsuitable_groups": "气虚体燥、阴虚燥咳、吐血者慎用。", "precautions": "用量一般为3-10g。陈化时间越长品质越佳。"},
            {"name": "丹参", "category": "活血药", "origin_and_form": "唇形科植物丹参的干燥根和根茎。主产于四川、安徽、河南等地。", "flavor_meridian": "苦，微寒。归心、肝经。", "common_pairings": "与黄芪配伍益气活血，与三七配伍化瘀止痛。", "unsuitable_groups": "无瘀血者慎用，孕妇慎用。", "precautions": "用量一般为10-15g。不宜与藜芦同用。"},
            {"name": "茯苓", "category": "补益药", "origin_and_form": "多孔菌科真菌茯苓的干燥菌核。主产于云南、安徽、湖北等地。", "flavor_meridian": "甘、淡，平。归心、肺、脾、肾经。", "common_pairings": "与白术配伍健脾利湿，与人参、黄芪配伍补气健脾。", "unsuitable_groups": "虚寒精滑或气虚下陷者慎用。", "precautions": "用量一般为10-15g。"},
        ]
        for h in herbs_data:
            db.add(Herb(**h))

        # ===== Products =====
        products_data = [
            {"name": "精选黄芪片 250g", "category": "原药材", "price": Decimal("38.00"), "specification": "250g/袋", "description": "甘肃道地黄芪，精选大片，色泽金黄，质地紧实。适合日常煲汤、泡水。", "stock": 200},
            {"name": "宁夏枸杞王 500g", "category": "原药材", "price": Decimal("68.00"), "specification": "500g/罐", "description": "宁夏中宁特级枸杞，颗粒饱满，色泽鲜红，甘甜可口。", "stock": 150},
            {"name": "当归头片 200g", "category": "原药材", "price": Decimal("45.00"), "specification": "200g/袋", "description": "甘肃岷县当归头，油性足，香气浓郁，补血佳品。", "stock": 100},
            {"name": "金银花茶 100g", "category": "简加工产品", "price": Decimal("32.00"), "specification": "100g/罐", "description": "河南封丘金银花，手工采摘，低温烘干，花蕾完整。", "stock": 300},
            {"name": "菊花枸杞茶包 30袋", "category": "简加工产品", "price": Decimal("28.00"), "specification": "30袋/盒", "description": "精选杭白菊与宁夏枸杞科学配比，独立茶包，方便冲泡。", "stock": 500},
            {"name": "四物汤料包", "category": "调理组合包", "price": Decimal("58.00"), "specification": "10包/盒", "description": "当归、川芎、白芍、熟地黄经典配方，每包独立包装。", "stock": 80},
            {"name": "补气养血组合", "category": "调理组合包", "price": Decimal("88.00"), "specification": "7天量/盒", "description": "黄芪、当归、党参、大枣科学配比，适合气血两虚人群。", "stock": 60},
            {"name": "陈皮丝 150g", "category": "简加工产品", "price": Decimal("25.00"), "specification": "150g/袋", "description": "广东新会陈皮，陈化三年以上，香气醇厚，理气健脾。", "stock": 200},
        ]
        for p in products_data:
            db.add(Product(**p))

        # ===== Prompt Templates =====
        prompts = [
            {"type": "health_advisor", "role_name": "健康顾问", "content": "你是一位专业的中医健康顾问。请根据用户提供的健康信息，从传统中医角度给出调理方向建议。注意：你不是医生，不能做医疗诊断或开处方，只能提供中医养生调理方向的参考建议。回答要专业、温和、有条理。", "version": 1, "is_active": True},
            {"type": "pairing_assistant", "role_name": "科普助手", "content": "你是一位中药科普助手。请根据用户选择的中药，分析它们的搭配思路，说明各药材的传统功效方向、注意事项和不适合人群。注意使用科普语言，避免医疗诊断用语。", "version": 1, "is_active": True},
            {"type": "content_generator", "role_name": "科普内容生成", "content": "你是一位中药百科内容编辑。请为指定的中药生成科普内容，包括：来源与形态、性味归经、常见搭配方向、不适合人群、注意事项。内容要准确、专业、通俗易懂。", "version": 1, "is_active": True},
        ]
        for p in prompts:
            db.add(PromptTemplate(**p))

        # ===== Compliance Words =====
        words = [
            {"forbidden_word": "治愈", "replacement": "调理方向"},
            {"forbidden_word": "治疗", "replacement": "健康参考"},
            {"forbidden_word": "疗效承诺", "replacement": "传统用法参考"},
            {"forbidden_word": "根治", "replacement": "调理建议"},
            {"forbidden_word": "药效", "replacement": "传统功效"},
            {"forbidden_word": "处方", "replacement": "搭配思路"},
        ]
        for w in words:
            db.add(ComplianceWord(**w))

        await db.commit()
        print("Seed complete! Created:")
        print("  - 1 admin user (phone: 13800000000)")
        print("  - 1 test user (phone: 13900000001)")
        print("  - 10 herbs")
        print("  - 8 products")
        print("  - 3 prompt templates")
        print("  - 6 compliance words")
        print("\nLogin with phone: 13800000000, code: 123456 (admin)")
        print("Login with phone: 13900000001, code: 123456 (user)")


if __name__ == "__main__":
    asyncio.run(seed())
