# 三项 stated-versus-true 文字缺陷：现状、对照事实与最小改法（X-4 / X-5 / X-7）

来源：外部 GPT 评审的 Part III III.4 + 本记录的 open-defect 表（X-4/X-5/X-7 三行）。
性质：**都是"文字与自家表格/图矛盾"，不需要新实验、不需要新数字**；每处 1–3 句。
θ 重采源（items 46–48）之后复查：三项均**不受**θ 影响，但 X-4 的对照事实因重采源而更硬（见下）。

**状态（2026-09-29）：三项全部应用完毕（X-4 = §7 item 49；X-5、X-7 = §7 item 50）。快照 `snapshots/2026-09-29-pre-x4-fix/` 与 `snapshots/2026-09-29-pre-x5x7-fix/`；改后 main 17 pp. / supplement 16 pp.、0 error / 0 undefined / 0 overfull，两处改动都保持段落物理行数不变，故记录中已有行号引用全部继续有效。**

---

## X-4 — Local-Hájek 与 FedAvg 的"重合"及其归因

**现状**（`main.tex:1851–1854`，§V 末段）：

> …On U-Air those RAVEN bars are Design-on, not the RAVEN-NoDesign rows of Table III.  **Local-Hájek coincides with FedAvg on U-Air because both restrict the active set to the Design support and the realized within-client Hájek weights are uniform** (supplemental material).

**为什么不对**（两点，互相独立）：

1. **归因错误**：FedAvg-Window 并不把活跃集限制到 Design 支持。附录 `tab:app_e3_uair` 的题注自己写着"Each row uses the active set its own definition licenses: the rows that read `π^tar` restrict the set, the others keep every delivered client"（`appendix.tex:1865–1867`）——FedAvg-Window 属于后者。这句归因其实是**修复前冻结 `fedavg_window` 缺陷的化石**（2026-08-11 那版 runner 丢掉了 `π^tar=0` 的 client，记录 §2A N1），route-A 修复后 FedAvg 已改为"保留全部已交付 client"。
2. **重合本身在 U-Air 已经不成立**：附录表里 FedAvg-Window = **1.1119**、Local-Hájek = **1.1923**（θ 重采源后；重采源前是 1.1882，也 != 1.1119）。真正重合的是 **SensorScope** 两行（7.9389 = 7.9389，`appendix.tex:1848/1851`）。

**对照事实（可引用的证据）**：附录《Local-Hájek Degeneracy Analysis》（`appendix.tex:1555–1583`）对 9,666 个有效 client-window（SensorScope 6,070 / U-Air 3,596）审计得到 **within-client 校正权重极差 = 0**，并给出归一化局部目标下的推导。也就是说：**在同一条活跃集上** Local-Hájek 退化为 FedAvg，原因是权重均匀，而不是因为 FedAvg 也限制了支持集。该审计与模型无关（θ 重采源不影响它）。

**最小改法**（替换该句，保留前两句不动）：

> Local-Hájek coincides with FedAvg-Window wherever the two keep the same active set, because the realized within-client Hájek weights are uniform on these traces (supplemental material); on U-Air the supplemental rows differ because Local-Hájek restricts the set to the target-mass support while FedAvg-Window keeps every delivered client.

（替代方案：直接删掉这句，附录的退化分析已独立成立；但保留一句可回答"为什么 SensorScope 两行数值相同"的读者疑问，故推荐改写而非删除。）

**影响面**：这是审稿人最容易"一眼对上表"的那类矛盾——他比较附录同一张表的 Local-Hájek 与 FedAvg 两行就会发现 1.1923 ≠ 1.1119，而正文说它们重合。

---

## X-5 — "除平衡对照外全部使用 20 paired seeds"

**现状**（`main.tex:1594`）：

> **All experiments except the balanced control use 20 paired seeds** (the balanced control uses five).  Those seeds capture algorithmic and EventTrace randomness, not independent cities.

**为什么不对**：有**四张表**用的是 **10 seeds**，句子漏了它们（平衡对照的 5 seeds 已除外，那部分没错）：

| 表 | 位置 | 题注 | seeds / windows |
|---|---|---|---|
| `tab:tdrive_hybrid`（T-Drive 混合排序，真实出租车 `R`） | `main.tex:1733–1744` | `main.tex:1736` | 10 seeds / 178 windows |
| `tab:traffic_four_region`（NSW-Traffic 四区域协议排序） | `appendix.tex:1914–1924` | `appendix.tex:1918` | 10 seeds / 100 windows |
| `tab:cityscanner_hybrid`（City Scanner 访问-占用排序） | `appendix.tex:2461–2469` | `appendix.tex:2465` | 10 seeds / 100 windows |
| `tab:cityscanner_p2_measured_o`（City Scanner Pilot 2 measured-`O` 排序） | `appendix.tex:2531–2540` | `appendix.tex:2535` | 10 seeds / 100 windows |

**最小改法**（替换该句；`main.tex` 不能引用附录 label——`xr` 是 supplement 读 main 的方向，故用描述性指代）：

> All experiments use 20 paired seeds except the balanced control, which uses five, and the four protocol-comparison tables that use ten (the T-Drive hybrid ranking here and the three supplemental rankings).  Those seeds capture algorithmic and EventTrace randomness, not independent cities.

**影响面**：这是"证据覆盖面"表述，方向上是**低估**自家协议表；不改正则任何按 20 seeds 去核对的审稿人都会在四张表上对不上。属于低风险、一行修好。

---

## X-7 — 附录 F 开篇说 U-Air 用 Design-off，而它下面的图用 Design-on

**现状**（`appendix.tex:1685–1688`，附录 F 开篇）：

> The sealed same-backbone protocol family below uses the **Design-off** setting on U-Air; the main-text table reports both settings on both blocks, and the sensor-scope and U-Air rows of Table III are the Design-on and Design-off settings respectively.

**为什么不对**（两点）：

1. **与它自己引入的图矛盾**：附录 F 紧跟的图 3（结构）题注写 "U-Air RAVEN-MCS **in this figure uses Design on**, not the Design-off rows of Table III"（`appendix.tex:1788–1790`）；图 4（预测风险）题注写 "U-Air RAVEN-MCS **here uses Design on**. The Design-off U-Air row (`RMSE_μ = 1.1131`) is in Table III"（`appendix.tex:1801–1803`）。正文 §V 同口径：`main.tex:1851–1853` "On U-Air those RAVEN bars are Design-on"。E3 正式树的 `raven` 臂确实是 Design-**on**（`raven_wo_design` 才是 Design-off 的消融臂）。
2. **"respectively" 那句也错**：Table III 在**两个数据集上都报两个设置**（每个数据集两行 RAVEN-Design / RAVEN-NoDesign），不是"SS 行 = Design-on、U-Air 行 = Design-off"。它想说的其实是**部署选择**：SensorScope 部署 Design-on、U-Air 部署 Design-off——这正是 §VII-G 的表述（`main.tex:2125–2128`：`RAVEN-Design and City Scanner report Design on. RAVEN-NoDesign reports Design off on U-Air and T-Drive`）。

**最小改法**（替换该段两句）：

> The sealed same-backbone family below is evaluated with Design on, on both blocks.  Table III reports both settings on both blocks; the deployed setting is Design on for SensorScope and Design off for U-Air.

**影响面**：附录开篇与它自己下面的两张图直接冲突，是三项里**最容易被逐页阅读的审稿人抓到**的一处；同时它也是唯一一处会在"到底哪个设置进了图"上误导读者（图用的是 Design-on 臂，部署的是 Design-off）。

---

## 三项汇总

| 项 | 位置 | 病根 | 最小改法 | 需重编译 | 新增计算 |
|---|---|---|---|---|---|
| X-4 | `main.tex:1851–1854` | 归因化石 + U-Air 已不重合 | 改写 1 句 | 是 | 无 |
| X-5 | `main.tex:1594` | 漏列 4 张 10-seed 协议表 | 改写 1 句 | 是 | 无 |
| X-7 | `appendix.tex:1685–1688` | 与自家图题注/§V/§VII-G 冲突 | 改写 2 句 | 是 | 无 |

三项合计 4 句正文，改完 main 仍应为 **17 pp.**、supplement **16 pp.**（X-7 的两句净减 1 行，X-5 增约 1 行，X-4 增约 2 行；页数不变的风险很小，但仍需重编译核对 17/16 与 0 error/0 undefined/0 overfull）。
