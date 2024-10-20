用户需要将自己的youtube发布视频的权限授予给Google应用，Google应用才可以根据用户授权信息里的token来发布视频。

## 一、注册 Google 应用
1. 打开开发者控制台：[Google Cloud Console](https://console.cloud.google.com/projectselector2/apis/dashboard?hl=zh-cn&supportedpurview=project)
2. 进入创建项目界面，开始创建。给项目起个名字，选择无组织即可。
3. 启用 YouTube Data API v3 服务。
4. 在弹出的界面中搜索框里输入 `YouTube Data API v3`。
5. 点击搜索的结果，并启用。
6. 创建 OAuth 权限请求页面。
7. 依次创建 2 个凭据，其中创建 OAuth 客户端 ID 时选择 Web 应用类型。
8. 下载上一步中创建的 API 密钥和 OAuth2 客户端配置信息 JSON 文件。

## 二、准备服务器资源
1. 由于 OAuth2 授权过程中，需要向 YouTube API 传递重定向地址，因此必须申请一个可以被海外 YouTube 顺利访问的公网域名。该公网域名也同时需要配置在上面第 7 步骤“创建 OAuth 客户端 ID”里的“已获授权的重定向 URI”部分。
2. 需要准备持久化的数据库，用来存放 OAuth2 授权后得到的 refresh_token 信息，这样后面可以通过 refresh_token 生成临时访问的 token，使用 token 可以调用发布视频接口。

## 三、代码说明
1. 代码采用 Python 编写，版本 3.10，需要安装如下依赖：
   - google-api-python-client
   - google-auth-oauthlib
   - google-auth-httplib2
   - flask
   - httplib
2. OAuth 代码说明：
   假设 OAuth 服务代码部署在公网域名 `yumenzhisi.com` 下，那么可以在浏览器里直接输入 `https://yumenzhisi.com/` 访问，会默认调用上面 `index` 方法，然后会被立即重定向到 `authorize` 方法，这个方法里会告诉 YouTube 重定向的 URI 是什么，接下来就是前端页面的 Google 账号授权操作，一步步点下去之后，最终 YouTube API 服务端会调用前面传递的重定向 URI，上面的代码中重定向 URI 为 `/oauth2callback`，也就是上面的 `oauth2callback` 方法，在该方法里会拿到 `refresh_token` 等信息，这个信息要持久化存储起来。
3. Publish 代码说明：
   代码中 `credentials.txt` 里存放的是前面步骤中授权得到的用户 `refresh_token` 的信息（其实可以存到 MySQL 等数据库中，这里只是为了模拟流程方便而存文件中）。`options` 是待发布的视频的一些信息，`file` 为视频文件的路径，`title` 为视频标题，`description` 是视频的描述信息，`category` 为视频的类别，22 表示 People & Blogs，`keywords` 表示关键字，`privacyStatus` 表示是公开还是私有。
