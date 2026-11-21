# GPT C2 关闭报告（写法）

执行 `GPT_C2_CLOSE_INSTRUCTION.md`。未重算 φ，未训练，未改表数字。

## 对账

见 `GPT_C2_AUDIT.md`。冻结计数仍为：

- SensorScope 0/10285（on）
- U-Air 2016/5688 = 35.4%（off）
- T-Drive 135268/285659 = 47.4%（off）
- NSW 0/18576（on）
- City Scanner XXI 0/9343（on）
- Pilot2 XXII 0/10141（on）

覆盖实现仍是 `(client_id, opportunity_stratum)` 键上的正质量和之比。因 \(\sum_{k,s}\pi=1\)，主文写成 \(I_{\mathrm{tar}}\) 上的质量和。

## 主文（`TO_OVERLEAF_paper_tmc_r1_clean/main.tex`）

- `subsec:target_measures`：\(\varpi\) 与 \(\pi^{\mathrm{tar}}_{k,s}\) 由兼容恒等式对接；定义 \(I_{\mathrm{tar}}=\{(k,s):\pi^{\mathrm{tar}}_{k,s}>0\}\)；单位查找 \(\pi^{\mathrm{tar}}(k(i),s(i))\)，缺 key = 0；\(\phi\) 数的是该查找为零，不是 \(\varpi_i=0\)。
- `eq:agg_Ct`：对 \((k,s)\in I_{\mathrm{tar}}\) 求和；\(\pi^{\mathrm{opp}}_{k,s,t}\) 为 \(F_{t-}\) 可测；Gate 仍不切换 Design。
- `eq:scd_phi` 与 Algorithm 1：同一查找；指向 Table XX 的按块构造。OFF 仍为 \(\widehat\zeta=1\)（不重开 C1）。

## 附录（`appendix.tex`）

- `app:deferred_constructions`：\(I_{\mathrm{tar}}\) 与 \(C_t\) 使用 \(\pi^{\mathrm{tar}}_{k,s}\)。
- `tab:scd_phi_freeze`：六行数字未改。Caption 改为「该块冻结 \(\pi^{\mathrm{tar}}\) 查找」。表后一句按块写 SS/UA、T-Drive、CS \(\mu_{h(i)}\)、NSW。未恢复全局 \(\pi_i=\mu_{h(i)}\)。

## 编译与自检

- `main.pdf` **14 页**；`supplemental.pdf` **13 页**。无 undefined ref。
- 稿中无 C1/C2/kill-bar。`non-inferiority` 在 `main.tex` 仍 1 处。
- 散文检查：em dash 0/3；advisory `uniform_sentence_run`、`semicolon_density`（既有信号，未为阈值改科学句）。

## 关闭条

写法关闭成立：风险、Design/覆盖、\(\phi\) 查找挂在同一套冻结 \(\varpi\) / \(\pi^{\mathrm{tar}}_{k,s}\) 上；\(I_{\mathrm{tar}}\) 与机会质量已定义；附录不把 \(\mu_{h(i)}\) 写成总公式；已发表 \(\phi\) 与 Design 开关未动。

未做：用 \(\varpi_i=0\) 重算 U-Air；统一 `build_pi_target` 重算 T-Drive/CS；C3 hybrid；公开包缺 XXI/XXII。
