# P0 补做

实际使用的 PowerShell 命令：

```powershell
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:OPENBLAS_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
& "C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe" "C:\Cursor\raven.mcs\results_targeted_reference_calibration\p0_same_value_screen_20261022_210125\prepare_data.py"
```

Python 是 `C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe`。没有升级这个环境，也没有新建包装依赖。内存用 Windows 工作集接口计量。

EPA 日文件和补充 PDF、数据字典只从 `source_cache_20261022` 读取。主表从原始数据包读取。没有重新下载。
