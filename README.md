# 用户需要将自己的 YouTube 发布视频的权限授予给 Google 应用

## 一、注册 Google 应用
1. 打开开发者控制台：[Google Cloud Console](https://console.cloud.google.com/projectselector2/apis/dashboard?hl=zh-cn&supportedpurview=project)

2. 进入创建项目界面，开始创建。给项目起个名字，选择无组织即可。

3. 启用 YouTube Data API v3 服务。

4. 在弹出的界面中搜索框里输入 `YouTube Data API v3`，如下：

5. 点击搜索的结果，并启用。

6. 创建 OAuth 权限请求页面。

7. 依次创建 2 个凭据，其中创建 OAuth 客户端 ID 时选择 Web 应用类型。

8. 下载上一步中创建的 API 密钥和 OAuth2 客户端配置信息 JSON 文件。

## 二、准备服务器资源
1. 由于 OAuth2 授权过程中，需要向 YouTube API 传递重定向地址，因此必须申请一个可以被海外 YouTube 顺利访问的公网域名。该公网域名也同时需要配置在上面第 7 步骤“创建 OAuth 客户端 ID”里的“已获授权的重定向 URI”部分。

2. 需要准备持久化的数据库，用来存放 OAuth2 授权后得到的 refresh_token 信息，这样后面可以通过 refresh_token 生成临时访问的 token，使用 token 可以调用发布视频接口。
