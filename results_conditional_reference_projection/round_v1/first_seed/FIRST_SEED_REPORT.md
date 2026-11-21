# FIRST_SEED_REPORT

运行状态：S1_PASS_FIRST_SEED_COMPLETE。三种子筛选：THREE_SEED_SCREEN_NOT_EVALUATED。
分支 B：NOT_REGISTERED_NO_DEPLOYMENT_CONTRACT。一个种子不能确定全局 B*，也不能宣布 GO。

| 方法 | RMSE_mu | WorstGroup | Delta_group | Delta_cs | 部署 CPU | 部署 wall | 服务器步 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| FedAvg-Window | 0.685570 | 0.809606 | 0.109713 | 0.723467 | 36.781 | 37.678 | 100 |
| TwoStage-Hajek | 0.676373 | 0.797016 | 0.075868 | 0.422039 | 28.312 | 28.579 | 100 |
| U_matched_uniform | 0.697883 | 0.826136 | 0.220712 | 0.678877 | 27.953 | 28.191 | 100 |
| P_reference_projection | 0.677475 | 0.798515 | 0.076826 | 0.423047 | 28.094 | 28.530 | 100 |
| F_full_raven_design | 0.680691 | 0.803064 | 0.043240 | 0.444014 | 30.125 | 30.502 | 100 |

配对差是 P 减对手；相对 RMSE 是 P/对手 - 1。结构百分点是 50 乘 L1 差。

- U_matched_uniform: RMSE 相对 -0.029243033905435922, group pp 7.194321775971289, 部署 CPU 比 1.0050307434320849, wall 比 1.012026692054472。
- F_full_raven_design: RMSE 相对 -0.004724513158174237, group pp -1.6792962778377594, 部署 CPU 比 0.9325726141078838, wall 比 0.9353359052525413。
- TwoStage-Hajek: RMSE 相对 0.0016302216460448715, group pp -0.04788546068676541, 部署 CPU 比 0.9922737306843267, wall 比 0.9982627665028857。
- FedAvg-Window: RMSE 相对 -0.011807770840954745, group pp 1.6443396552329035, 部署 CPU 比 0.7638062871707731, wall 比 0.7571970586980437。
- Delivered-SpatialMean: RMSE 相对 -0.1224040110805874, group pp , 部署 CPU 比 , wall 比 。
- Delivered-CellBlockMean: RMSE 相对 -0.14786333876657654, group pp , 部署 CPU 比 , wall 比 。

F 的求解器负权重清理：2 次，最深 -4.404407170205483e-11。只接受不差于求解器容差 1e-6 的数值负值，然后截断到 0 再归一化。更差的负值会停止，不更换 F。
FedAU 与 ObsUse 没有合法的逐单元 validation 缓存，不估计它们是否被 P 超过。
