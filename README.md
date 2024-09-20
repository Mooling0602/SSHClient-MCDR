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
