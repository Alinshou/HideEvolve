# W01 仓库与数据来源审计

审计日期：2026-10-09。审计方式：读取旧仓库版本、阶段收束文件、主要源文件、数据来源清单；没有重跑旧实验。日程依据：HideEvolve_V5.pdf 第 3 页 10/12 条目。

## 版本和源码边界

- 新项目：`C:/Users/21882/VS.project/HideEvolve`，报告前 HEAD `7c9e1a0`。
- 旧项目：`C:/Users/21882/VS.project/Foundation Model Agent`，HEAD `5093a8f0aed925f8e06c92591fdb1aa9a626fabb`。用户的设置变更及未跟踪材料没有被该 SHA 覆盖，本次未修改旧项目。
- ShinkaEvolve：`8adc053a2ce4511ad2ac310e004c530a73fb974a`，Apache-2.0，核心工作树无本地修改。
- ReEvo：`6dce18257da5e11db2d138e417a2fffc5c72d05f`，MIT；只做源代码审计，水印任务未适配。

## Stage 1-8 与 PoC

阶段状态依据旧仓库 `docs/POC_FEASIBILITY_CLOSURE_FINAL_20261008_ZH.md`，不重新宣称全部历史证据已经复核。

| 阶段 | 既有状态 | 可复用范围 |
|---|---|---|
| 1-3 | DCT/QIM、JPEG、指标、数据与记录链已有实现 | 数据身份、指标、失败记账需经新任务契约测试后复用 |
| 4-5 | Fixed/Random/TPE/NSGA-II 探索执行完成，保留未满预算结果 | 工程与对照设计参考，不能替代新研究的同行程序演化基线 |
| 6 | 三条 Agent 轨迹各32次真实评价 | 旧闭环工程证据；尚未证明方法优势 |
| 7 | 真实64×1000开发矩阵、精度与资源分析完成 | 成本与功效规划；不作为新论文盲测结果 |
| 8 | V0.2设计及离线分析器/规划器保留，runner和后续完整试验暂缓 | 已完成与暂缓部分继续分别标注 |

已定位源码：`evaluation.py`、`metrics.py`、`data.py`、`coco.py`、`payload.py`、`attacks.py`、`candidate_runner.py`、`deepseek_agent.py`、`watermark/dct_qim.py`、`stage8_inference.py`、`stage8_planner.py`、`stage8_simulation.py`，均位于旧仓库 `src/hideevolve/`。

抽查发现旧 JPEG 攻击固定编码参数；DCT/QIM 处理二维亮度图。旧接口并非新协议的完整 RGB 程序对。W02 应先建立盲提取、消息/密钥隔离与失败记账测试，再移植可复用内容。新项目尚无水印方法优势证据。

## 数据来源

既有来源：COCO 2017 validation，官方主页 https://cocodataset.org/。旧仓库 `data/SOURCES.yaml`、`data/README.md` 和 `data/manifests/` 记录来源、图片身份与授权信息。本次未重新下载完整数据。

- val2017.zip 既有 SHA-256：`4f7e2ccb2866ec5041993c9cf2a952bbed69647b115d0f74da7ce8f4bef82f05`。
- annotations_trainval2017.zip 既有 SHA-256：`113a836d90195ee1f884e704da6304dfaaecff1f023f49b6ca93c4aaae470268`。
- 原始图片保留各自授权，不能将 COCO 描述为所有图片可无条件再分发。
- 旧1000张已用开发图像及新开发图像须从新盲测池排除。三类新数据清单在 W02 冻结，W01未使用 COCO 进行水印比较。

设备：`hardware.yaml`；实际实验环境：`env-lock.md`、`requirements-lock.txt`；主仓库 SHA 是已安装的上游源码版本，不把安装副本路径当作版本号。
