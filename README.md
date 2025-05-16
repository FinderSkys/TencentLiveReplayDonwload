# TencentLiveReplayDonwload

一个用于自动下载腾讯会议直播回放的工具，支持多线程下载，可快速获取 .mp4 视频文件

## 功能特性

- 自动解析腾讯会议直播回放地址
- 多线程加速下载
- 自动命名下载文件
- 支持自定义 EdgeDriver 路径
- 支持 macOS / Windows / Linux 平台

## 使用前准备

### 1. 获取你的 Edge 浏览器版本

打开 **Edge 浏览器**，进入：

```
设置 → 关于 Microsoft Edge
```

记下你当前的浏览器版本号（如：123.0.2420.65）。

### 2. 下载对应版本的 EdgeDriver

访问以下链接下载与你 Edge 浏览器版本一致的 EdgeDriver：
👉 [https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH)

解压后将以下文件放入本项目根目录中：

- **Windows 用户**：`msedgedriver.exe`
- **macOS/Linux 用户**：`msedgedriver`

> 你也可以将驱动文件放置在其他目录。此时请编辑配置文件 config.ini，并将其中的参数 edge_driver_path 设置为驱动程序的绝对路径（建议使用绝对路径）。

## 使用方法

### 1. 克隆项目

```bash
git clone https://github.com/FinderSkys/TencentLiveReplayDonwload.git
cd TencentLiveReplayDonwload
```

### 2. 安装依赖

确保你已安装 Python（开发使用版本 3.10.9，未在其他版本上验证）：

```bash
pip install -r requirements.txt
```

### 3. 启动程序

```bash
python main.py
```

按提示输入腾讯直播回放的链接地址，例如：

```
https://meeting.tencent.com/crm/2qvZmxpgef
```

程序将自动进行解析并下载。

## 注意事项

- 程序使用 **多线程下载**，若下载过程中出现“合并校验失败”，请重新下载一次；
- 若多次尝试仍然失败，请提交 [Issue](https://github.com/FinderSkys/TencentLiveReplayDonwload/issues)。
- 请保持网络畅通，避免中断下载。

## License

本项目基于 GNU General Public License v3.0 进行授权。
详见 [LICENSE](LICENSE) 文件。
