# SSHClient-MCDR
MCDR的一个SSH客户端实现。

Not support English yet, translate yourself.

## 用法
!!ssh connect <地址> <用户名> <密码> <端口（可选）>

连接成功后，即可使用!!ssh "<可带空格的命令>"执行命令并获取执行结果

不用了可使用!!ssh disconnect退出ssh会话

## 当前局限
- ssh连接是全局共享的，所有人都能访问
- 未成功建立连接的ssh会话，也需要断开后才能再次建立连接
- 仅支持默认端口22，将于提交到插件仓库前修复
- 暂不支持使用密钥文件登录，只能使用密码
- 玩家在游戏内尝试连接将会公屏暴露主机连接信息和用户名密码
