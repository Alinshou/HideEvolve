# W01 ReEvo 接入风险表

日期：2026-10-09。官方仓库：https://github.com/ai4co/reevo；SHA `6dce18257da5e11db2d138e417a2fffc5c72d05f`；许可证 MIT。

已核查 README、main.py 和 reevo.py；README 明确支持 DeepSeek deepseek-chat。当前仅源码级审计，未安装验收或运行水印任务。

| 风险 | 依据 | 等级 | 接入检查 |
|---|---|---|---|
| 问题接口 | cfg/problem、problems、prompts 三类任务文件；现有任务以组合优化为主 | 高 | 用完整 embed/decode 程序和统一 evaluator；不以旧调参接口替代 |
| 共享代码文件 | 候选写入 problems/<problem>/gpt.py，eval.py导入 | 中高 | 检查并行覆盖，逐候选封存 |
| 分值与失败 | 评价器stdout末行被解析，内部按最小化比较 | 中 | 可行性优先，明确失败分值与方向 |
| Windows/Python | 子进程调用字符串python | 中 | 用对应环境启动，核实实际解释器与超时 |
| 多模型调用成本 | 生成、短/长反思、交叉、变异可有不同客户端 | 高 | 统一模型口径，所有调用/失败计入预算 |
| 盲提取与泄露 | 原版无本任务的图像/消息/真值隔离契约 | 高 | 接入W02契约，decode只见攻击图像、固定协议与密钥 |

入口：`main.py` 创建 `ReEvo`，`reevo.py` 从任务提示载入 seed function、签名、描述，将候选写入 gpt.py 并启动任务 eval.py。原版搜索机制应保留。

投入上限：正式适配最多两个工作日，W10前决定是否纳入。若依赖、接口、评价协议或成本公平无法满足，则记录未完成原因，保持条件性基线；不阻塞 Shinka 主线，不自行重写一个近似算法冒充原版。
