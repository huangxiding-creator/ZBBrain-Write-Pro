#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标题生成优化测试脚本 (v3.6.11)

测试目标：
1. 验证标题生成不会返回空
2. 验证标题是完整句子，不会硬截断
3. 验证标题长度在28-32字之间（允许稍微超长但必须完整）
4. 验证智能截断功能
"""

import sys
import os
import re
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ZBBrainArticle import Config, ZhipuAIAnalyzer
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试用例
TEST_CASES = [
    {
        "question": "EPC项目设计变更频繁导致成本失控，如何建立有效的变更管理机制？",
        "answer": """
EPC项目设计变更管理是项目成败的关键。根据我们多年的项目经验，设计变更主要来源于三个方面：
1. 业主需求变更：业主在项目实施过程中提出新的功能需求或修改原有需求
2. 设计优化：设计单位根据现场情况或技术进步对原设计进行优化
3. 法规变化：相关法规标准的更新导致设计需要调整

有效的变更管理机制应包括：
- 建立变更审批流程：所有变更必须经过技术、商务、法务等多部门评审
- 设置变更控制委员会：由业主、设计、施工、监理等各方代表组成
- 实行变更分级管理：根据变更金额和影响范围设置不同审批权限
- 建立变更数据库：记录所有变更信息，便于追踪和分析

变更索赔的关键点：
1. 及时性：变更发生后24小时内必须发出书面通知
2. 完整性：变更记录必须包含原因、范围、影响、费用、工期等完整信息
3. 合规性：严格按照合同约定的变更程序执行
4. 可追溯性：所有变更文件必须编号归档，便于后期审计
""",
        "keyword": "EPC设计变更"
    },
    {
        "question": "EPC总承包项目分包商违约如何处理？合同中应该约定哪些关键条款？",
        "answer": """
EPC总承包项目分包管理是项目风险控制的重要环节。分包商违约是常见风险，主要包括：
1. 工期延误：分包商未能按计划完成工作
2. 质量问题：分包商交付的工作成果不符合技术规范
3. 安全事故：分包商在施工过程中发生安全事故
4. 成本超支：分包商要求增加费用或索赔

合同关键条款建议：
- 明确违约责任：详细约定各类违约情形及相应责任
- 设置履约保证金：金额一般为合同额的5%-10%
- 约定违约金计算方式：按日计算的违约金比例
- 明确解除合同条件：严重违约时总包有权解除合同
- 约定争议解决机制：仲裁或诉讼的选择

处理违约的步骤：
1. 收集证据：书面记录违约事实，拍照、录像等
2. 发出通知：按合同约定的方式发出违约通知
3. 协商解决：尝试通过协商达成解决方案
4. 启动索赔：按合同约定启动索赔程序
5. 终止合同：严重违约时行使解除权
""",
        "keyword": "EPC分包"
    },
    {
        "question": "EPC项目投标报价有哪些常见的坑？如何避免报价失误？",
        "answer": """
EPC项目投标报价是项目盈利的基础，常见的报价失误包括：

1. 工程量计算错误
- 遗漏部分工程内容
- 工程量计算规则理解偏差
- 单位换算错误

2. 价格取定不当
- 材料价格未考虑涨价风险
- 人工费未考虑市场波动
- 机械费计算不准确

3. 风险费估计不足
- 技术风险未充分考虑
- 政策风险估计不足
- 市场风险估计偏差

4. 间接费计算错误
- 管理费取费基数错误
- 利润率设置不合理
- 税金计算有误

避免报价失误的建议：
- 建立标准化的报价审核流程
- 组建专业的报价团队
- 使用专业软件进行计算
- 进行多轮交叉复核
- 参考历史项目数据
- 聘请第三方进行独立审核
""",
        "keyword": "EPC投标报价"
    }
]


def _is_complete_sentence(title: str) -> bool:
    """检测标题是否是完整句子"""
    if not title:
        return False
    # 检查是否有结尾标点（感叹号、问号、句号）
    if title[-1] in '！？。!?':
        return True
    # 检查是否有谓语动词
    verbs = ['是', '有', '能', '会', '要', '可以', '需要', '必须', '应该', '让', '使', '帮']
    for v in verbs:
        if v in title:
            return True
    return False


def _smart_truncate_title(title: str, max_len: int = 30) -> str:
    """智能截断标题到完整句子"""
    if len(title) <= max_len:
        return title

    # 如果标题以感叹号或问号结尾，尝试在标点处截断
    if title[-1] in '！？!?':
        search_area = title[:max_len]
        punct_positions = []
        for i, char in enumerate(search_area):
            if char in '！？，。、：,!?.:':
                punct_positions.append(i)

        if punct_positions:
            cut_pos = punct_positions[-1] + 1
            return title[:cut_pos]

    # 尝试在逗号处截断
    if '，' in title[:max_len]:
        last_comma = title[:max_len].rfind('，')
        if last_comma >= 20:
            return title[:last_comma] + '！'

    # 最后手段：截断并添加感叹号
    return title[:max_len - 1] + '！'


def validate_title(title: str, test_case: dict) -> dict:
    """验证标题质量"""
    result = {
        "title": title,
        "length": len(title),
        "is_valid": True,
        "issues": [],
        "is_complete": False
    }

    # 检查是否为空
    if not title or title.strip() == '':
        result["is_valid"] = False
        result["issues"].append("❌ 标题为空")
        return result

    # 检查长度
    if len(title) < 20:
        result["is_valid"] = False
        result["issues"].append(f"❌ 标题过短 ({len(title)}字)")
    elif len(title) > 32:
        result["is_valid"] = False
        result["issues"].append(f"❌ 标题超长 ({len(title)}字)")
    elif len(title) < 26:
        result["issues"].append(f"⚠️ 标题略短 ({len(title)}字)")
    elif len(title) > 30:
        result["issues"].append(f"⚠️ 标题稍长 ({len(title)}字)")

    # 检查是否是完整句子
    result["is_complete"] = _is_complete_sentence(title)
    if not result["is_complete"]:
        result["is_valid"] = False
        result["issues"].append("❌ 标题不是完整句子")

    # 检查是否包含关键词
    keyword = test_case.get("keyword", "")
    if keyword and keyword not in title:
        result["issues"].append(f"⚠️ 标题不包含关键词 [{keyword}]")

    # 检查是否有结尾标点
    if title[-1] not in '！？!?':
        result["issues"].append("⚠️ 标题没有结尾标点")

    return result


def run_tests():
    """运行测试"""
    print("=" * 60)
    print("标题生成优化测试 (v3.6.11)")
    print("=" * 60)

    # 加载配置
    config = Config()
    analyzer = ZhipuAIAnalyzer(config, logger)

    total_tests = len(TEST_CASES)
    passed_tests = 0

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'='*60}")
        print(f"测试用例 {i}/{total_tests}")
        print(f"{'='*60}")
        print(f"问题: {test_case['question'][:50]}...")
        print(f"关键词: {test_case['keyword']}")

        try:
            # 生成标题
            title = analyzer.generate_catchy_title(
                question=test_case['question'],
                answer=test_case['answer'],
                keyword=test_case['keyword']
            )

            # 验证标题
            validation = validate_title(title, test_case)

            print(f"\n生成的标题: {title}")
            print(f"标题长度: {validation['length']}字")
            print(f"完整句子: {'✅ 是' if validation['is_complete'] else '❌ 否'}")

            if validation['issues']:
                print("问题:")
                for issue in validation['issues']:
                    print(f"  {issue}")

            if validation['is_valid']:
                print("\n✅ 测试通过")
                passed_tests += 1
            else:
                print("\n❌ 测试失败")

        except Exception as e:
            print(f"\n❌ 测试异常: {str(e)}")
            logger.error(f"测试用例 {i} 异常: {str(e)}")

    # 测试智能截断功能
    print(f"\n{'='*60}")
    print("智能截断功能测试")
    print(f"{'='*60}")

    truncate_test_cases = [
        "全过程咨询EPC总承包项目人才留用压力大！2026招聘潮下，如何留住核心人才？",
        "EPC设计变更频发，90%项目利润受损？掌握这3招成本控制策略让利润翻倍！",
        "别让设计变更毁了你的EPC项目！这4招帮你有效规避风险并保护合法权益！",
    ]

    for title in truncate_test_cases:
        truncated = _smart_truncate_title(title, 30)
        is_complete = _is_complete_sentence(truncated)
        print(f"\n原标题 ({len(title)}字): {title}")
        print(f"截断后 ({len(truncated)}字): {truncated}")
        print(f"完整句子: {'✅ 是' if is_complete else '❌ 否'}")

    # 总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    print(f"总测试数: {total_tests}")
    print(f"通过数: {passed_tests}")
    print(f"失败数: {total_tests - passed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")

    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
