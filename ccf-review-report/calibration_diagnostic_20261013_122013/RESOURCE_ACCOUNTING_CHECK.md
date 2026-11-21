# D1 资源计量核验

状态：新设施限定验收通过；旧完整生命周期CPU仍未知。预算口径为原5 CPU小时申请内新增上限900秒；余额不构成执行许可。

## 根因与修复

旧 [run_accounted](C:/Cursor/raven.mcs/scripts/validate_conditional_bundle_b0.py:32) 的顺序是`Popen → 写PID文件 → attach`。本项目 `.venv_new/Scripts/python.exe` 是启动器，真正解释器的映像为 `C:/Users/szr/AppData/Local/Programs/Python/Python311/python.exe`。启动器可在attach之前创建解释器；事后只挂接启动器不能把已经存在的子进程补入该Job。

固定1 CPU秒的受控复现主动将旧挂接延后0.2秒：Job只含启动器PID13680，CPU为0；实际解释器PID25328自报退出前CPU1.09375秒。该复现自身位于新外层Job中，真实成本1.234375秒全部计费，未丢掉逃出内层的计算。证据：[旧竞态复现](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/D1_legacy_delayed_attach.meter.json)、[实际解释器记录](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/D1_legacy_delayed_attach.log)、[完整外层计量](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/legacy_repro.meter.json)。

这确证了旧设施存在该竞态，并能解释同样的零读数；旧采集当时没有保存完整PID树，不能追溯断言其每个启动时点。嵌套Job本身不是这里已证明的根因。微软文档说明父Job应包含其子Job资源及退出进程；本次通过实际读数验证了这条路径。[Nested Jobs](https://learn.microsoft.com/en-us/windows/win32/procthread/nested-jobs)、[Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)。

新 [windows_cpu_meter.py](C:/Cursor/raven.mcs/scripts/windows_cpu_meter.py:60) 的边界是：`CreateProcess(CREATE_SUSPENDED) → AssignProcessToJobObject → ResumeThread`。启动器的解释器及后续子进程从出生时继承根Job，不允许breakaway。完成端口记录每个PID的加入/退出；保留进程句柄直至最终退出，分别读取GetProcessTimes。根Job active=0后才读最终账，避免只等待父进程。无法打开PID、数量不符或读数不符会阻止后续计算，不把零值默认为有效。

单核Job affinity限制并发CPU；每5毫秒检查累计user+kernel及监控进程CPU，保留0.15秒终止余量，并设内核Job user-time后备限制及墙钟看门狗。该设施约束与机器信息须进入将来采集环境身份；不会自动证明旧q适用于新的运行条件。没有更改候选2秒规划限额。

## 事前容差与实测

运行前 [AUTHORIZATION.json](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/AUTHORIZATION.json) 已固定独立CPU比较容差：`0.03125 × N_PID + 0.01` 秒，覆盖两个读数的系统计时分辨率/结束边界；N=4时为0.135秒。本次所有差值均为0，没有事后调容差。CPU两读数覆盖完整进程生命周期，父进程退出前打印的自CPU仅作包含关系检查。

|检查|根Job CPU|逐PID和|差值|退出/预算行为|
|---|---:|---:|---:|---|
|正常父子进程|0.875000秒|0.875000秒|0|父子正常退出，4个PID均覆盖|
|外层总CPU预算终止|1.859375秒|1.859375秒|0|2秒预算触发，父子均124退出，4个PID保留|
|内部规划子进程预算终止|2.046875秒|2.046875秒|0|只终止规划子进程，父进程正常退出；规划段1.921875≤2秒|

第三行根Job含父进程启动、规划前后及辅助进程，所以大于单次规划段不是超出2秒规划预算。其内部子进程CPU1.890625秒，父进程规划增量0.03125秒；两者之和1.921875秒。根Job读数已包含这些子项，**不能再次相加**。这项验证使用同一`ProcessTreeBudget/wait_accounted`和spawn/GO拓扑，只有有限CPU工作及强制超时，不接真实采集、SGD或规划场景。

完整逐PID加入/退出、映像、CPU和Job归属：

- [D1_normal.meter.json](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/D1_normal.meter.json)：PID24380启动器0.015625、17996控制台0.015625、23328解释器0.328125、7520规划子进程0.515625秒。
- [D1_timeout.meter.json](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/D1_timeout.meter.json)：PID2552启动器0、12500控制台0.015625、2816解释器0.109375、5416规划子进程1.734375秒。启动器单独为0合法，整棵树非零。
- [nested_planner_timeout.meter.json](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/nested_planner_timeout.meter.json)：实际规划PID19692退出码124，父解释器19500正常退出；没有丢失已终止子进程。

正常/终止为本次设施关键路径验收；旧B0的27项未变更科学接口检查只引用既有结果，未重新运行全套。新统计实际经已修改的`run_accounted`入口执行并通过，覆盖入口接线。10个相关脚本语法检查通过。

## 互斥记账与预算

累计账取各独立外层Job CPU，加对应账务驱动自身CPU。Job内部的规划CPU、训练CPU、嵌套Job、逐PID和及竞态复现的内层账都是已包含项。驱动自身CPU已含监控CPU，因此不再加监控字段。

本轮新增实测及计费最终值见 [FINAL_BUDGET.json](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/FINAL_BUDGET.json)。下列数字由最终汇总填入：

|项目|数值|性质|
|---|---:|---|
|新增可确认CPU|11.656250秒|实测下界，含全部设施测试/子进程及离线统计|
|交互、启动/记录尾部留额|90秒|非实测，不是经证明的缺口上界|
|新增保守计费|101.656250秒 = 0.02823785 CPU小时|低于900秒授权调度额度|
|计量执行阶段墙钟之和|12.115193秒|不含读取/编辑/撰写等待，也不当作完整任务墙钟|
|旧批加本轮计费|1862.296875秒|两批互斥计费相加|
|原5小时申请余额|16137.703125秒|不是精确实耗余额或新授权|

D0及设施修好之前只运行标准库只读哈希/JSON核对和有限固定CPU测试，有进程自身CPU记录；未运行大型计算。交互文件读取、编辑、启动/记录尾部等另列90秒留额，属于非实测计费，不能写成精确CPU或经证明的实际上界。之后的数据统计均由新根Job约束。工具调用/撰写墙钟不等于上述执行阶段墙钟。

旧账继续为实测下界1520.640625秒，加240秒非实测留额，保守计费1760.640625秒。没有用新测试给旧生命周期补验通过，也没有改写原BUDGET或STOP。原5小时申请余额按“18000−1760.640625−本轮计费”计算。本轮已修好的计量设施不应在下一批再次按旧360秒准备项重复收费；原七条14720秒估计暂停，修订规划支持后成本须重测。
