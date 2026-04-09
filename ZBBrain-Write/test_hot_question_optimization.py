#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热点问题生成优化测试脚本 (v3.6.12)

测试目标：
1. 验证热点问题针对非常具体的业务场景
2. 验证热点问题字数超过50字（越多越好）
3. 验证热点问题包含具体业务场景词
"""

import sys
import os
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ZBBrainArticle import Config, ZhipuAIAnalyzer, ContentQualityScorer
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 模拟文章数据（来自搜狗微信爬取的真实文章）
MOCK_ARTICLES = [
    {
        "title": "EPC总承包项目设计变更管理要点分析",
        "summary": "设计变更管理是EPC总承包项目成本控制的关键环节。本文分析了设计变更的主要原因、变更费用的构成以及变更索赔的关键要点。",
        "keywords": ["设计变更", "成本控制", "索赔"]
    },
    {
        "title": "EPC项目分包商违约风险防范措施",
        "summary": "分包商违约是EPC项目常见风险之一。本文从合同条款设计、过程监管、违约处理等方面提出了系统的风险防范措施。",
        "keywords": ["分包商", "违约风险", "合同管理"]
    },
    {
        "title": "EPC项目投标报价常见误区及应对策略",
        "summary": "投标报价是EPC项目盈利的基础。本文总结了投标报价中常见的工程量计算错误、价格取定不当、风险费估计不足等问题及应对策略。",
        "keywords": ["投标报价", "工程量", "风险费"]
    }
]


def validate_question_quality(question: str, quality_scorer: ContentQualityScorer) -> dict:
    """验证热点问题质量"""
    result = {
        "question": question,
        "length": len(question),
        "is_valid": True,
        "issues": [],
        "score": 0,
        "specific_scene_count": 0
    }

    # 使用质量评分器评分
    quality_result = quality_scorer.score_question(question)
    result["score"] = quality_result["score"]
    result["specific_scene_count"] = quality_result["details"].get("specific_scene_count", 0)

    # 检查字数
    if len(question) < 50:
        result["is_valid"] = False
        result["issues"].append(f"❌ 字数不足50字 ({len(question)}字)")
    elif len(question) < 60:
        result["issues"].append(f"⚠️ 字数刚达标 ({len(question)}字)，建议80字以上")
    elif len(question) < 80:
        result["issues"].append(f"⚠️ 字数良好 ({len(question)}字)，建议80字以上")
    else:
        result["issues"].append(f"✅ 字数优秀 ({len(question)}字)")

    # 检查具体场景词
    if result["specific_scene_count"] < 1:
        result["is_valid"] = False
        result["issues"].append("❌ 缺少具体业务场景词")
    elif result["specific_scene_count"] < 2:
        result["issues"].append("⚠️ 具体场景词较少，建议增加")
    else:
        result["issues"].append(f"✅ 包含{result['specific_scene_count']}个具体场景词")

    # 检查问句格式
    if not (question.endswith('？') or question.endswith('?')):
        result["is_valid"] = False
        result["issues"].append("❌ 问题不以问号结尾")

    question_words = ['如何', '怎样', '为什么', '什么', '哪些', '怎么', '能否', '是否']
    if not any(w in question for w in question_words):
        result["is_valid"] = False
        result["issues"].append("❌ 缺少疑问词")

    return result


def run_tests():
    """运行测试"""
    print("=" * 70)
    print("热点问题生成优化测试 (v3.6.12)")
    print("=" * 70)

    # 加载配置
    config = Config()
    analyzer = ZhipuAIAnalyzer(config, logger)
    quality_scorer = ContentQualityScorer(logger)

    print(f"\n📝 测试配置:")
    print(f"   模型: {config.zhipu_model_fast}")
    print(f"   最小问题评分: {80}分")

    # 测试3次生成
    test_count = 3
    passed_tests = 0
    total_length = 0

    for i in range(test_count):
        print(f"\n{'='*70}")
        print(f"测试 {i+1}/{test_count}")
        print(f"{'='*70}")

        try:
            # 生成热点问题
            question = analyzer.generate_hot_question(MOCK_ARTICLES)

            # 验证质量
            validation = validate_question_quality(question, quality_scorer)

            print(f"\n生成的热点问题:")
            print(f"   {question}")
            print(f"\n质量评估:")
            print(f"   字数: {validation['length']}字")
            print(f"   评分: {validation['score']}分")
            print(f"   具体场景词数: {validation['specific_scene_count']}个")
            print(f"\n评估结果:")
            for issue in validation['issues']:
                print(f"   {issue}")

            if validation['is_valid']:
                print("\n✅ 测试通过")
                passed_tests += 1
                total_length += validation['length']
            else:
                print("\n❌ 测试失败")

        except Exception as e:
            print(f"\n❌ 测试异常: {str(e)}")
            logger.error(f"测试 {i+1} 异常: {str(e)}")

    # 测试备用问题质量
    print(f"\n{'='*70}")
    print("备用问题质量测试")
    print(f"{'='*70}")

    backup_questions = [
        "在EPC总承包项目的设计变更管理过程中，当业主频繁提出功能性变更需求且拒绝承担由此产生的工期延误和成本增加费用时，总承包商应如何通过合同条款约定和现场证据保全来有效维护自身的合法权益并实现合理索赔？",
        "EPC总承包项目在分包商选择和管理过程中，面对分包商工期延误、质量不达标、人员不足等多重违约风险，总承包商应如何在合同中设置预防性条款和违约责任，以及在执行过程中如何进行有效监管和及时止损？",
        "在EPC项目投标报价阶段，面对招标文件中的技术参数模糊、工程量清单不完整、合同条款存在明显陷阱等情况，投标团队应如何通过技术经济分析识别潜在风险，并在报价中合理预留风险准备金以避免中标后亏损？",
    ]

    for i, question in enumerate(backup_questions, 1):
        validation = validate_question_quality(question, quality_scorer)
        print(f"\n备用问题 {i}:")
        print(f"   {question[:60]}...")
        print(f"   字数: {validation['length']}字, 评分: {validation['score']}分")
        print(f"   状态: {'✅ 通过' if validation['is_valid'] else '❌ 失败'}")

    # 总结
    print(f"\n{'='*70}")
    print("测试总结")
    print(f"{'='*70}")
    print(f"总测试数: {test_count}")
    print(f"通过数: {passed_tests}")
    print(f"失败数: {test_count - passed_tests}")
    print(f"通过率: {passed_tests/test_count*100:.1f}%")
    if passed_tests > 0:
        print(f"平均字数: {total_length/passed_tests:.1f}字")

    return passed_tests == test_count


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
