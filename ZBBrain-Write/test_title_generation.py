#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ZBBrain-Write 标题生成测试脚本
v3.6.10 - 验证AI返回空问题修复

测试目标：
1. 验证重试机制工作正常
2. 验证空响应被正确处理
3. 验证最终生成高质量标题
"""

import sys
import os

# 设置控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ZBBrainArticle import ZhipuAIAnalyzer, Config, Logger, Constants

def test_title_generation():
    """测试标题生成功能"""

    print("=" * 60)
    print("[TEST] ZBBrain-Write 标题生成测试 v3.6.10")
    print("=" * 60)

    # 初始化配置
    config = Config("config.ini")
    logger = Logger(config.log_file_path, debug_mode=True)

    # 创建AI分析器
    analyzer = ZhipuAIAnalyzer(config, logger)

    # 测试用例
    test_cases = [
        {
            "question": "在EPC总承包项目投标与实施过程中，面对2026年公务员、国企及事业单位大规模招聘带来的激烈人才竞争，项目经理应如何制定针对性的留人策略和人才配置方案？",
            "answer": """
EPC总承包项目人才留用策略分析

一、人才竞争现状分析
2026年公务员、国企及事业单位大规模招聘确实给EPC总承包行业带来了较大的人才竞争压力。项目经理需要从多个维度制定针对性的留人策略。

二、核心留人策略
1. 薪酬竞争力保障
   - 建立市场薪酬调研机制，确保核心岗位薪酬不低于市场75分位
   - 设计项目奖金激励机制，将个人收益与项目效益挂钩
   - 提供专项津贴（如驻场补贴、技术津贴等）

2. 职业发展通道
   - 明确技术序列和管理序列双通道发展路径
   - 提供专业培训机会，如注册建造师、造价工程师等
   - 建立导师制度，加速人才成长

3. 工作环境优化
   - 改善项目部生活条件
   - 合理安排工作强度，避免过度加班
   - 建立团队文化，增强归属感

4. 情感激励措施
   - 定期团建活动
   - 家属关怀计划
   - 荣誉表彰体系

三、实施建议
项目经理应在项目启动初期就制定完整的人才保留计划，并定期评估效果，及时调整策略。
""",
            "keyword": "全过程咨询"
        },
        {
            "question": "EPC总承包项目设计变更频繁导致成本超支，如何有效控制设计变更对项目利润的影响？",
            "answer": """
EPC项目设计变更成本控制策略

设计变更是EPC项目成本超支的主要原因之一，需要建立系统的控制机制。

一、设计变更来源分析
1. 业主需求变化
2. 设计深度不足
3. 现场条件变化
4. 法规标准更新

二、成本控制措施
1. 建立变更审批流程
   - 设置变更金额阈值
   - 分级审批机制
   - 变更影响评估

2. 合同条款优化
   - 明确变更计价原则
   - 设置变更管理费
   - 约定变更响应时限

3. 设计阶段控制
   - 加强设计评审
   - BIM技术应用
   - 设计优化激励机制

三、索赔策略
1. 及时记录变更指令
2. 完善变更签证
3. 建立变更台账
""",
            "keyword": "设计变更"
        }
    ]

    # 运行测试
    results = []
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"[TEST CASE {i}]")
        print(f"   问题: {case['question'][:50]}...")
        print(f"   关键词: {case['keyword']}")
        print(f"{'='*60}")

        try:
            title = analyzer.generate_catchy_title(
                question=case['question'],
                answer=case['answer'],
                keyword=case['keyword']
            )

            # 验证结果
            is_valid = True
            issues = []

            if not title:
                is_valid = False
                issues.append("标题为空")
            elif len(title) < 10:
                is_valid = False
                issues.append(f"标题过短 ({len(title)}字)")
            elif len(title) > 30:
                is_valid = False
                issues.append(f"标题超长 ({len(title)}字)")
            elif case['keyword'] and case['keyword'] not in title:
                issues.append(f"标题不包含关键词「{case['keyword']}」")
                # 关键词缺失不算失败，只是警告

            result = {
                'case': i,
                'title': title,
                'length': len(title),
                'is_valid': is_valid,
                'issues': issues
            }
            results.append(result)

            # 输出结果
            status = "[PASS]" if is_valid else "[FAIL]"
            print(f"\n{status}")
            print(f"   生成标题: {title}")
            print(f"   标题长度: {len(title)}字")
            if issues:
                print(f"   [WARN] 问题: {', '.join(issues)}")

        except Exception as e:
            results.append({
                'case': i,
                'title': None,
                'length': 0,
                'is_valid': False,
                'issues': [f"异常: {str(e)}"]
            })
            print(f"\n[ERROR] 异常: {str(e)}")

    # 汇总结果
    print("\n" + "=" * 60)
    print("[SUMMARY] 测试汇总")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for r in results if r['is_valid'])

    print(f"总测试数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {total - passed}")
    print(f"通过率: {passed/total*100:.1f}%")

    if passed == total:
        print("\n[SUCCESS] 所有测试通过！标题生成功能修复成功！")
        return 0
    else:
        print("\n[WARNING] 部分测试失败，请检查日志")
        return 1


if __name__ == "__main__":
    exit_code = test_title_generation()
    sys.exit(exit_code)
